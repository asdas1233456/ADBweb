"""
设备健康度 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models.device_health import (
    DeviceHealthRecord, 
    DeviceUsageStats, 
    DeviceAlert,
    AlertRule
)
from app.models.device import Device
from app.schemas.common import Response
from app.services.device_health import DeviceHealthService
from app.services.alert_engine import AlertEngine
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/device-health", tags=["设备健康度"])


@router.get("/devices/{device_id}/health", response_model=Response)
async def get_device_health(
    device_id: int,
    db: Session = Depends(get_session)
):
    """获取设备当前健康度"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 获取最新的健康度记录
    statement = select(DeviceHealthRecord).where(
        DeviceHealthRecord.device_id == device_id
    ).order_by(DeviceHealthRecord.created_at.desc()).limit(1)
    
    health_record = db.exec(statement).first()
    
    if not health_record:
        return Response(
            message="暂无健康度数据",
            data=None
        )
    
    # 获取健康等级
    health_service = DeviceHealthService()
    level_code, level_name, level_color = health_service.get_health_level(
        health_record.health_score
    )
    
    return Response(
        data={
            "device_id": device_id,
            "device_name": device.model,
            "health_score": health_record.health_score,
            "level_code": level_code,
            "level_name": level_name,
            "level_color": level_color,
            "battery_level": health_record.battery_level,
            "temperature": health_record.temperature,
            "cpu_usage": health_record.cpu_usage,
            "memory_usage": health_record.memory_usage,
            "storage_usage": health_record.storage_usage,
            "network_status": health_record.network_status,
            "last_check_time": health_record.created_at.isoformat()
        }
    )


@router.get("/devices/{device_id}/health/history", response_model=Response)
async def get_device_health_history(
    device_id: int,
    hours: int = Query(default=24, description="查询最近N小时的数据"),
    db: Session = Depends(get_session)
):
    """获取设备健康度历史"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 查询指定时间范围内的记录
    start_time = datetime.now() - timedelta(hours=hours)
    statement = select(DeviceHealthRecord).where(
        DeviceHealthRecord.device_id == device_id,
        DeviceHealthRecord.created_at >= start_time
    ).order_by(DeviceHealthRecord.created_at.asc())
    
    records = db.exec(statement).all()
    
    return Response(
        data={
            "device_id": device_id,
            "records": [
                {
                    "health_score": r.health_score,
                    "battery_level": r.battery_level,
                    "temperature": r.temperature,
                    "cpu_usage": r.cpu_usage,
                    "memory_usage": r.memory_usage,
                    "created_at": r.created_at.isoformat()
                }
                for r in records
            ]
        }
    )


@router.get("/devices/{device_id}/history", response_model=Response)
async def get_device_history(
    device_id: int,
    hours: int = Query(default=24, description="查询最近N小时的数据"),
    db: Session = Depends(get_session)
):
    """获取设备健康度历史（别名接口）"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 查询指定时间范围内的记录
    start_time = datetime.now() - timedelta(hours=hours)
    statement = select(DeviceHealthRecord).where(
        DeviceHealthRecord.device_id == device_id,
        DeviceHealthRecord.created_at >= start_time
    ).order_by(DeviceHealthRecord.created_at.asc())
    
    records = db.exec(statement).all()
    
    return Response(
        data={
            "device_id": device_id,
            "records": [
                {
                    "health_score": r.health_score,
                    "battery_level": r.battery_level,
                    "temperature": r.temperature,
                    "cpu_usage": r.cpu_usage,
                    "memory_usage": r.memory_usage,
                    "created_at": r.created_at.isoformat()
                }
                for r in records
            ]
        }
    )


@router.get("/devices/{device_id}/stats", response_model=Response)
async def get_device_stats(
    device_id: int,
    db: Session = Depends(get_session)
):
    """获取设备使用统计"""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 获取使用统计
    statement = select(DeviceUsageStats).where(
        DeviceUsageStats.device_id == device_id
    )
    stats = db.exec(statement).first()
    
    if not stats:
        return Response(
            data={
                "device_id": device_id,
                "total_executions": 0,
                "success_executions": 0,
                "failed_executions": 0,
                "success_rate": 0,
                "avg_duration": 0
            }
        )
    
    return Response(
        data={
            "device_id": device_id,
            "total_executions": stats.total_executions,
            "success_executions": stats.success_executions,
            "failed_executions": stats.failed_executions,
            "success_rate": stats.success_rate or 0,
            "avg_duration": stats.avg_duration or 0,
            "last_execution_time": stats.last_execution_time.isoformat() if stats.last_execution_time else None
        }
    )


