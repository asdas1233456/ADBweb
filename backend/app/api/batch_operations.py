"""
批量设备操作API路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.common import Response
from app.services.batch_device_service import BatchDeviceService
from pydantic import BaseModel
from typing import List
import logging
import os

router = APIRouter(prefix="/batch-operations", tags=["批量操作"])
logger = logging.getLogger(__name__)


class BatchInstallRequest(BaseModel):
    """批量安装请求"""
    device_ids: List[int]
    apk_path: str


class BatchUninstallRequest(BaseModel):
    """批量卸载请求"""
    device_ids: List[int]
    package_name: str


class BatchPushFileRequest(BaseModel):
    """批量推送文件请求"""
    device_ids: List[int]
    local_path: str
    remote_path: str


class BatchCommandRequest(BaseModel):
    """批量执行命令请求"""
    device_ids: List[int]
    command: str


class BatchClearCacheRequest(BaseModel):
    """批量清除缓存请求"""
    device_ids: List[int]
    package_name: str


@router.post("/install-app", response_model=Response[dict])
async def batch_install_app(
    request: BatchInstallRequest,
    db: Session = Depends(get_session)
):
    """
    批量安装应用
    
    Args:
        request: 批量安装请求
        
    Returns:
        操作结果
    """
    try:
        service = BatchDeviceService(db)
        result = await service.batch_install_app(request.device_ids, request.apk_path)
        
        return Response(
            message=f"批量安装完成: 成功 {result['success']}/{result['total']}",
            data=result
        )
    except Exception as e:
        logger.error(f"批量安装应用失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/uninstall-app", response_model=Response[dict])
async def batch_uninstall_app(
    request: BatchUninstallRequest,
    db: Session = Depends(get_session)
):
    """
    批量卸载应用
    
    Args:
        request: 批量卸载请求
        
    Returns:
        操作结果
    """
    try:
        service = BatchDeviceService(db)
        result = await service.batch_uninstall_app(request.device_ids, request.package_name)
        
        return Response(
            message=f"批量卸载完成: 成功 {result['success']}/{result['total']}",
            data=result
        )
    except Exception as e:
        logger.error(f"批量卸载应用失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push-file", response_model=Response[dict])
async def batch_push_file(
    request: BatchPushFileRequest,
    db: Session = Depends(get_session)
):
    """
    批量推送文件
    
    Args:
        request: 批量推送文件请求
        
    Returns:
        操作结果
    """
    try:
        service = BatchDeviceService(db)
        result = await service.batch_push_file(
            request.device_ids, 
            request.local_path, 
            request.remote_path
        )
        
        return Response(
            message=f"批量推送文件完成: 成功 {result['success']}/{result['total']}",
            data=result
        )
    except Exception as e:
        logger.error(f"批量推送文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-command", response_model=Response[dict])
async def batch_execute_command(
    request: BatchCommandRequest,
    db: Session = Depends(get_session)
):
    """
    批量执行Shell命令
    
    Args:
        request: 批量执行命令请求
        
    Returns:
        操作结果
    """
    try:
        service = BatchDeviceService(db)
        result = await service.batch_execute_command(request.device_ids, request.command)
        
        return Response(
            message=f"批量执行命令完成: 成功 {result['success']}/{result['total']}",
            data=result
        )
    except Exception as e:
        logger.error(f"批量执行命令失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reboot", response_model=Response[dict])
async def batch_reboot(
    device_ids: List[int],
    db: Session = Depends(get_session)
):
    """
    批量重启设备
    
    Args:
        device_ids: 设备ID列表
        
    Returns:
        操作结果
    """
    try:
        service = BatchDeviceService(db)
        result = await service.batch_reboot(device_ids)
        
        return Response(
            message=f"批量重启完成: 成功 {result['success']}/{result['total']}",
            data=result
        )
    except Exception as e:
        logger.error(f"批量重启设备失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache", response_model=Response[dict])
async def batch_clear_cache(
    request: BatchClearCacheRequest,
    db: Session = Depends(get_session)
):
    """
    批量清除应用缓存
    
    Args:
        request: 批量清除缓存请求
        
    Returns:
        操作结果
    """
    try:
        service = BatchDeviceService(db)
        result = await service.batch_clear_cache(request.device_ids, request.package_name)
        
        return Response(
            message=f"批量清除缓存完成: 成功 {result['success']}/{result['total']}",
            data=result
        )
    except Exception as e:
        logger.error(f"批量清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-apk")
async def upload_apk(file: UploadFile = File(...)):
    """
    上传APK文件
    
    Args:
        file: APK文件
        
    Returns:
        文件路径
    """
    try:
        # 创建上传目录
        upload_dir = "uploads/apks"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"APK文件上传成功: {file_path}")
        
        return Response(
            message="APK文件上传成功",
            data={"file_path": file_path, "filename": file.filename}
        )
    except Exception as e:
        logger.error(f"APK文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
