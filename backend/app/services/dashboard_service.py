"""
仪表盘服务
"""
from sqlmodel import Session, select, func
from app.models import Device, Script, TaskLog, ActivityLog
from app.schemas.dashboard import (
    DashboardOverview, Statistics, DeviceStatusItem,
    ExecutionStats, RecentActivity
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """仪表盘服务类"""
    
    @staticmethod
    def get_dashboard_overview(db: Session) -> DashboardOverview:
        """获取仪表盘概览数据"""
        try:
            # 统计数据
            total_devices = db.exec(select(func.count(Device.id))).one()
            online_devices = db.exec(
                select(func.count(Device.id)).where(Device.status == "online")
            ).one()
            total_scripts = db.exec(
                select(func.count(Script.id)).where(Script.is_active == True)
            ).one()
            
            # 今日执行次数
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_executions = db.exec(
                select(func.count(TaskLog.id)).where(TaskLog.start_time >= today_start)
            ).one()
            
            # 计算成功率（最近100条记录）
            recent_logs = db.exec(
                select(TaskLog).order_by(TaskLog.start_time.desc()).limit(100)
            ).all()
            
            if recent_logs:
                success_count = sum(1 for log in recent_logs if log.status == "success")
                success_rate = round((success_count / len(recent_logs)) * 100, 1)
            else:
                success_rate = 0.0
            
            statistics = Statistics(
                online_devices=online_devices,
                total_devices=total_devices,
                total_scripts=total_scripts,
                today_executions=today_executions,
                success_rate=success_rate
            )
            
            # 设备状态
            devices = db.exec(select(Device)).all()
            device_status = [
                DeviceStatusItem(
                    id=device.id,
                    model=device.model,
                    battery=device.battery,
                    status=device.status
                )
                for device in devices
            ]
            
            # 执行统计（本周）
            week_start = datetime.now() - timedelta(days=7)
            week_logs = db.exec(
                select(TaskLog).where(TaskLog.start_time >= week_start)
            ).all()
            
            success_count = sum(1 for log in week_logs if log.status == "success")
            failed_count = sum(1 for log in week_logs if log.status == "failed")
            running_count = sum(1 for log in week_logs if log.status == "running")
            total_count = len(week_logs)
            
            execution_stats = ExecutionStats(
                success_count=success_count,
                failed_count=failed_count,
                running_count=running_count,
                total_count=total_count,
                success_percentage=round((success_count / total_count * 100) if total_count > 0 else 0, 1),
                failed_percentage=round((failed_count / total_count * 100) if total_count > 0 else 0, 1),
                running_percentage=round((running_count / total_count * 100) if total_count > 0 else 0, 1)
            )
            
            # 最近活动
            activities = db.exec(
                select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(10)
            ).all()
            
            recent_activities = [
                RecentActivity(
                    id=activity.id,
                    activity_type=activity.activity_type,
                    description=activity.description,
                    user_name=activity.user_name,
                    status=activity.status,
                    created_at=activity.created_at.strftime("%Y-%m-%d %H:%M:%S")
                )
                for activity in activities
            ]
            
            return DashboardOverview(
                statistics=statistics,
                device_status=device_status,
                execution_stats=execution_stats,
                recent_activities=recent_activities
            )
            
        except Exception as e:
            logger.error(f"获取仪表盘数据失败: {e}")
            raise
