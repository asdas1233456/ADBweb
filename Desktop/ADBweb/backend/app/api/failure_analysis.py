"""
失败分析 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models.failure_analysis import FailureAnalysis, ScriptFailureStats, StepExecutionLog
from app.models.task_log import TaskLog
from app.schemas.common import Response
from app.services.failure_service import FailureService
from app.services.failure_analyzer import FailureAnalyzer
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/failure-analysis", tags=["失败分析"])


@router.post("/tasks/{task_log_id}/analyze", response_model=Response)
async def analyze_task_failure(
    task_log_id: int,
    db: Session = Depends(get_session)
):
    """分析任务失败"""
    task_log = db.get(TaskLog, task_log_id)
    if not task_log:
        raise HTTPException(status_code=404, detail="任务日志不存在")
    
    if task_log.status != 'failed':
        raise HTTPException(status_code=400, detail="任务未失败，无需分析")
    
    service = FailureService(db)
    analysis = await service.analyze_task_failure(task_log_id)
    
    if not analysis:
        raise HTTPException(status_code=500, detail="分析失败")
    
    analyzer = FailureAnalyzer()
    suggestions = analysis.suggestions.split(',') if analysis.suggestions else []
    
    return Response(
        message="分析完成",
        data={
            "id": analysis.id,
            "task_log_id": analysis.task_log_id,
            "failure_type": analysis.failure_type,
            "failure_icon": analyzer.get_error_icon(analysis.failure_type),
            "severity": analyzer.get_error_severity(analysis.failure_type),
            "failed_step_index": analysis.failed_step_index,
            "failed_step_name": analysis.failed_step_name,
            "error_message": analysis.error_message,
            "suggestions": suggestions,
            "confidence": analysis.confidence,
            "screenshot_path": analysis.screenshot_path,
            "created_at": analysis.created_at.isoformat()
        }
    )


@router.get("/tasks/{task_log_id}", response_model=Response)
async def get_task_failure_analysis(
    task_log_id: int,
    db: Session = Depends(get_session)
):
    """获取任务失败分析"""
    statement = select(FailureAnalysis).where(
        FailureAnalysis.task_log_id == task_log_id
    )
    analysis = db.exec(statement).first()
    
    if not analysis:
        # 如果没有分析记录，尝试自动分析
        task_log = db.get(TaskLog, task_log_id)
        if task_log and task_log.status == 'failed':
            service = FailureService(db)
            analysis = await service.analyze_task_failure(task_log_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="未找到失败分析")
    
    analyzer = FailureAnalyzer()
    suggestions = analysis.suggestions.split(',') if analysis.suggestions else []
    
    return Response(
        data={
            "id": analysis.id,
            "task_log_id": analysis.task_log_id,
            "failure_type": analysis.failure_type,
            "failure_icon": analyzer.get_error_icon(analysis.failure_type),
            "severity": analyzer.get_error_severity(analysis.failure_type),
            "failed_step_index": analysis.failed_step_index,
            "failed_step_name": analysis.failed_step_name,
            "error_message": analysis.error_message,
            "suggestions": suggestions,
            "confidence": analysis.confidence,
            "screenshot_path": analysis.screenshot_path,
            "created_at": analysis.created_at.isoformat()
        }
    )


@router.get("/scripts/{script_id}/stats", response_model=Response)
async def get_script_failure_stats(
    script_id: int,
    db: Session = Depends(get_session)
):
    """获取脚本失败统计"""
    statement = select(ScriptFailureStats).where(
        ScriptFailureStats.script_id == script_id
    )
    stats = db.exec(statement).first()
    
    if not stats:
        return Response(
            data={
                "script_id": script_id,
                "total_failures": 0,
                "failure_by_type": {},
                "most_common_failure": None,
                "failure_rate": 0
            }
        )
    
    import json
    failure_by_type = json.loads(stats.failure_by_type) if stats.failure_by_type else {}
    
    return Response(
        data={
            "script_id": script_id,
            "total_failures": stats.total_failures,
            "failure_by_type": failure_by_type,
            "most_common_failure": stats.most_common_failure,
            "failure_rate": stats.failure_rate or 0,
            "last_failure_time": stats.last_failure_time.isoformat() if stats.last_failure_time else None
        }
    )


@router.get("/trend", response_model=Response)
async def get_failure_trend(
    script_id: Optional[int] = None,
    range: str = Query(default="week", description="时间范围: week/month/year"),
    db: Session = Depends(get_session)
):
    """获取失败趋势"""
    # 计算时间范围
    range_map = {
        'week': 7,
        'month': 30,
        'year': 365
    }
    days = range_map.get(range, 7)
    start_date = datetime.now() - timedelta(days=days)
    
    # 构建查询
    statement = select(FailureAnalysis).where(
        FailureAnalysis.created_at >= start_date
    )
    
    if script_id:
        # 通过task_log关联script
        statement = statement.join(TaskLog).where(TaskLog.script_id == script_id)
    
    analyses = db.exec(statement).all()
    
    # 统计失败类型分布
    failure_by_type = {}
    for analysis in analyses:
        failure_type = analysis.failure_type
        failure_by_type[failure_type] = failure_by_type.get(failure_type, 0) + 1
    
    return Response(
        data={
            "range": range,
            "total_failures": len(analyses),
            "failure_by_type": failure_by_type,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().isoformat()
        }
    )


@router.get("/tasks/{task_log_id}/steps", response_model=Response)
async def get_step_execution_logs(
    task_log_id: int,
    db: Session = Depends(get_session)
):
    """获取步骤执行日志"""
    statement = select(StepExecutionLog).where(
        StepExecutionLog.task_log_id == task_log_id
    ).order_by(StepExecutionLog.step_index)
    
    logs = db.exec(statement).all()
    
    return Response(
        data=[
            {
                "step_index": log.step_index,
                "step_name": log.step_name,
                "step_type": log.step_type,
                "status": log.status,
                "duration": log.duration,
                "error_message": log.error_message,
                "start_time": log.start_time.isoformat() if log.start_time else None,
                "end_time": log.end_time.isoformat() if log.end_time else None
            }
            for log in logs
        ]
    )


@router.get("/overview", response_model=Response)
async def get_failure_overview(
    days: int = Query(default=7, description="统计最近N天"),
    db: Session = Depends(get_session)
):
    """获取失败分析总览"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 总失败次数
    total_failures = db.exec(
        select(func.count(FailureAnalysis.id)).where(
            FailureAnalysis.created_at >= start_date
        )
    ).one()
    
    # 按类型统计
    analyses = db.exec(
        select(FailureAnalysis).where(
            FailureAnalysis.created_at >= start_date
        )
    ).all()
    
    failure_by_type = {}
    for analysis in analyses:
        failure_type = analysis.failure_type
        failure_by_type[failure_type] = failure_by_type.get(failure_type, 0) + 1
    
    # 最常见失败类型
    most_common = None
    if failure_by_type:
        most_common = max(failure_by_type.items(), key=lambda x: x[1])[0]
    
    # 获取最近的失败
    recent_failures = db.exec(
        select(FailureAnalysis)
        .order_by(FailureAnalysis.created_at.desc())
        .limit(5)
    ).all()
    
    analyzer = FailureAnalyzer()
    
    return Response(
        data={
            "total_failures": total_failures,
            "failure_by_type": failure_by_type,
            "most_common_failure": most_common,
            "recent_failures": [
                {
                    "id": f.id,
                    "task_log_id": f.task_log_id,
                    "failure_type": f.failure_type,
                    "failure_icon": analyzer.get_error_icon(f.failure_type),
                    "error_message": f.error_message,
                    "created_at": f.created_at.isoformat()
                }
                for f in recent_failures
            ]
        }
    )
