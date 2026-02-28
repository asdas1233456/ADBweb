"""
示例库 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExampleBase(BaseModel):
    """示例基础模型"""
    title: str
    description: str
    category: str
    difficulty: str = "beginner"
    script_type: str
    code: str
    tags: Optional[str] = None
    use_case: Optional[str] = None
    prerequisites: Optional[str] = None
    expected_result: Optional[str] = None
    author: str = "系统"


class ExampleCreate(ExampleBase):
    """创建示例"""
    pass


class ExampleUpdate(BaseModel):
    """更新示例"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    script_type: Optional[str] = None
    code: Optional[str] = None
    tags: Optional[str] = None
    use_case: Optional[str] = None
    prerequisites: Optional[str] = None
    expected_result: Optional[str] = None


class ExampleResponse(ExampleBase):
    """示例响应"""
    id: int
    rating: float
    download_count: int
    view_count: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BestPracticeBase(BaseModel):
    """最佳实践基础模型"""
    title: str
    category: str
    content: str
    code_examples: Optional[str] = None
    dos: Optional[str] = None
    donts: Optional[str] = None
    tips: Optional[str] = None
    difficulty: str = "beginner"
    tags: Optional[str] = None
    author: str = "系统"


class BestPracticeCreate(BestPracticeBase):
    """创建最佳实践"""
    pass


class BestPracticeUpdate(BaseModel):
    """更新最佳实践"""
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    code_examples: Optional[str] = None
    dos: Optional[str] = None
    donts: Optional[str] = None
    tips: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[str] = None


class BestPracticeResponse(BestPracticeBase):
    """最佳实践响应"""
    id: int
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SnippetBase(BaseModel):
    """代码片段基础模型"""
    title: str
    description: str
    language: str
    code: str
    category: str
    tags: Optional[str] = None
    shortcut: Optional[str] = None
    author: str = "系统"


class SnippetCreate(SnippetBase):
    """创建代码片段"""
    pass


class SnippetUpdate(BaseModel):
    """更新代码片段"""
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    shortcut: Optional[str] = None


class SnippetResponse(SnippetBase):
    """代码片段响应"""
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
