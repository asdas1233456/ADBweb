"""
通用响应模型
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# 别名，保持兼容性
PaginatedResponse = PageResponse
