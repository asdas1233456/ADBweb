"""
生成设备健康度测试数据
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.device import Device
from app.models.device_health import DeviceHealthRecord
from datetime import datetime
import random

def generate_health_data():
    """为所有设备生成健康度数据"""
    with Session(engine) as db:
        # 获取所有设备
        devices = db.exec(select(Device)).all()
        
        if not devices:
            print("❌ 没有找到设备，请先创建设备")
            return
        
        print(f"📊 为 {len(devices)} 个设备生成健康度数据...")
        
        for device in devices:
            # 生成健康度记录
            health_record = DeviceHealthRecord(
                device_id=device.id,
                health_score=random.randint(60, 100),  # 60-100分
                battery_level=device.battery or random.randint(20, 100),
                temperature=random.uniform(30, 45),  # 30-45度
                cpu_usage=random.uniform(10, 80),  # 10-80%
                memory_usage=random.uniform(30, 85),  # 30-85%
                storage_usage=random.uniform(40, 90),  # 40-90%
                network_status="connected",
                created_at=datetime.now()
            )
            
            db.add(health_record)
            print(f"  ✅ {device.model}: 健康度 {health_record.health_score}分")
        
        db.commit()
        print(f"\n✅ 成功生成 {len(devices)} 条健康度记录")

if __name__ == "__main__":
    generate_health_data()
