import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, establishments, courts, coaches, bookings, coach_bookings, availability
from app.routers import upload

# ── Logging setup ─────────────────────────────────────────────────────────────
logger = logging.getLogger("dinkr")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

app = FastAPI(title="Dinkr API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    status = response.status_code
    level = logging.WARNING if status >= 400 else logging.INFO
    logger.log(
        level,
        "%s %s  →  %d  (%.1f ms)",
        request.method,
        request.url.path,
        status,
        ms,
    )
    return response

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(establishments.router, prefix="/establishments", tags=["Establishments"])
app.include_router(courts.router, prefix="/courts", tags=["Courts"])
app.include_router(coaches.router, prefix="/coaches", tags=["Coaches"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(coach_bookings.router, prefix="/coach-bookings", tags=["Coach Bookings"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])


@app.get("/health")
async def health():
    return {"status": "ok"}
