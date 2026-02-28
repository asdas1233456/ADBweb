"""
设备表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Device(SQLModel, table=True):
    """设备表"""
    __tablename__ = "device"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="设备ID")
    serial_number: str = Field(unique=True, index=True, max_length=100, description="设备序列号")
    model: str = Field(max_length=100, index=True, description="设备型号")  # 添加索引
    android_version: str = Field(max_length=20, description="Android版本")
    resolution: Optional[str] = Field(default=None, max_length=20, description="屏幕分辨率")
    battery: int = Field(default=0, ge=0, le=100, description="电池电量")
    status: str = Field(default="offline", max_length=20, index=True, description="设备状态")  # 添加索引
    group_name: Optional[str] = Field(default=None, max_length=100, index=True, description="设备分组")  # 添加索引
    cpu_usage: Optional[float] = Field(default=0.0, description="CPU使用率")
    memory_usage: Optional[float] = Field(default=0.0, description="内存使用率")
    last_connected_at: Optional[datetime] = Field(default=None, description="最后连接时间")
    created_at: datetime = Field(default_factory=datetime.now, index=True, description="创建时间")  # 添加索引
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
