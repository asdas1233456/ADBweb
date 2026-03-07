"""
修复ADB路径配置
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.system_config import SystemConfig

def fix_adb_path():
    """修复ADB路径"""
    with Session(engine) as session:
        # 查找ADB路径配置
        config = session.exec(
            select(SystemConfig).where(SystemConfig.config_key == "adb_path")
        ).first()
        
        if config:
            old_path = config.config_value
            # 使用系统PATH中的adb（不指定完整路径）
            config.config_value = "adb"
            session.add(config)
            session.commit()
            print(f"✅ ADB路径已更新")
            print(f"   旧路径: {old_path}")
            print(f"   新路径: adb (使用系统PATH)")
        else:
            # 创建新配置
            new_config = SystemConfig(
                config_key="adb_path",
                config_value="adb",
                description="ADB可执行文件路径"
            )
            session.add(new_config)
            session.commit()
            print("✅ 已创建ADB路径配置: adb (使用系统PATH)")

if __name__ == "__main__":
    fix_adb_path()
