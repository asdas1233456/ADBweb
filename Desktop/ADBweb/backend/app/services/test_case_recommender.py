"""
测试用例推荐服务
基于设备型号和历史失败数据的协同过滤推荐
"""
from typing import List, Dict
from sqlmodel import Session, select
from app.models.test_case import TestCase


class TestCaseRecommender:
    """测试用例推荐器"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def recommend_by_device(
        self, 
        device_model: str, 
        limit: int = 3
    ) -> List[TestCase]:
        """
        基于设备型号推荐测试用例
        
        推荐策略：
        1. 优先推荐该设备型号历史失败次数最多的用例
        2. 考虑用例优先级（priority越小越重要）
        3. 计算综合得分 = failure_count * 10 + (6 - priority) * 5
        
        Args:
            device_model: 设备型号
            limit: 推荐数量
            
        Returns:
            推荐的测试用例列表
        """
        # 查询该设备型号的所有用例
        statement = select(TestCase).where(TestCase.device_model == device_model)
        test_cases = self.session.exec(statement).all()
        
        if not test_cases:
            # 如果没有该设备的用例，返回通用高优先级用例
            statement = select(TestCase).where(TestCase.priority <= 2).limit(limit)
            return list(self.session.exec(statement).all())
        
        # 计算推荐得分
        scored_cases = []
        for case in test_cases:
            # 综合得分 = 失败次数权重 + 优先级权重
            score = case.failure_count * 10 + (6 - case.priority) * 5
            scored_cases.append((score, case))
        
        # 按得分降序排序
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前N个
        return [case for score, case in scored_cases[:limit]]
    
    def recommend_by_tags(
        self, 
        tags: List[str], 
        limit: int = 5
    ) -> List[TestCase]:
        """
        基于标签推荐测试用例
        
        Args:
            tags: 标签列表
            limit: 推荐数量
            
        Returns:
            推荐的测试用例列表
        """
        # 查询所有用例
        statement = select(TestCase)
        all_cases = self.session.exec(statement).all()
        
        # 计算标签匹配度
        scored_cases = []
        for case in all_cases:
            if not case.tags:
                continue
            
            case_tags = set(tag.strip() for tag in case.tags.split(','))
            input_tags = set(tags)
            
            # 计算交集数量
            match_count = len(case_tags & input_tags)
            if match_count > 0:
                # 得分 = 标签匹配数 * 20 + 失败次数 * 5
                score = match_count * 20 + case.failure_count * 5
                scored_cases.append((score, case))
        
        # 按得分降序排序
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        
        return [case for score, case in scored_cases[:limit]]
    
    def get_statistics(self, device_model: str) -> Dict:
        """
        获取设备的测试统计信息
        
        Args:
            device_model: 设备型号
            
        Returns:
            统计信息字典
        """
        statement = select(TestCase).where(TestCase.device_model == device_model)
        test_cases = self.session.exec(statement).all()
        
        if not test_cases:
            return {
                "total_cases": 0,
                "total_failures": 0,
                "total_successes": 0,
                "avg_failure_rate": 0.0
            }
        
        total_failures = sum(case.failure_count for case in test_cases)
        total_successes = sum(case.success_count for case in test_cases)
        total_executions = total_failures + total_successes
        
        return {
            "total_cases": len(test_cases),
            "total_failures": total_failures,
            "total_successes": total_successes,
            "avg_failure_rate": round(
                total_failures / total_executions * 100 if total_executions > 0 else 0, 
                2
            )
        }
