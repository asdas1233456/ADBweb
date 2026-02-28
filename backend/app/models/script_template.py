"""
脚本模板模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ScriptTemplate(SQLModel, table=True):
    """脚本模板表"""
    __tablename__ = "script_template"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="模板ID")
    name: str = Field(max_length=200, index=True, description="模板名称")
    category: str = Field(max_length=50, index=True, description="模板分类")
    description: Optional[str] = Field(default=None, description="模板描述")
    language: str = Field(default="adb", max_length=20, description="脚本语言")
    template_content: str = Field(description="模板内容")
    variables: Optional[str] = Field(default=None, description="模板变量JSON")
    tags: Optional[str] = Field(default=None, description="标签，逗号分隔")
    usage_count: int = Field(default=0, description="使用次数")
    is_builtin: bool = Field(default=False, description="是否内置模板")
    is_active: bool = Field(default=True, description="是否启用")
    created_by: Optional[str] = Field(default="system", max_length=100, description="创建者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")