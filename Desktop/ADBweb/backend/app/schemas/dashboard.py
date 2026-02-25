"""
仪表盘相关模型
"""
from pydantic import BaseModel
from typing import List


class DeviceStatusItem(BaseModel):
    """设备状态项"""
    id: int
    model: str
    battery: int
    status: str


class ExecutionStats(BaseModel):
    """执行统计"""
    success_count: int
    failed_count: int
    running_count: int
    total_count: int
    success_percentage: float
    failed_percentage: float
    running_percentage: float


class Statistics(BaseModel):
    """统计数据"""
    online_devices: int
    total_devices: int
    total_scripts: int
    today_executions: int
    success_rate: float


class RecentActivity(BaseModel):
    """最近活动"""
    id: int
    activity_type: str
    description: str
    user_name: str
    status: str
    created_at: str


class DashboardOverview(BaseModel):
    """仪表盘概览"""
    statistics: Statistics
    device_status: List[DeviceStatusItem]
    execution_stats: ExecutionStats
    recent_activities: List[RecentActivity]
