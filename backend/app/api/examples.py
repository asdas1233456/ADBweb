"""
示例库 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_session
from app.models.example import Example, BestPractice, Snippet
from app.schemas.example import (
    ExampleCreate, ExampleUpdate, ExampleResponse,
    BestPracticeCreate, BestPracticeUpdate, BestPracticeResponse,
    SnippetCreate, SnippetUpdate, SnippetResponse
)

router = APIRouter(prefix="/examples", tags=["示例库"])


# ==================== 示例脚本 API ====================

@router.get("", response_model=dict)
async def get_examples(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    script_type: Optional[str] = Query(None, description="脚本类型筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    is_featured: Optional[bool] = Query(None, description="是否精选"),
    session: Session = Depends(get_session)
):
    """获取示例列表"""
    query = select(Example)
    
    # 筛选条件
    if category:
        query = query.where(Example.category == category)
    if difficulty:
        query = query.where(Example.difficulty == difficulty)
    if script_type:
        query = query.where(Example.script_type == script_type)
    if is_featured is not None:
        query = query.where(Example.is_featured == is_featured)
    if keyword:
        query = query.where(
            (Example.title.contains(keyword)) |
            (Example.description.contains(keyword)) |
            (Example.tags.contains(keyword))
        )
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total = session.exec(total_query).one()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Example.is_featured.desc(), Example.download_count.desc())
    
    examples = session.exec(query).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": examples,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/categories/list", response_model=dict)
async def get_example_categories(
    session: Session = Depends(get_session)
):
    """获取示例分类列表"""
    query = select(Example.category, func.count(Example.id).label('count')).group_by(Example.category)
    results = session.exec(query).all()
    
    categories = [{"name": cat, "count": count} for cat, count in results]
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": categories
    }


@router.get("/categories", response_model=dict)
async def get_categories(
    session: Session = Depends(get_session)
):
    """获取示例分类列表（别名接口）"""
    query = select(Example.category, func.count(Example.id).label('count')).group_by(Example.category)
    results = session.exec(query).all()
    
    categories = [{"name": cat, "count": count} for cat, count in results]
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": categories
    }


@router.get("/{example_id}", response_model=dict)
async def get_example(
    example_id: int,
    session: Session = Depends(get_session)
):
    """获取示例详情"""
    example = session.get(Example, example_id)
    if not example:
        raise HTTPException(status_code=404, detail="示例不存在")
    
    # 增加浏览次数
    example.view_count += 1
    session.add(example)
    session.commit()
    session.refresh(example)
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": example
    }


@router.post("", response_model=dict)
async def create_example(
    example: ExampleCreate,
    session: Session = Depends(get_session)
):
    """创建示例"""
    db_example = Example(**example.model_dump())
    session.add(db_example)
    session.commit()
    session.refresh(db_example)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": db_example
    }


@router.put("/{example_id}", response_model=dict)
async def update_example(
    example_id: int,
    example: ExampleUpdate,
    session: Session = Depends(get_session)
):
    """更新示例"""
    db_example = session.get(Example, example_id)
    if not db_example:
        raise HTTPException(status_code=404, detail="示例不存在")
    
    update_data = example.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_example, key, value)
    
    db_example.updated_at = datetime.now()
    session.add(db_example)
    session.commit()
    session.refresh(db_example)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": db_example
    }


@router.delete("/{example_id}", response_model=dict)
async def delete_example(
    example_id: int,
    session: Session = Depends(get_session)
):
    """删除示例"""
    example = session.get(Example, example_id)
    if not example:
        raise HTTPException(status_code=404, detail="示例不存在")
    
    session.delete(example)
    session.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.post("/{example_id}/download", response_model=dict)
async def download_example(
    example_id: int,
    session: Session = Depends(get_session)
):
    """下载示例（增加下载次数）"""
    example = session.get(Example, example_id)
    if not example:
        raise HTTPException(status_code=404, detail="示例不存在")
    
    example.download_count += 1
    session.add(example)
    session.commit()
    session.refresh(example)
    
    return {
        "code": 200,
        "message": "下载成功",
        "data": example
    }


# ==================== 最佳实践 API ====================

@router.get("/practices/list", response_model=dict)
async def get_best_practices(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    session: Session = Depends(get_session)
):
    """获取最佳实践列表"""
    query = select(BestPractice)
    
    # 筛选条件
    if category:
        query = query.where(BestPractice.category == category)
    if difficulty:
        query = query.where(BestPractice.difficulty == difficulty)
    if keyword:
        query = query.where(
            (BestPractice.title.contains(keyword)) |
            (BestPractice.content.contains(keyword)) |
            (BestPractice.tags.contains(keyword))
        )
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total = session.exec(total_query).one()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(BestPractice.like_count.desc())
    
    practices = session.exec(query).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": practices,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/practices/{practice_id}", response_model=dict)
async def get_best_practice(
    practice_id: int,
    session: Session = Depends(get_session)
):
    """获取最佳实践详情"""
    practice = session.get(BestPractice, practice_id)
    if not practice:
        raise HTTPException(status_code=404, detail="最佳实践不存在")
    
    # 增加浏览次数
    practice.view_count += 1
    session.add(practice)
    session.commit()
    session.refresh(practice)
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": practice
    }


@router.post("/practices", response_model=dict)
async def create_best_practice(
    practice: BestPracticeCreate,
    session: Session = Depends(get_session)
):
    """创建最佳实践"""
    db_practice = BestPractice(**practice.model_dump())
    session.add(db_practice)
    session.commit()
    session.refresh(db_practice)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": db_practice
    }


@router.post("/practices/{practice_id}/like", response_model=dict)
async def like_best_practice(
    practice_id: int,
    session: Session = Depends(get_session)
):
    """点赞最佳实践"""
    practice = session.get(BestPractice, practice_id)
    if not practice:
        raise HTTPException(status_code=404, detail="最佳实践不存在")
    
    practice.like_count += 1
    session.add(practice)
    session.commit()
    session.refresh(practice)
    
    return {
        "code": 200,
        "message": "点赞成功",
        "data": practice
    }


# ==================== 代码片段 API ====================

@router.get("/snippets/list", response_model=dict)
async def get_snippets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    language: Optional[str] = Query(None, description="语言筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    session: Session = Depends(get_session)
):
    """获取代码片段列表"""
    query = select(Snippet)
    
    # 筛选条件
    if category:
        query = query.where(Snippet.category == category)
    if language:
        query = query.where(Snippet.language == language)
    if keyword:
        query = query.where(
            (Snippet.title.contains(keyword)) |
            (Snippet.description.contains(keyword)) |
            (Snippet.tags.contains(keyword))
        )
    
    # 总数
    total_query = select(func.count()).select_from(query.subquery())
    total = session.exec(total_query).one()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Snippet.usage_count.desc())
    
    snippets = session.exec(query).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": snippets,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/snippets/{snippet_id}", response_model=dict)
async def get_snippet(
    snippet_id: int,
    session: Session = Depends(get_session)
):
    """获取代码片段详情"""
    snippet = session.get(Snippet, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="代码片段不存在")
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": snippet
    }


@router.post("/snippets", response_model=dict)
async def create_snippet(
    snippet: SnippetCreate,
    session: Session = Depends(get_session)
):
    """创建代码片段"""
    db_snippet = Snippet(**snippet.model_dump())
    session.add(db_snippet)
    session.commit()
    session.refresh(db_snippet)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": db_snippet
    }


@router.post("/snippets/{snippet_id}/use", response_model=dict)
async def use_snippet(
    snippet_id: int,
    session: Session = Depends(get_session)
):
    """使用代码片段（增加使用次数）"""
    snippet = session.get(Snippet, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="代码片段不存在")
    
    snippet.usage_count += 1
    session.add(snippet)
    session.commit()
    session.refresh(snippet)
    
    return {
        "code": 200,
        "message": "使用成功",
        "data": snippet
    }
