"""파일 업로드 유틸리티."""

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

from app.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


async def validate_image(file: UploadFile) -> bytes:
    """이미지 파일 검증. 검증 통과 시 파일 내용(bytes) 반환."""
    if not file.filename:
        raise HTTPException(status_code=422, detail="파일명이 없습니다.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=422,
            detail=f"파일 크기가 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB를 초과합니다.",
        )

    # Content-Type 검증
    allowed_content_types = {"image/jpeg", "image/png"}
    if file.content_type not in allowed_content_types:
        raise HTTPException(status_code=422, detail="지원하지 않는 Content-Type입니다.")

    return content


async def save_image(content: bytes, category: str, store_id: int, original_filename: str) -> str:
    """이미지를 디스크에 저장하고 상대 경로 반환."""
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    relative_dir = f"{category}/{store_id}"
    full_dir = os.path.join(settings.UPLOAD_DIR, relative_dir)

    os.makedirs(full_dir, exist_ok=True)

    file_path = os.path.join(full_dir, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"{relative_dir}/{unique_name}"


async def delete_image(image_path: str) -> None:
    """이미지 파일 삭제 (idempotent)."""
    full_path = os.path.join(settings.UPLOAD_DIR, image_path)
    if os.path.exists(full_path):
        os.remove(full_path)
