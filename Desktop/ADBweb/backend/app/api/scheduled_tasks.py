"""
定时任务API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import ScheduledTask, Script, Device, ActivityLog
from app.schemas.common import Response, PageResponse
from app.services.scheduler_service import scheduler_service
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

router = APIRouter(prefix="/scheduled-tasks", tags=["定时任务"])
logger = logging.getLogger(__name__)


class ScheduledTaskCreate(BaseModel):
    """创建定时任务"""
    name: str
    script_id: int
    device_id: int
    frequency: str
    schedule_time: str
    schedule_day: Optional[str] = None
    cron_expression: Optional[str] = None
    priority: int = 0
    max_retry: int = 3
    depends_on: Optional[str] = None


class ScheduledTaskUpdate(BaseModel):
    """更新定时任务"""
    name: Optional[str] = None
    script_id: Optional[int] = None
    device_id: Optional[int] = None
    frequency: Optional[str] = None
    schedule_time: Optional[str] = None
    schedule_day: Optional[str] = None
    cron_expression: Optional[str] = None
    priority: Optional[int] = None
    max_retry: Optional[int] = None
    depends_on: Optional[str] = None


class ToggleTaskRequest(BaseModel):
    """切换任务状态"""
    is_enabled: bool


@router.get("", response_model=Response[PageResponse[ScheduledTask]])
async def get_scheduled_tasks(
    is_enabled: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_session)
):
    """获取定时任务列表"""
    query = select(ScheduledTask)
    
    if is_enabled is not None:
        query = query.where(ScheduledTask.is_enabled == is_enabled)
    
    total = len(db.exec(query).all())
    offset = (page - 1) * page_size
    tasks = db.exec(query.offset(offset).limit(page_size)).all()
    
    page_data = PageResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
    
    return Response(data=page_data)


@router.get("/{task_id}", response_model=Response[ScheduledTask])
async def get_scheduled_task(task_id: int, db: Session = Depends(get_session)):
    """获取定时任务详情"""
    task = db.get(ScheduledTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    return Response(data=task)


@router.post("", response_model=Response[ScheduledTask])
async def create_scheduled_task(
    task_data: ScheduledTaskCreate,
    db: Session = Depends(get_session)
):
    """创建定时任务"""
    # 验证脚本和设备是否存在
    script = db.get(Script, task_data.script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    device = db.get(Device, task_data.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 创建任务
    task = ScheduledTask(**task_data.dict())
    
    # 计算下次运行时间
    task.next_run_at = datetime.now()  # 简化处理
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 添加到调度器
    scheduler_service.add_task(task)
    
    # 记录活动日志
    activity = ActivityLog(
        activity_type="scheduled_task_create",
        description=f"创建定时任务: {task.name}",
        related_id=task.id,
        related_type="task",
        status="success"
    )
    db.add(activity)
    db.commit()
    
    return Response(message="定时任务创建成功", data=task)


@router.put("/{task_id}", response_model=Response[ScheduledTask])
async def update_scheduled_task(
    task_id: int,
    task_data: ScheduledTaskUpdate,
    db: Session = Depends(get_session)
):
    """更新定时任务"""
    task = db.get(ScheduledTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    # 更新字段
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    
    task.updated_at = datetime.now()
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 更新调度器
    scheduler_service.remove_task(task_id)
    if task.is_enabled:
        scheduler_service.add_task(task)
    
    return Response(message="定时任务更新成功", data=task)


@router.delete("/{task_id}", response_model=Response)
async def delete_scheduled_task(task_id: int, db: Session = Depends(get_session)):
    """删除定时任务"""
    task = db.get(ScheduledTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    # 从调度器移除
    scheduler_service.remove_task(task_id)
    
    # 删除任务
    db.delete(task)
    db.commit()
    
    return Response(message="定时任务删除成功")


@router.put("/{task_id}/toggle", response_model=Response[dict])
async def toggle_scheduled_task(
    task_id: int,
    toggle_data: ToggleTaskRequest,
    db: Session = Depends(get_session)
):
    """切换定时任务状态"""
    task = db.get(ScheduledTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    task.is_enabled = toggle_data.is_enabled
    task.updated_at = datetime.now()
    db.add(task)
    db.commit()
    
    # 更新调度器
    if toggle_data.is_enabled:
        scheduler_service.resume_task(task_id)
    else:
        scheduler_service.pause_task(task_id)
    
    return Response(
        message="任务状态已更新",
        data={"id": task_id, "is_enabled": toggle_data.is_enabled}
    )


@router.post("/{task_id}/execute", response_model=Response[dict])
async def execute_scheduled_task(task_id: int, db: Session = Depends(get_session)):
    """立即执行定时任务"""
    task = db.get(ScheduledTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    # TODO: 调用脚本执行服务
    logger.info(f"立即执行定时任务: {task.name} (预留接口)")
    
    return Response(
        message="任务已开始执行",
        data={"task_log_id": 0, "status": "running"}
    )
