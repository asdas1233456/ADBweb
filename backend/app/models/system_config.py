"""
系统配置表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class SystemConfig(SQLModel, table=True):
    """系统配置表"""
    __tablename__ = "system_config"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="配置ID")
    config_key: str = Field(unique=True, max_length=100, description="配置键")
    config_value: Optional[str] = Field(default=None, description="配置值")
    config_type: str = Field(default="string", max_length=20, description="配置类型")
    description: Optional[str] = Field(default=None, max_length=500, description="配置说明")
    is_system: bool = Field(default=False, description="是否系统配置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
