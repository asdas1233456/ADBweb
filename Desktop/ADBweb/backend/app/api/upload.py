"""
文件上传API路由
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.file_handler import FileHandler
from app.schemas.common import Response
import logging

router = APIRouter(prefix="/upload", tags=["文件上传"])
logger = logging.getLogger(__name__)


@router.post("/script", response_model=Response[dict])
async def upload_script(
    file: UploadFile = File(...),
    script_type: str = Form(...)
):
    """上传脚本文件"""
    try:
        # 验证脚本类型
        if script_type not in ["python", "batch"]:
            raise HTTPException(status_code=400, detail="不支持的脚本类型")
        
        # 保存文件
        result = await FileHandler.save_script_file(file, script_type)
        
        return Response(message="文件上传成功", data=result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")


@router.post("/screenshot", response_model=Response[dict])
async def upload_screenshot(
    file: UploadFile = File(...),
    task_log_id: int = Form(...)
):
    """上传截图文件"""
    try:
        # 保存文件
        result = await FileHandler.save_screenshot(file, task_log_id)
        
        return Response(message="截图上传成功", data=result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"截图上传失败: {e}")
        raise HTTPException(status_code=500, detail="截图上传失败")
