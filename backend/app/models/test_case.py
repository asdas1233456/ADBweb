"""
测试用例模型
"""
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class TestCase(SQLModel, table=True):
    """测试用例表"""
    __tablename__ = "test_cases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, description="用例名称")
    description: Optional[str] = Field(default=None, description="用例描述")
    device_model: str = Field(max_length=100, description="适用设备型号")
    priority: int = Field(default=3, description="优先级 1-5，1最高")
    failure_count: int = Field(default=0, description="历史失败次数")
    success_count: int = Field(default=0, description="历史成功次数")
    script_template: Optional[str] = Field(default=None, description="脚本模板")
    tags: Optional[str] = Field(default=None, description="标签，逗号分隔")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "微信登录测试",
                "description": "测试微信应用的登录功能",
                "device_model": "小米14",
                "priority": 1,
                "failure_count": 5,
                "success_count": 20,
                "tags": "登录,微信,核心功能"
            }
        }
