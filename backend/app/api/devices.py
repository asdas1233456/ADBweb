"""
设备管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Device, ActivityLog
from app.schemas.common import Response, PageResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

router = APIRouter(prefix="/devices", tags=["设备管理"])
logger = logging.getLogger(__name__)


@router.get("", response_model=Response[PageResponse[Device]])
async def get_devices(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_session)
):
    """获取设备列表"""
    query = select(Device)
    
    if status:
        query = query.where(Device.status == status)
    
    # 优化：先计算总数（使用count查询）
    count_query = select(func.count(Device.id))
    if status:
        count_query = count_query.where(Device.status == status)
    total = db.exec(count_query).one()
    
    # 分页查询，按更新时间倒序
    offset = (page - 1) * page_size
    query = query.order_by(Device.updated_at.desc()).offset(offset).limit(page_size)
    devices = db.exec(query).all()
    
    page_data = PageResponse(
        items=devices,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
    
    # 返回带 items 的结构以保持一致性
    return Response(data=page_data.model_dump())


@router.get("/{device_id}", response_model=Response[Device])
async def get_device(device_id: int, db: Session = Depends(get_session)):
    """获取设备详情"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return Response(data=device)


@router.post("/refresh", response_model=Response[dict])
async def refresh_devices(db: Session = Depends(get_session)):
    """刷新设备列表 - 扫描ADB设备并自动添加到系统"""
    try:
        from app.services.adb_device_scanner import scan_and_add_devices
        
        # 扫描并添加设备
        result = scan_and_add_devices(db)
        
        # 记录活动日志
        activity = ActivityLog(
            activity_type="device_refresh",
            description=f"刷新设备列表: 新增 {result['new_devices']} 台, 更新 {result['updated_devices']} 台",
            status="success"
        )
        db.add(activity)
        db.commit()
        
        logger.info(f"设备列表刷新成功: {result}")
        
        return Response(
            message=f"设备列表已刷新: 新增 {result['new_devices']} 台, 更新 {result['updated_devices']} 台",
            data=result
        )
    except Exception as e:
        logger.error(f"刷新设备列表失败: {e}")
        
        # 记录失败日志
        activity = ActivityLog(
            activity_type="device_refresh",
            description=f"刷新设备列表失败: {str(e)}",
            status="failed"
        )
        db.add(activity)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"刷新设备列表失败: {str(e)}")


@router.post("/scan", response_model=Response[dict])
async def scan_devices(db: Session = Depends(get_session)):
    """扫描设备（别名接口）- 与refresh功能相同"""
    try:
        from app.services.adb_device_scanner import scan_and_add_devices
        
        # 扫描并添加设备
        result = scan_and_add_devices(db)
        
        # 记录活动日志
        activity = ActivityLog(
            activity_type="device_scan",
            description=f"扫描设备列表: 新增 {result['new_devices']} 台, 更新 {result['updated_devices']} 台",
            status="success"
        )
        db.add(activity)
        db.commit()
        
        logger.info(f"设备扫描完成: {result}")
        
        return Response(
            message=f"设备扫描完成: 新增 {result['new_devices']} 台, 更新 {result['updated_devices']} 台",
            data=result
        )
    except Exception as e:
        logger.error(f"扫描设备失败: {e}")
        
        # 记录失败日志
        activity = ActivityLog(
            activity_type="device_scan",
            description=f"扫描设备失败: {str(e)}",
            status="failed"
        )
        db.add(activity)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"扫描设备失败: {str(e)}")


@router.post("/{device_id}/disconnect", response_model=Response)
async def disconnect_device(device_id: int, db: Session = Depends(get_session)):
    """断开设备连接"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    device.status = "offline"
    device.updated_at = datetime.now()
    db.add(device)
    
    # 记录活动日志
    activity = ActivityLog(
        activity_type="device_disconnect",
        description=f"{device.model} 已断开连接",
        related_id=device.id,
        related_type="device",
        status="success"
    )
    db.add(activity)
    db.commit()
    
    return Response(message="设备已断开连接")


@router.get("/groups/list", response_model=Response[list])
async def get_device_groups(db: Session = Depends(get_session)):
    """获取设备分组列表"""
    query = select(Device.group_name).distinct().where(Device.group_name.isnot(None))
    groups = db.exec(query).all()
    return Response(data=[g for g in groups if g])


@router.put("/{device_id}/group", response_model=Response[Device])
async def update_device_group(
    device_id: int,
    group_name: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """更新设备分组"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    device.group_name = group_name
    device.updated_at = datetime.now()
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return Response(message="设备分组已更新", data=device)


