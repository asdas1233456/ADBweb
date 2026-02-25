"""
示例库模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Example(SQLModel, table=True):
    """示例脚本表"""
    __tablename__ = "example"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="示例ID")
    title: str = Field(max_length=200, description="示例标题")
    description: str = Field(description="详细描述")
    category: str = Field(max_length=50, description="分类")
    difficulty: str = Field(default="beginner", max_length=20, description="难度级别")
    script_type: str = Field(max_length=20, description="脚本类型")
    code: str = Field(description="示例代码")
    tags: Optional[str] = Field(default=None, max_length=500, description="标签")
    use_case: Optional[str] = Field(default=None, description="使用场景")
    prerequisites: Optional[str] = Field(default=None, description="前置条件")
    expected_result: Optional[str] = Field(default=None, description="预期结果")
    author: str = Field(default="系统", max_length=100, description="作者")
    rating: float = Field(default=0.0, description="评分")
    download_count: int = Field(default=0, description="下载次数")
    view_count: int = Field(default=0, description="浏览次数")
    is_featured: bool = Field(default=False, description="是否精选")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class BestPractice(SQLModel, table=True):
    """最佳实践表"""
    __tablename__ = "best_practice"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="实践ID")
    title: str = Field(max_length=200, description="实践标题")
    category: str = Field(max_length=50, description="分类")
    content: str = Field(description="Markdown内容")
    code_examples: Optional[str] = Field(default=None, description="代码示例JSON")
    dos: Optional[str] = Field(default=None, description="推荐做法JSON")
    donts: Optional[str] = Field(default=None, description="不推荐做法JSON")
    tips: Optional[str] = Field(default=None, description="技巧提示JSON")
    difficulty: str = Field(default="beginner", max_length=20, description="难度级别")
    tags: Optional[str] = Field(default=None, max_length=500, description="标签")
    author: str = Field(default="系统", max_length=100, description="作者")
    view_count: int = Field(default=0, description="浏览次数")
    like_count: int = Field(default=0, description="点赞数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class Snippet(SQLModel, table=True):
    """代码片段表"""
    __tablename__ = "snippet"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="片段ID")
    title: str = Field(max_length=200, description="片段标题")
    description: str = Field(description="描述")
    language: str = Field(max_length=50, description="编程语言")
    code: str = Field(description="代码")
    category: str = Field(max_length=50, description="分类")
    tags: Optional[str] = Field(default=None, max_length=500, description="标签")
    usage_count: int = Field(default=0, description="使用次数")
    shortcut: Optional[str] = Field(default=None, max_length=50, description="快捷键")
    author: str = Field(default="系统", max_length=100, description="作者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
