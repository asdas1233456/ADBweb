"""
活动日志API路由
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Optional
from app.core.database import get_session
from app.models.activity_log import ActivityLog
from app.schemas.common import Response

router = APIRouter(prefix="/activity-logs", tags=["活动日志"])


@router.get("", response_model=Response)
async def get_activity_logs(
    activity_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_session)
):
    """获取活动日志列表"""
    query = select(ActivityLog).order_by(ActivityLog.created_at.desc())
    
    if activity_type:
        query = query.where(ActivityLog.activity_type == activity_type)
    if status:
        query = query.where(ActivityLog.status == status)
    
    query = query.limit(limit)
    logs = db.exec(query).all()
    
    return Response(data=logs)
