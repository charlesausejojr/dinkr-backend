import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.config import settings
from app.dependencies import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("dinkr")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.secret_key,
        algorithm=settings.algorithm
    )


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        logger.warning("Register failed — email already exists: %s", payload.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("New user registered: %s (id=%s)", user.email, user.id)
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning("Login failed for: %s", payload.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info("Login: %s", user.email)
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Clerk OAuth exchange ───────────────────────────────────────────────────────
class ClerkTokenPayload(BaseModel):
    token: str


CLERK_JWKS_URL = "https://fond-lion-33.clerk.accounts.dev/.well-known/jwks.json"
CLERK_API_URL = "https://api.clerk.com/v1"


async def _verify_clerk_token(token: str) -> str:
    """Verify a Clerk session JWT and return the Clerk user ID (sub)."""
    async with httpx.AsyncClient() as client:
        jwks_res = await client.get(CLERK_JWKS_URL)
        jwks_res.raise_for_status()
        jwks = jwks_res.json()

    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid Clerk token") from exc

    kid = header.get("kid")
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Clerk signing key not found")

    try:
        payload = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Clerk token expired") from exc
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Clerk token verification failed") from exc

    user_id: str = payload.get("sub", "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Clerk token missing subject")
    return user_id


async def _get_clerk_user(clerk_user_id: str) -> dict:
    """Fetch user details from Clerk's management API."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{CLERK_API_URL}/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
        )
        if res.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to fetch Clerk user")
        return res.json()


@router.post("/clerk", response_model=Token)
async def clerk_oauth(payload: ClerkTokenPayload, db: AsyncSession = Depends(get_db)):
    """Exchange a Clerk session JWT for a Dinkr backend JWT."""
    clerk_user_id = await _verify_clerk_token(payload.token)
    clerk_user = await _get_clerk_user(clerk_user_id)

    # Extract email and name from Clerk user object
    email_addresses = clerk_user.get("email_addresses", [])
    if not email_addresses:
        raise HTTPException(status_code=400, detail="No email associated with this Google account")
    email = email_addresses[0]["email_address"]

    first = clerk_user.get("first_name") or ""
    last = clerk_user.get("last_name") or ""
    full_name = f"{first} {last}".strip() or email.split("@")[0]

    # Find or create user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = User(email=email, hashed_password=None, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("New OAuth user created via Clerk: %s (id=%s)", email, user.id)
    else:
        logger.info("OAuth login for existing user: %s (id=%s)", email, user.id)

    return Token(access_token=create_access_token(user.id))
