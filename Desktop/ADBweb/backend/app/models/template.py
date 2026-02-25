"""
模板表模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Template(SQLModel, table=True):
    """模板表"""
    __tablename__ = "template"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="模板ID")
    name: str = Field(max_length=200, description="模板名称")
    description: str = Field(description="模板描述")
    author: str = Field(default="系统", max_length=100, description="模板作者")
    category: str = Field(default="other", max_length=50, description="模板分类")
    type: str = Field(default="visual", max_length=20, description="模板类型")
    tags: Optional[str] = Field(default=None, max_length=500, description="标签")
    content: str = Field(description="模板内容")
    preview: Optional[str] = Field(default=None, description="预览内容")
    downloads: int = Field(default=0, description="下载次数")
    rating: float = Field(default=0.0, description="评分")
    is_featured: bool = Field(default=False, description="是否精选")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
