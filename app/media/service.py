"""
Media service - handles image upload, conversion to WebP, optimization
"""
import uuid
import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

# Try to import Pillow, gracefully handle if not installed
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not installed. Image optimization disabled. Install with: pip install Pillow")

# Configuration
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_WIDTH = 1920
WEBP_QUALITY = 85
THUMBNAIL_SIZE = (400, 400)
THUMBNAIL_QUALITY = 80


async def upload_image(
    file: UploadFile,
    category: str = "blog"
) -> dict:
    """
    Upload image, convert to WebP, create thumbnail

    Args:
        file: Uploaded file
        category: Category folder (blog, icons, etc.)

    Returns:
        dict with original, optimized, and thumbnail URLs

    Raises:
        ValueError: If file type not allowed or file too large
    """
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError(f"File type not allowed. Allowed: {', '.join(ALLOWED_TYPES)}")

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    # Generate unique filename
    file_id = uuid.uuid4().hex[:12]
    original_ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"

    # Create directories
    originals_dir = UPLOAD_DIR / category / "originals"
    optimized_dir = UPLOAD_DIR / category / "optimized"
    originals_dir.mkdir(parents=True, exist_ok=True)
    optimized_dir.mkdir(parents=True, exist_ok=True)

    # Save original
    original_path = originals_dir / f"{file_id}{original_ext}"
    with open(original_path, "wb") as f:
        f.write(content)

    # If Pillow not available, return original only
    if not PILLOW_AVAILABLE:
        return {
            "id": file_id,
            "original": f"/uploads/{category}/originals/{file_id}{original_ext}",
            "optimized": f"/uploads/{category}/originals/{file_id}{original_ext}",
            "thumbnail": f"/uploads/{category}/originals/{file_id}{original_ext}"
        }

    # Convert and optimize with Pillow
    optimized_path = optimized_dir / f"{file_id}.webp"
    thumbnail_path = optimized_dir / f"{file_id}_thumb.webp"

    with Image.open(original_path) as img:
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize if too large
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

        # Save optimized WebP
        img.save(optimized_path, "WEBP", quality=WEBP_QUALITY, optimize=True)

        # Create thumbnail
        img_thumb = img.copy()
        img_thumb.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        img_thumb.save(thumbnail_path, "WEBP", quality=THUMBNAIL_QUALITY)

    return {
        "id": file_id,
        "original": f"/uploads/{category}/originals/{file_id}{original_ext}",
        "optimized": f"/uploads/{category}/optimized/{file_id}.webp",
        "thumbnail": f"/uploads/{category}/optimized/{file_id}_thumb.webp"
    }


def delete_image(file_id: str, category: str = "blog") -> bool:
    """
    Delete image and all its variants

    Args:
        file_id: Image ID (without extension)
        category: Category folder

    Returns:
        True if deleted, False if not found
    """
    deleted = False
    originals_dir = UPLOAD_DIR / category / "originals"
    optimized_dir = UPLOAD_DIR / category / "optimized"

    # Delete originals (any extension)
    for f in originals_dir.glob(f"{file_id}.*"):
        f.unlink()
        deleted = True

    # Delete optimized versions
    for f in optimized_dir.glob(f"{file_id}*"):
        f.unlink()
        deleted = True

    return deleted


def get_image_url(
    file_id: str,
    category: str = "blog",
    variant: str = "optimized"
) -> Optional[str]:
    """
    Get URL for an image

    Args:
        file_id: Image ID
        category: Category folder
        variant: 'original', 'optimized', or 'thumbnail'

    Returns:
        URL string or None if not found
    """
    if variant == "original":
        originals_dir = UPLOAD_DIR / category / "originals"
        for f in originals_dir.glob(f"{file_id}.*"):
            return f"/uploads/{category}/originals/{f.name}"
    elif variant == "thumbnail":
        path = UPLOAD_DIR / category / "optimized" / f"{file_id}_thumb.webp"
        if path.exists():
            return f"/uploads/{category}/optimized/{file_id}_thumb.webp"
    else:  # optimized
        path = UPLOAD_DIR / category / "optimized" / f"{file_id}.webp"
        if path.exists():
            return f"/uploads/{category}/optimized/{file_id}.webp"

    return None
