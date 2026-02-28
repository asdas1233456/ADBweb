"""
测试用例推荐API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_session
from app.models.test_case import TestCase
from app.services.test_case_recommender import TestCaseRecommender
from app.schemas.common import Response

router = APIRouter(prefix="/test-case", tags=["测试用例"])


class TestCaseResponse(BaseModel):
    """测试用例响应"""
    id: int
    name: str
    description: Optional[str]
    device_model: str
    priority: int
    failure_count: int
    success_count: int
    script_template: Optional[str]
    tags: Optional[str]
    failure_rate: float  # 失败率


class RecommendResponse(BaseModel):
    """推荐响应"""
    recommendations: List[TestCaseResponse]
    statistics: dict


@router.get("/recommend", response_model=Response[RecommendResponse])
async def recommend_test_cases(
    device_model: str = Query(..., description="设备型号"),
    limit: int = Query(3, description="推荐数量"),
    session: Session = Depends(get_session)
):
    """
    推荐测试用例
    
    基于设备型号和历史失败数据推荐高优先级测试用例
    """
    recommender = TestCaseRecommender(session)
    
    # 获取推荐用例
    recommended_cases = recommender.recommend_by_device(device_model, limit)
    
    # 获取统计信息
    statistics = recommender.get_statistics(device_model)
    
    # 构建响应
    recommendations = []
    for case in recommended_cases:
        total = case.failure_count + case.success_count
        failure_rate = round(case.failure_count / total * 100 if total > 0 else 0, 2)
        
        recommendations.append(TestCaseResponse(
            id=case.id,
            name=case.name,
            description=case.description,
            device_model=case.device_model,
            priority=case.priority,
            failure_count=case.failure_count,
            success_count=case.success_count,
            script_template=case.script_template,
            tags=case.tags,
            failure_rate=failure_rate
        ))
    
    result = RecommendResponse(
        recommendations=recommendations,
        statistics=statistics
    )
    
    return Response(data=result)


@router.get("/list", response_model=Response[List[TestCaseResponse]])
async def list_test_cases(
    device_model: Optional[str] = None,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """
    获取测试用例列表
    """
    statement = select(TestCase)
    if device_model:
        statement = statement.where(TestCase.device_model == device_model)
    statement = statement.limit(limit)
    
    cases = session.exec(statement).all()
    
    result = []
    for case in cases:
        total = case.failure_count + case.success_count
        failure_rate = round(case.failure_count / total * 100 if total > 0 else 0, 2)
        
        result.append(TestCaseResponse(
            id=case.id,
            name=case.name,
            description=case.description,
            device_model=case.device_model,
            priority=case.priority,
            failure_count=case.failure_count,
            success_count=case.success_count,
            script_template=case.script_template,
            tags=case.tags,
            failure_rate=failure_rate
        ))
    
    return Response(data=result)


@router.post("/create", response_model=Response[TestCaseResponse])
async def create_test_case(
    case: TestCase,
    session: Session = Depends(get_session)
):
    """创建测试用例"""
    session.add(case)
    session.commit()
    session.refresh(case)
    
    total = case.failure_count + case.success_count
    failure_rate = round(case.failure_count / total * 100 if total > 0 else 0, 2)
    
    result = TestCaseResponse(
        id=case.id,
        name=case.name,
        description=case.description,
        device_model=case.device_model,
        priority=case.priority,
        failure_count=case.failure_count,
        success_count=case.success_count,
        script_template=case.script_template,
        tags=case.tags,
        failure_rate=failure_rate
    )
    
    return Response(data=result)


@router.get("/devices", response_model=Response[List[str]])
async def get_device_models(
    session: Session = Depends(get_session)
):
    """获取所有设备型号列表"""
    statement = select(TestCase.device_model).distinct()
    models = session.exec(statement).all()
    return Response(data=list(models))
