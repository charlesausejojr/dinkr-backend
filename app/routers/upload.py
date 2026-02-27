import logging
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings

router = APIRouter()
logger = logging.getLogger("dinkr")

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

PHOTO_MIN_BYTES  = 100 * 1024        #  100 KB
PHOTO_MAX_BYTES  = 5  * 1024 * 1024  #    5 MB
AVATAR_MIN_BYTES = 30  * 1024        #   30 KB
AVATAR_MAX_BYTES = 3  * 1024 * 1024  #    3 MB


def _validate(contents: bytes, content_type: str, min_bytes: int, max_bytes: int, label: str) -> None:
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, and GIF images are accepted.")

    size = len(contents)
    if size < min_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"{label} is too small ({size // 1024} KB). Minimum is {min_bytes // 1024} KB."
        )
    if size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"{label} is too large ({size / (1024*1024):.1f} MB). Maximum is {max_bytes // (1024*1024)} MB."
        )


def _upload(contents: bytes, folder: str) -> str:
    result = cloudinary.uploader.upload(
        contents,
        folder=f"dinkr/{folder}",
        resource_type="image",
    )
    return result["secure_url"]


@router.post("/photo")
async def upload_photo(file: UploadFile = File(...)):
    """Establishment and court photos. Min 100 KB · Max 5 MB."""
    contents = await file.read()
    _validate(contents, file.content_type or "", PHOTO_MIN_BYTES, PHOTO_MAX_BYTES, "Photo")
    url = _upload(contents, "photos")
    logger.info("Photo uploaded → %s", url)
    return {"url": url}


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """Coach profile avatars. Min 30 KB · Max 3 MB."""
    contents = await file.read()
    _validate(contents, file.content_type or "", AVATAR_MIN_BYTES, AVATAR_MAX_BYTES, "Avatar")
    url = _upload(contents, "avatars")
    logger.info("Avatar uploaded → %s", url)
    return {"url": url}
