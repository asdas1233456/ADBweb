"""
初始化数据
"""
from sqlmodel import Session, select
from app.models import SystemConfig
import logging

logger = logging.getLogger(__name__)


def init_system_config(db: Session):
    """初始化系统配置"""
    configs = [
        {"config_key": "adb_path", "config_value": "C:\\platform-tools\\adb.exe", "config_type": "string", "description": "ADB工具路径", "is_system": True},
        {"config_key": "python_path", "config_value": "C:\\Python39\\python.exe", "config_type": "string", "description": "Python解释器路径", "is_system": True},
        {"config_key": "auto_connect", "config_value": "true", "config_type": "boolean", "description": "自动连接设备", "is_system": True},
        {"config_key": "auto_refresh", "config_value": "true", "config_type": "boolean", "description": "自动刷新设备列表", "is_system": True},
        {"config_key": "refresh_interval", "config_value": "5", "config_type": "number", "description": "刷新间隔（秒）", "is_system": True},
        {"config_key": "log_level", "config_value": "info", "config_type": "string", "description": "日志级别", "is_system": True},
        {"config_key": "max_log_lines", "config_value": "1000", "config_type": "number", "description": "最大日志行数", "is_system": True},
        {"config_key": "screenshot_quality", "config_value": "high", "config_type": "string", "description": "截图质量", "is_system": True},
        {"config_key": "screenshot_format", "config_value": "png", "config_type": "string", "description": "截图格式", "is_system": True},
        {"config_key": "enable_notification", "config_value": "true", "config_type": "boolean", "description": "启用桌面通知", "is_system": True},
        {"config_key": "enable_sound", "config_value": "false", "config_type": "boolean", "description": "启用提示音", "is_system": True},
    ]
    
    for config_data in configs:
        existing = db.exec(
            select(SystemConfig).where(SystemConfig.config_key == config_data["config_key"])
        ).first()
        
        if not existing:
            config = SystemConfig(**config_data)
            db.add(config)
    
    db.commit()
    logger.info("系统配置初始化完成")


def init_templates(db: Session):
    """初始化模板数据（已废弃）"""
    logger.info("模板数据初始化已跳过（功能已移除）")
