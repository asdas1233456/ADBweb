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
async def execute_scheduled_task(
    task_id: int, 
    device_id: Optional[int] = None,  # 允许临时指定设备
    db: Session = Depends(get_session)
):
    """立即执行定时任务"""
    from app.models.task_log import TaskLog
    from app.services.task_executor import TaskExecutor
    from fastapi import BackgroundTasks
    
    task = db.get(ScheduledTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    # 使用指定的设备ID，如果没有指定则使用任务默认的设备
    target_device_id = device_id if device_id is not None else task.device_id
    
    # 获取脚本和设备信息
    script = db.get(Script, task.script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    device = db.get(Device, target_device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 允许在线和空闲状态的设备执行任务
    if device.status not in ["online", "idle"]:
        raise HTTPException(status_code=400, detail=f"设备当前状态为 {device.status}，无法执行任务")
    
    # 创建任务日志（使用选择的设备ID）
    task_log = TaskLog(
        task_name=f"[定时任务] {task.name}",
        script_id=task.script_id,
        device_id=target_device_id,
        scheduled_task_id=task_id,
        status="running",
        start_time=datetime.now()
    )
    db.add(task_log)
    
    # 更新设备状态
    device.status = "busy"
    db.add(device)
    
    # 更新定时任务统计
    task.run_count = (task.run_count or 0) + 1
    task.last_run_at = datetime.now()
    db.add(task)
    
    db.commit()
    db.refresh(task_log)
    
    # 获取脚本步骤
    steps = []
    if script.steps_json:
        import json
        try:
            steps = json.loads(script.steps_json)
        except:
            steps = []
    
    # 在后台执行任务
    import asyncio
    from app.core.database import engine
    from app.services.failure_service import FailureService
    
    async def execute_task_background():
        executor = TaskExecutor()
        
        try:
            # 根据脚本类型执行不同逻辑
            if script.type == "visual":
                # 可视化脚本：执行步骤
                result = await executor.execute_script(
                    task_id=task_log.id,
                    script_id=script.id,
                    device_id=device.id,
                    steps=steps
                )
            elif script.type in ["python", "batch"]:
                # Python/批处理脚本：执行文件内容
                result = await executor.execute_file_script(
                    task_id=task_log.id,
                    script=script,
                    device_id=device.id
                )
            else:
                raise Exception(f"不支持的脚本类型: {script.type}")
            
            # 更新任务日志
            with Session(engine) as db_session:
                task_log_update = db_session.get(TaskLog, task_log.id)
                if task_log_update:
                    task_log_update.status = result["status"]
                    task_log_update.end_time = datetime.now()
                    if result["status"] == "failed":
                        task_log_update.error_message = result.get("message", "执行失败")
                    
                    # 计算执行时长
                    if task_log_update.start_time and task_log_update.end_time:
                        duration = (task_log_update.end_time - task_log_update.start_time).total_seconds()
                        task_log_update.duration = int(duration)
                    
                    db_session.add(task_log_update)
                    
                    # 更新定时任务成功次数
                    scheduled_task = db_session.get(ScheduledTask, task_id)
                    if scheduled_task and result["status"] == "success":
                        scheduled_task.success_count = (scheduled_task.success_count or 0) + 1
                        db_session.add(scheduled_task)
                    
                    db_session.commit()
                    
                    # 如果失败，自动分析
                    if result["status"] == "failed":
                        logger.info(f"🔍 开始分析失败原因...")
                        failure_service = FailureService(db_session)
                        await failure_service.analyze_task_failure(task_log.id)
                    
                    # 恢复设备状态
                    device_update = db_session.get(Device, device.id)
                    if device_update:
                        device_update.status = "online"
                        db_session.add(device_update)
                        db_session.commit()
                    
                    logger.info(f"✅ 定时任务完成: {task_log.id}, 状态: {result['status']}")
        
        except Exception as e:
            logger.error(f"❌ 定时任务执行异常: {task_log.id}, 错误: {e}")
            
            # 更新失败状态
            with Session(engine) as db_session:
                task_log_update = db_session.get(TaskLog, task_log.id)
                if task_log_update:
                    task_log_update.status = "failed"
                    task_log_update.end_time = datetime.now()
                    task_log_update.error_message = str(e)
                    db_session.add(task_log_update)
                    db_session.commit()
                    
                    # 自动分析失败
                    failure_service = FailureService(db_session)
                    await failure_service.analyze_task_failure(task_log.id)
                    
                    # 恢复设备状态
                    device_update = db_session.get(Device, device.id)
                    if device_update:
                        device_update.status = "online"
                        db_session.add(device_update)
                        db_session.commit()
    
    # 启动后台任务
    asyncio.create_task(execute_task_background())
    
    logger.info(f"✅ 定时任务已创建: {task.name} (ID: {task_log.id})")
    
    return Response(
        message="任务已开始执行",
        data={"task_log_id": task_log.id, "status": "running"}
    )
