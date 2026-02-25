"""
任务执行API路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from datetime import datetime
from app.core.database import get_session
from app.models.task_log import TaskLog
from app.models.script import Script
from app.models.device import Device
from app.schemas.common import Response
from app.services.task_executor import TaskExecutor
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/tasks", tags=["任务执行"])


class TaskExecute(BaseModel):
    """执行任务请求模型"""
    task_name: str
    script_id: int
    device_id: int


@router.post("/execute", response_model=Response)
async def execute_task(
    task_data: TaskExecute, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session)
):
    """执行脚本(支持实时推送)"""
    # 验证脚本和设备是否存在
    script = db.get(Script, task_data.script_id)
    if not script or not script.is_active:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    device = db.get(Device, task_data.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    if device.status != "online":
        raise HTTPException(status_code=400, detail="设备离线或忙碌")
    
    # 创建任务日志
    task_log = TaskLog(
        task_name=task_data.task_name,
        script_id=task_data.script_id,
        device_id=task_data.device_id,
        status="running",
        start_time=datetime.now()
    )
    db.add(task_log)
    
    # 更新设备状态
    device.status = "busy"
    db.add(device)
    
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
    background_tasks.add_task(
        execute_task_background,
        task_log.id,
        task_data.script_id,
        task_data.device_id,
        steps
    )
    
    print(f"✅ 任务已创建: {task_data.task_name} (ID: {task_log.id})")
    
    return Response(
        message="任务已开始执行",
        data={"task_log_id": task_log.id, "status": "running"}
    )


async def execute_task_background(
    task_log_id: int,
    script_id: int,
    device_id: int,
    steps: list
):
    """后台执行任务"""
    from app.core.database import engine
    from app.services.failure_service import FailureService
    
    executor = TaskExecutor()
    
    try:
        # 执行脚本
        result = await executor.execute_script(
            task_id=task_log_id,
            script_id=script_id,
            device_id=device_id,
            steps=steps
        )
        
        # 更新任务日志
        with Session(engine) as db:
            task_log = db.get(TaskLog, task_log_id)
            if task_log:
                task_log.status = result["status"]
                task_log.end_time = datetime.now()
                if result["status"] == "failed":
                    task_log.error_message = result.get("message", "执行失败")
                
                # 计算执行时长
                if task_log.start_time and task_log.end_time:
                    duration = (task_log.end_time - task_log.start_time).total_seconds()
                    task_log.duration = int(duration)
                
                db.add(task_log)
                db.commit()
                
                # 如果失败，自动分析
                if result["status"] == "failed":
                    print(f"🔍 开始分析失败原因...")
                    failure_service = FailureService(db)
                    await failure_service.analyze_task_failure(task_log_id)
                
                # 恢复设备状态
                device = db.get(Device, device_id)
                if device:
                    device.status = "online"
                    db.add(device)
                    db.commit()
                
                print(f"✅ 任务完成: {task_log_id}, 状态: {result['status']}")
    
    except Exception as e:
        print(f"❌ 任务执行异常: {task_log_id}, 错误: {e}")
        
        # 更新失败状态
        with Session(engine) as db:
            task_log = db.get(TaskLog, task_log_id)
            if task_log:
                task_log.status = "failed"
                task_log.end_time = datetime.now()
                task_log.error_message = str(e)
                db.add(task_log)
                db.commit()
                
                # 自动分析失败
                failure_service = FailureService(db)
                await failure_service.analyze_task_failure(task_log_id)
                
                # 恢复设备状态
                device = db.get(Device, device_id)
                if device:
                    device.status = "online"
                    db.add(device)
                    db.commit()



@router.get("/{task_log_id}/logs", response_model=Response[TaskLog])
async def get_task_logs(task_log_id: int, db: Session = Depends(get_session)):
    """获取任务执行日志"""
    task_log = db.get(TaskLog, task_log_id)
    if not task_log:
        raise HTTPException(status_code=404, detail="任务日志不存在")
    return Response(data=task_log)


@router.post("/{task_log_id}/stop", response_model=Response)
async def stop_task(task_log_id: int, db: Session = Depends(get_session)):
    """停止任务执行"""
    task_log = db.get(TaskLog, task_log_id)
    if not task_log:
        raise HTTPException(status_code=404, detail="任务日志不存在")
    
    if task_log.status != "running":
        raise HTTPException(status_code=400, detail="任务未在运行中")
    
    # 更新任务状态
    task_log.status = "failed"
    task_log.end_time = datetime.now()
    task_log.error_message = "用户手动停止"
    db.add(task_log)
    
    # 更新设备状态
    if task_log.device_id:
        device = db.get(Device, task_log.device_id)
        if device:
            device.status = "online"
            db.add(device)
    
    db.commit()
    
    # TODO: 预留接口：停止正在执行的脚本进程
    print(f"[INFO] 停止任务: {task_log_id}")
    
    return Response(message="任务已停止")
