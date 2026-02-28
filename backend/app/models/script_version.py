"""
脚本版本管理模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ScriptVersion(SQLModel, table=True):
    """脚本版本表"""
    __tablename__ = "script_version"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="版本ID")
    script_id: int = Field(foreign_key="script.id", description="关联脚本ID")
    version: str = Field(max_length=50, description="版本号")
    content: str = Field(description="脚本内容")
    change_log: Optional[str] = Field(default=None, description="变更日志")
    is_current: bool = Field(default=False, description="是否当前版本")
    created_by: Optional[str] = Field(default="system", max_length=100, description="创建者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class ScriptExecutionLog(SQLModel, table=True):
    """脚本执行日志表"""
    __tablename__ = "script_execution_log"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="日志ID")
    script_id: int = Field(foreign_key="script.id", description="关联脚本ID")
    version_id: Optional[int] = Field(default=None, foreign_key="script_version.id", description="版本ID")
    status: str = Field(max_length=20, description="执行状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    execution_time: Optional[float] = Field(default=None, description="执行时间(秒)")
    device_info: Optional[str] = Field(default=None, description="设备信息")
    created_at: datetime = Field(default_factory=datetime.now, description="执行时间")