@router.get("/alerts", response_model=Response)
async def get_alerts(
    device_id: Optional[int] = None,
    is_resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """获取告警列表"""
    statement = select(DeviceAlert)
    
    # 添加筛选条件
    if device_id is not None:
        statement = statement.where(DeviceAlert.device_id == device_id)
    if is_resolved is not None:
        statement = statement.where(DeviceAlert.is_resolved == is_resolved)
    if severity:
        statement = statement.where(DeviceAlert.severity == severity)
    
    statement = statement.order_by(DeviceAlert.created_at.desc())
    
    alerts = db.exec(statement).all()
    
    return Response(
        data=[
            {
                "id": alert.id,
                "device_id": alert.device_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "is_resolved": alert.is_resolved,
                "created_at": alert.created_at.isoformat(),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            for alert in alerts
        ]
    )


@router.post("/alerts/{alert_id}/resolve", response_model=Response)
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_session)
):
    """解决告警"""
    alert_engine = AlertEngine(db)
    success = alert_engine.resolve_alert(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="告警不存在或已解决")
    
    return Response(message="告警已解决")


@router.get("/alert-rules", response_model=Response)
async def get_alert_rules(
    db: Session = Depends(get_session)
):
    """获取告警规则列表"""
    statement = select(AlertRule)
    rules = db.exec(statement).all()
    
    return Response(
        data=[
            {
                "id": rule.id,
                "rule_name": rule.rule_name,
                "rule_type": rule.rule_type,
                "condition_field": rule.condition_field,
                "operator": rule.operator,
                "threshold_value": rule.threshold_value,
                "severity": rule.severity,
                "is_enabled": rule.is_enabled
            }
            for rule in rules
        ]
    )


@router.get("/overview", response_model=Response)
async def get_health_overview(
    db: Session = Depends(get_session)
):
    """获取健康度总览（优化版）"""
    # 使用子查询获取每个设备的最新健康度记录ID
    subquery = (
        select(
            DeviceHealthRecord.device_id,
            func.max(DeviceHealthRecord.id).label('max_id')
        )
        .group_by(DeviceHealthRecord.device_id)
        .subquery()
    )
    
    # 一次性查询所有设备的最新健康度记录
    statement = (
        select(DeviceHealthRecord, Device)
        .join(subquery, DeviceHealthRecord.id == subquery.c.max_id)
        .join(Device, DeviceHealthRecord.device_id == Device.id)
    )
    
    results = db.exec(statement).all()
    
    health_service = DeviceHealthService()
    health_data = []
    
    for health_record, device in results:
        level_code, level_name, level_color = health_service.get_health_level(
            health_record.health_score
        )
        
        health_data.append({
            "device_id": device.id,
            "device_name": device.model,
            "health_score": health_record.health_score,
            "level_code": level_code,
            "level_name": level_name,
            "level_color": level_color,
            "battery_level": health_record.battery_level,
            "temperature": health_record.temperature,
            "cpu_usage": health_record.cpu_usage,
            "memory_usage": health_record.memory_usage,
            "storage_usage": health_record.storage_usage,
            "network_status": health_record.network_status,
            "last_check_time": health_record.created_at.isoformat()
        })
    
    # 获取未解决的告警数量
    unresolved_alerts = db.exec(
        select(func.count(DeviceAlert.id)).where(DeviceAlert.is_resolved == False)
    ).one()
    
    return Response(
        data={
            "devices": health_data,
            "unresolved_alerts": unresolved_alerts
        }
    )


@router.post("/collect", response_model=Response)
async def trigger_health_collection(
    db: Session = Depends(get_session)
):
    """手动触发健康度采集"""
    from app.services.health_scheduler import health_scheduler
    import asyncio
    
    try:
        # 在后台执行采集任务
        asyncio.create_task(health_scheduler.collect_device_health())
        
        return Response(
            message="健康度采集任务已启动，请稍后刷新查看结果"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"启动采集任务失败: {str(e)}"
        )
