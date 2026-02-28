"""
AI生成脚本模型
"""
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class AIScript(SQLModel, table=True):
    """AI生成脚本记录表"""
    __tablename__ = "ai_scripts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str = Field(description="用户输入的自然语言描述")
    generated_script: str = Field(description="生成的脚本内容")
    language: str = Field(default="python", description="脚本语言")
    optimization_suggestions: Optional[str] = Field(default=None, description="优化建议JSON")
    device_model: Optional[str] = Field(default=None, max_length=100, description="目标设备型号")
    status: str = Field(default="success", description="生成状态: success/failed")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "测试微信登录功能",
                "generated_script": "adb shell input tap 500 1000",
                "language": "adb",
                "device_model": "小米14"
            }
        }
