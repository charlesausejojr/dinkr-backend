import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()
logger = logging.getLogger("dinkr")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}

# Guardrails
PHOTO_MIN_BYTES  = 100 * 1024        #  100 KB — ensures real photo quality
PHOTO_MAX_BYTES  = 5  * 1024 * 1024  #    5 MB — prevents massive uploads
AVATAR_MIN_BYTES = 30  * 1024        #   30 KB — avatars can be smaller
AVATAR_MAX_BYTES = 3  * 1024 * 1024  #    3 MB


def _validate_and_save(
    contents: bytes,
    filename: str,
    content_type: str,
    min_bytes: int,
    max_bytes: int,
    label: str,
) -> str:
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, WebP, and GIF images are accepted."
        )

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension.")

    size = len(contents)
    if size < min_bytes:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{label} is too small ({size // 1024} KB). "
                f"Please upload a higher-quality image (minimum {min_bytes // 1024} KB)."
            )
        )
    if size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{label} is too large ({size / (1024 * 1024):.1f} MB). "
                f"Maximum allowed size is {max_bytes // (1024 * 1024)} MB."
            )
        )

    unique_name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    with open(path, "wb") as f:
        f.write(contents)

    logger.info("File uploaded: %s (%d KB)", unique_name, size // 1024)
    return f"/uploads/{unique_name}"


@router.post("/photo")
async def upload_photo(file: UploadFile = File(...)):
    """
    For establishment and court photos.
    Min: 100 KB | Max: 5 MB | Types: JPEG, PNG, WebP, GIF
    """
    contents = await file.read()
    url = _validate_and_save(
        contents,
        file.filename or "upload",
        file.content_type or "",
        PHOTO_MIN_BYTES,
        PHOTO_MAX_BYTES,
        "Photo",
    )
    return {"url": url}


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """
    For coach profile avatars.
    Min: 30 KB | Max: 3 MB | Types: JPEG, PNG, WebP, GIF
    """
    contents = await file.read()
    url = _validate_and_save(
        contents,
        file.filename or "avatar",
        file.content_type or "",
        AVATAR_MIN_BYTES,
        AVATAR_MAX_BYTES,
        "Avatar",
    )
    return {"url": url}
