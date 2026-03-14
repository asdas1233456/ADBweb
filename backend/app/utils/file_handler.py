"""
文件处理工具
"""
import os
import re
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile
from app.core.config import settings
import logging
from app.utils.time_utils import now_local

logger = logging.getLogger(__name__)


class FileHandler:
    """文件处理类"""

    @staticmethod
    def ensure_upload_dir():
        """确保上传目录存在"""
        dirs = [
            settings.UPLOAD_DIR,
            os.path.join(settings.UPLOAD_DIR, "scripts"),
            os.path.join(settings.UPLOAD_DIR, "screenshots"),
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    @staticmethod
    def _get_upload_size(file: UploadFile) -> int:
        """获取上传文件大小"""
        try:
            file.file.seek(0, os.SEEK_END)
            size = file.file.tell()
            file.file.seek(0)
            return size
        except Exception:
            return 0

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名，防止路径穿越和非法字符"""
        name = os.path.basename(filename or "")
        name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
        return name or "upload"

    @staticmethod
    def _validate_extension(filename: str, allowed_exts: set) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_exts:
            raise ValueError(f"不支持的文件类型: {ext}")
        return ext

    @staticmethod
    async def save_script_file(file: UploadFile, script_type: str) -> dict:
        """保存脚本文件"""
        try:
            FileHandler.ensure_upload_dir()

            allowed_script_exts = {e.strip().lower() for e in settings.ALLOWED_SCRIPT_EXTS.split(",") if e.strip()}
            filename = FileHandler._sanitize_filename(file.filename)

            if script_type == "python" and not filename.lower().endswith(".py"):
                raise ValueError("只能上传 .py 文件")
            if script_type == "batch" and not filename.lower().endswith(".bat"):
                raise ValueError("只能上传 .bat 文件")

            ext = FileHandler._validate_extension(filename, allowed_script_exts)

            size = FileHandler._get_upload_size(file)
            if size > settings.MAX_FILE_SIZE:
                raise ValueError("文件过大，超过限制")

            timestamp = now_local().strftime("%Y%m%d_%H%M%S")
            unique = uuid.uuid4().hex[:8]
            stored_name = f"{timestamp}_{unique}{ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, "scripts", stored_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                file_content = f.read()

            logger.info(f"脚本文件已保存: {file_path}")

            return {
                "file_path": file_path,
                "file_name": stored_name,
                "file_size": size,
                "file_content": file_content
            }

        except Exception as e:
            logger.error(f"保存脚本文件失败: {e}")
            raise

    @staticmethod
    async def save_screenshot(file: UploadFile, task_log_id: int) -> dict:
        """保存截图文件"""
        try:
            FileHandler.ensure_upload_dir()

            allowed_image_exts = {e.strip().lower() for e in settings.ALLOWED_IMAGE_EXTS.split(",") if e.strip()}
            filename = FileHandler._sanitize_filename(file.filename)
            ext = FileHandler._validate_extension(filename, allowed_image_exts)

            size = FileHandler._get_upload_size(file)
            if size > settings.MAX_FILE_SIZE:
                raise ValueError("文件过大，超过限制")

            timestamp = now_local().strftime("%Y%m%d_%H%M%S")
            unique = uuid.uuid4().hex[:8]
            stored_name = f"task_{task_log_id}_{timestamp}_{unique}{ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, "screenshots", stored_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"截图文件已保存: {file_path}")

            return {
                "file_path": file_path,
                "file_name": stored_name,
                "file_size": size
            }

        except Exception as e:
            logger.error(f"保存截图文件失败: {e}")
            raise
