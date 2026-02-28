"""
任务执行日志表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TaskLog(SQLModel, table=True):
    """任务执行日志表"""
    __tablename__ = "task_log"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="日志ID")
    task_name: str = Field(max_length=200, description="任务名称")
    script_id: Optional[int] = Field(default=None, foreign_key="script.id", index=True, description="关联脚本ID")  # 添加索引
    device_id: Optional[int] = Field(default=None, foreign_key="device.id", index=True, description="关联设备ID")  # 添加索引
    scheduled_task_id: Optional[int] = Field(default=None, foreign_key="scheduled_task.id", index=True, description="关联定时任务ID")  # 添加索引
    status: str = Field(default="running", max_length=20, index=True, description="执行状态")  # 添加索引
    start_time: datetime = Field(default_factory=datetime.now, index=True, description="开始时间")  # 添加索引
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration: Optional[float] = Field(default=None, description="执行耗时")
    log_content: Optional[str] = Field(default=None, description="日志内容")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    screenshot_paths: Optional[str] = Field(default=None, description="截图路径")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