@router.get("/{device_id}/screenshot", response_model=Response[dict])
async def get_device_screenshot(device_id: int, db: Session = Depends(get_session)):
    """获取设备实时截图"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    if device.status != "online":
        raise HTTPException(status_code=400, detail="设备未连接")
    
    # TODO: 实现 ADB 截图逻辑
    logger.info(f"获取设备 {device.serial_number} 截图（预留接口）")
    
    return Response(
        message="截图获取成功",
        data={
            "device_id": device_id,
            "screenshot_url": "/api/screenshots/placeholder.png",
            "timestamp": datetime.now().isoformat()
        }
    )


@router.get("/{device_id}/performance", response_model=Response[dict])
async def get_device_performance(device_id: int, db: Session = Depends(get_session)):
    """获取设备性能数据"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    if device.status != "online":
        raise HTTPException(status_code=400, detail="设备未连接")
    
    # TODO: 实现 ADB 性能监控逻辑
    logger.info(f"获取设备 {device.serial_number} 性能数据（预留接口）")
    
    return Response(
        message="性能数据获取成功",
        data={
            "device_id": device_id,
            "cpu_usage": device.cpu_usage or 0.0,
            "memory_usage": device.memory_usage or 0.0,
            "battery": device.battery,
            "temperature": 35.0,
            "timestamp": datetime.now().isoformat()
        }
    )


class DeviceCreate(BaseModel):
    """创建设备请求"""
    serial_number: str
    model: str
    android_version: str
    resolution: Optional[str] = None
    battery: int = 0
    status: str = "offline"
    group_name: Optional[str] = None


class DeviceUpdate(BaseModel):
    """更新设备请求"""
    model: Optional[str] = None
    android_version: Optional[str] = None
    resolution: Optional[str] = None
    battery: Optional[int] = None
    battery_level: Optional[int] = None  # 兼容字段
    status: Optional[str] = None
    group_name: Optional[str] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None


@router.post("", response_model=Response[Device])
async def create_device(device_data: DeviceCreate, db: Session = Depends(get_session)):
    """创建设备"""
    # 检查序列号是否已存在
    existing = db.exec(select(Device).where(Device.serial_number == device_data.serial_number)).first()
    if existing:
        raise HTTPException(status_code=400, detail="设备序列号已存在")
    
    device = Device(**device_data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    
    # 记录活动日志
    activity = ActivityLog(
        activity_type="device_create",
        description=f"创建设备: {device.model}",
        related_id=device.id,
        related_type="device",
        status="success"
    )
    db.add(activity)
    db.commit()
    
    # 再次刷新以确保获取最新数据
    db.refresh(device)
    return Response(message="设备创建成功", data=device.model_dump())


@router.put("/{device_id}", response_model=Response[Device])
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_session)
):
    """更新设备"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新字段（兼容 battery_level 字段）
    update_dict = device_data.model_dump(exclude_unset=True)
    if "battery_level" in update_dict:
        update_dict["battery"] = update_dict.pop("battery_level")
    
    for key, value in update_dict.items():
        setattr(device, key, value)
    
    device.updated_at = datetime.now()
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return Response(message="设备更新成功", data=device.model_dump())


@router.delete("/{device_id}", response_model=Response)
async def delete_device(device_id: int, db: Session = Depends(get_session)):
    """删除设备"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 记录活动日志
    activity = ActivityLog(
        activity_type="device_delete",
        description=f"删除设备: {device.model}",
        related_id=device.id,
        related_type="device",
        status="success"
    )
    db.add(activity)
    
    db.delete(device)
    db.commit()
    
    return Response(message="设备删除成功")


class BatchExecuteRequest(BaseModel):
    """批量执行请求"""
    device_ids: list[int]
    script_id: int


@router.post("/batch/execute", response_model=Response[dict])
async def batch_execute_script(
    request: BatchExecuteRequest,
    db: Session = Depends(get_session)
):
    """批量执行脚本"""
    # 验证设备
    devices = db.exec(select(Device).where(Device.id.in_(request.device_ids))).all()
    if len(devices) != len(request.device_ids):
        raise HTTPException(status_code=404, detail="部分设备不存在")
    
    # TODO: 实现批量执行逻辑
    logger.info(f"批量执行脚本 {request.script_id} 到 {len(devices)} 个设备（预留接口）")
    
    return Response(
        message=f"已向 {len(devices)} 个设备发送执行任务",
        data={
            "device_count": len(devices),
            "script_id": request.script_id,
            "task_ids": []
        }
    )
