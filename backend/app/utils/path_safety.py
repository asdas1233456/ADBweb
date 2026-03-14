"""
路径安全校验工具
"""
from pathlib import Path

from app.core.config import settings


def resolve_upload_path(path_str: str) -> Path:
    """
    将路径解析为上传目录内的安全路径
    """
    base = Path(settings.UPLOAD_DIR).resolve()
    target = Path(path_str)
    if not target.is_absolute():
        # 兼容传入包含 uploads/ 前缀的相对路径
        base_name = Path(settings.UPLOAD_DIR).name
        parts = target.parts
        if parts and parts[0].lower() == base_name.lower():
            target = Path(*parts[1:])
        target = (base / target).resolve()
    else:
        target = target.resolve()

    if base != target and base not in target.parents:
        raise ValueError("路径不在允许的上传目录内")

    return target
