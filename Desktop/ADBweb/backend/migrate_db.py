"""
数据库迁移脚本 - 添加新字段
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, text
from app.core.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """执行数据库迁移"""
    logger.info("开始数据库迁移...")
    
    with Session(engine) as session:
        try:
            # 迁移 device 表
            logger.info("迁移 device 表...")
            
            # 添加 group_name 字段
            try:
                session.exec(text(
                    "ALTER TABLE device ADD COLUMN group_name VARCHAR(100)"
                ))
                logger.info("✓ 添加 device.group_name 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  device.group_name 字段已存在，跳过")
                else:
                    raise
            
            # 添加 cpu_usage 字段
            try:
                session.exec(text(
                    "ALTER TABLE device ADD COLUMN cpu_usage FLOAT DEFAULT 0.0"
                ))
                logger.info("✓ 添加 device.cpu_usage 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  device.cpu_usage 字段已存在，跳过")
                else:
                    raise
            
            # 添加 memory_usage 字段
            try:
                session.exec(text(
                    "ALTER TABLE device ADD COLUMN memory_usage FLOAT DEFAULT 0.0"
                ))
                logger.info("✓ 添加 device.memory_usage 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  device.memory_usage 字段已存在，跳过")
                else:
                    raise
            
            # 迁移 scheduled_task 表
            logger.info("迁移 scheduled_task 表...")
            
            # 添加 cron_expression 字段
            try:
                session.exec(text(
                    "ALTER TABLE scheduled_task ADD COLUMN cron_expression VARCHAR(100)"
                ))
                logger.info("✓ 添加 scheduled_task.cron_expression 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  scheduled_task.cron_expression 字段已存在，跳过")
                else:
                    raise
            
            # 添加 priority 字段
            try:
                session.exec(text(
                    "ALTER TABLE scheduled_task ADD COLUMN priority INTEGER DEFAULT 0"
                ))
                logger.info("✓ 添加 scheduled_task.priority 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  scheduled_task.priority 字段已存在，跳过")
                else:
                    raise
            
            # 添加 retry_count 字段
            try:
                session.exec(text(
                    "ALTER TABLE scheduled_task ADD COLUMN retry_count INTEGER DEFAULT 0"
                ))
                logger.info("✓ 添加 scheduled_task.retry_count 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  scheduled_task.retry_count 字段已存在，跳过")
                else:
                    raise
            
            # 添加 max_retry 字段
            try:
                session.exec(text(
                    "ALTER TABLE scheduled_task ADD COLUMN max_retry INTEGER DEFAULT 3"
                ))
                logger.info("✓ 添加 scheduled_task.max_retry 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  scheduled_task.max_retry 字段已存在，跳过")
                else:
                    raise
            
            # 添加 depends_on 字段
            try:
                session.exec(text(
                    "ALTER TABLE scheduled_task ADD COLUMN depends_on VARCHAR(200)"
                ))
                logger.info("✓ 添加 scheduled_task.depends_on 字段")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("  scheduled_task.depends_on 字段已存在，跳过")
                else:
                    raise
            
            session.commit()
            logger.info("✅ 数据库迁移完成！")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 数据库迁移失败: {e}")
            raise


if __name__ == "__main__":
    migrate_database()
