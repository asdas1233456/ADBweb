"""
测试ADB设备扫描器
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.adb_device_scanner import ADBDeviceScanner


def test_scanner():
    """测试扫描器"""
    print("="*80)
    print("ADB设备扫描器测试")
    print("="*80)
    
    # 创建扫描器（使用系统PATH中的adb）
    scanner = ADBDeviceScanner()
    
    print("\n正在扫描ADB设备...")
    devices = scanner.scan_devices()
    
    if not devices:
        print("\n❌ 未发现任何设备")
        print("\n请检查:")
        print("1. ADB是否已安装并在系统PATH中")
        print("2. 设备是否通过USB连接")
        print("3. 设备是否开启USB调试")
        print("4. 设备是否已授权电脑调试")
        return
    
    print(f"\n✅ 发现 {len(devices)} 台设备:\n")
    
    for i, device in enumerate(devices, 1):
        print(f"设备 {i}:")
        print(f"  序列号: {device['serial_number']}")
        print(f"  型号: {device['model']}")
        print(f"  Android版本: {device['android_version']}")
        print(f"  分辨率: {device['resolution']}")
        print(f"  电量: {device['battery']}%")
        print(f"  CPU使用率: {device['cpu_usage']}%")
        print(f"  内存使用率: {device['memory_usage']}%")
        print(f"  状态: {device['status']}")
        print()


if __name__ == "__main__":
    test_scanner()
