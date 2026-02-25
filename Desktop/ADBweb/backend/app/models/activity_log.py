"""
活动日志表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ActivityLog(SQLModel, table=True):
    """活动日志表"""
    __tablename__ = "activity_log"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="活动ID")
    activity_type: str = Field(max_length=50, description="活动类型")
    description: str = Field(description="活动描述")
    user_name: str = Field(default="系统", max_length=100, description="操作人")
    related_id: Optional[int] = Field(default=None, description="关联对象ID")
    related_type: Optional[str] = Field(default=None, max_length=50, description="关联对象类型")
    status: str = Field(default="success", max_length=20, description="活动状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
