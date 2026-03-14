"""
核心配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./test_platform.db"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_SCRIPT_EXTS: str = ".py,.bat"
    ALLOWED_IMAGE_EXTS: str = ".png,.jpg,.jpeg"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 安全与访问控制
    API_AUTH_ENABLED: bool = False
    API_ACCESS_KEY: Optional[str] = None  # 通过Header: X-API-Key 或 Authorization: Bearer 传入
    ENABLE_UPLOADS_STATIC: bool = False
    ENABLE_SCRIPT_EXECUTION: bool = True
    ENABLE_AUTO_PIP_INSTALL: bool = False
    
    # AI API 安全配置
    ALLOWED_AI_API_HOSTS: str = "api.deepseek.com,api.openai.com"
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "手机自动化测试平台"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
