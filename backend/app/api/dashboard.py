"""
仪表盘API路由
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.dashboard_service import DashboardService
from app.schemas.common import Response
from app.schemas.dashboard import DashboardOverview

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/overview", response_model=Response[DashboardOverview])
async def get_dashboard_overview(db: Session = Depends(get_session)):
    """获取仪表盘概览数据"""
    data = DashboardService.get_dashboard_overview(db)
    return Response(data=data)


@router.get("/stats", response_model=Response[DashboardOverview])
async def get_dashboard_stats(db: Session = Depends(get_session)):
    """获取仪表盘统计数据（别名接口）"""
    data = DashboardService.get_dashboard_overview(db)
    return Response(data=data)
