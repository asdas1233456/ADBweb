"""
数据库连接和会话管理
"""
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 生产环境设置为 False
    connect_args={"check_same_thread": False}  # SQLite 需要
)


def create_db_and_tables():
    """创建数据库表"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
        raise


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
