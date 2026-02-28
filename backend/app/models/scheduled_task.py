"""
定时任务表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, time
from typing import Optional


class ScheduledTask(SQLModel, table=True):
    """定时任务表"""
    __tablename__ = "scheduled_task"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="任务ID")
    name: str = Field(max_length=200, description="任务名称")
    script_id: int = Field(foreign_key="script.id", description="关联脚本ID")
    device_id: int = Field(foreign_key="device.id", description="关联设备ID")
    frequency: str = Field(max_length=50, description="执行频率")
    schedule_time: str = Field(description="执行时间")
    schedule_day: Optional[str] = Field(default=None, max_length=20, description="执行日期")
    cron_expression: Optional[str] = Field(default=None, max_length=100, description="Cron表达式")
    priority: int = Field(default=0, description="任务优先级(0-10,数字越大优先级越高)")
    retry_count: int = Field(default=0, description="失败重试次数")
    max_retry: int = Field(default=3, description="最大重试次数")
    depends_on: Optional[str] = Field(default=None, max_length=200, description="依赖任务ID列表(逗号分隔)")
    is_enabled: bool = Field(default=True, description="是否启用")
    last_run_at: Optional[datetime] = Field(default=None, description="上次运行时间")
    next_run_at: Optional[datetime] = Field(default=None, description="下次运行时间")
    run_count: int = Field(default=0, description="累计运行次数")
    success_count: int = Field(default=0, description="成功次数")
    fail_count: int = Field(default=0, description="失败次数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
