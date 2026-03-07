"""
测试电池电量获取
"""
from app.services.adb_device_scanner import ADBDeviceScanner

scanner = ADBDeviceScanner()

# 测试获取设备详情
serial = "8X6DGYQOCIAA957L"
print(f"测试设备: {serial}")

# 获取电池电量
battery = scanner._get_battery_level(serial)
print(f"电池电量: {battery}%")

# 获取完整设备信息
details = scanner._get_device_details(serial)
if details:
    print(f"\n完整设备信息:")
    for key, value in details.items():
        print(f"  {key}: {value}")
else:
    print("获取设备详情失败")
