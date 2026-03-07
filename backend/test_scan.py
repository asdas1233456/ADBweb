"""
测试设备扫描
"""
from sqlmodel import Session
from app.core.database import engine
from app.services.adb_device_scanner import scan_and_add_devices

def test_scan():
    """测试扫描"""
    with Session(engine) as session:
        print("开始扫描设备...")
        result = scan_and_add_devices(session, adb_path="adb")
        print(f"扫描结果: {result}")

if __name__ == "__main__":
    test_scan()
