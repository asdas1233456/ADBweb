"""
文件处理工具
"""
import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from app.core.config import settings
import logging

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
    async def save_script_file(file: UploadFile, script_type: str) -> dict:
        """保存脚本文件"""
        try:
            # 验证文件类型
            if script_type == "python" and not file.filename.endswith(".py"):
                raise ValueError("只能上传 .py 文件")
            if script_type == "batch" and not file.filename.endswith(".bat"):
                raise ValueError("只能上传 .bat 文件")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(settings.UPLOAD_DIR, "scripts", filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            logger.info(f"脚本文件已保存: {file_path}")
            
            return {
                "file_path": file_path,
                "file_name": file.filename,
                "file_size": os.path.getsize(file_path),
                "file_content": file_content
            }
            
        except Exception as e:
            logger.error(f"保存脚本文件失败: {e}")
            raise
    
    @staticmethod
    async def save_screenshot(file: UploadFile, task_log_id: int) -> dict:
        """保存截图文件"""
        try:
            # 验证文件类型
            if not (file.filename.endswith(".png") or file.filename.endswith(".jpg")):
                raise ValueError("只能上传 .png 或 .jpg 文件")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(file.filename)[1]
            filename = f"task_{task_log_id}_{timestamp}{ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, "screenshots", filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"截图文件已保存: {file_path}")
            
            return {
                "file_path": file_path,
                "file_name": filename,
                "file_size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            logger.error(f"保存截图文件失败: {e}")
            raise
