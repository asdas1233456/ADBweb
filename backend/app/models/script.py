"""
脚本表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Script(SQLModel, table=True):
    """脚本表"""
    __tablename__ = "script"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="脚本ID")
    name: str = Field(max_length=200, index=True, description="脚本名称")
    type: str = Field(default="visual", max_length=20, index=True, description="脚本类型")
    category: str = Field(default="other", max_length=50, index=True, description="脚本分类")
    description: Optional[str] = Field(default=None, description="脚本描述")
    file_path: Optional[str] = Field(default=None, max_length=500, description="文件路径")
    file_content: Optional[str] = Field(default=None, description="文件内容")
    steps_json: Optional[str] = Field(default=None, description="可视化步骤JSON")
    is_active: bool = Field(default=True, index=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, index=True, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
