"""
初始化数据
"""
from sqlmodel import Session, select
from app.models import SystemConfig, Template
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
    """初始化模板数据"""
    templates = [
        {
            "name": "APP启动性能测试",
            "description": "自动测试APP启动时间、内存占用、CPU使用率等性能指标",
            "author": "测试专家",
            "category": "性能测试",
            "type": "python",
            "tags": "性能,启动,监控",
            "content": "import time\\nimport subprocess\\n\\ndef test_app_launch():\\n    pass",
            "preview": "import time\\nimport subprocess",
            "downloads": 1250,
            "rating": 4.8,
            "is_featured": True
        },
        {
            "name": "自动登录模板",
            "description": "通用的登录流程自动化脚本，支持账号密码、验证码识别",
            "author": "自动化大师",
            "category": "功能测试",
            "type": "visual",
            "tags": "登录,自动化,通用",
            "content": '{"steps":[]}',
            "preview": "可视化步骤：点击 → 输入 → 等待 → 验证",
            "downloads": 2100,
            "rating": 4.9,
            "is_featured": True
        },
        {
            "name": "批量截图工具",
            "description": "自动遍历APP所有页面并截图保存，用于UI测试和文档制作",
            "author": "UI测试员",
            "category": "UI测试",
            "type": "python",
            "tags": "截图,UI,批量",
            "content": "def capture_screens():\\n    pass",
            "preview": "def capture_screens():",
            "downloads": 890,
            "rating": 4.6,
            "is_featured": False
        }
    ]
    
    for template_data in templates:
        existing = db.exec(
            select(Template).where(Template.name == template_data["name"])
        ).first()
        
        if not existing:
            template = Template(**template_data)
            db.add(template)
    
    db.commit()
    logger.info("模板数据初始化完成")
