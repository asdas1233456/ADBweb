"""
初始化测试数据脚本
"""
from sqlmodel import Session, select
from app.core.database import engine
from app.models.device import Device
from app.models.script import Script
from app.models.task_log import TaskLog
from datetime import datetime, timedelta
import random

def create_test_devices(session: Session):
    """创建测试设备"""
    test_devices = [
        {
            "serial_number": "emulator-5554",
            "model": "Pixel 6 Pro",
            "android_version": "13",
            "resolution": "1440x3120",
            "battery": 85,
            "cpu_usage": 25.5,
            "memory_usage": 45.2,
            "status": "online"
        },
        {
            "serial_number": "192.168.1.100:5555",
            "model": "小米 13",
            "android_version": "12",
            "resolution": "1080x2400",
            "battery": 92,
            "cpu_usage": 15.3,
            "memory_usage": 38.7,
            "status": "online"
        },
        {
            "serial_number": "HUAWEI_P50_001",
            "model": "华为 P50",
            "android_version": "11",
            "resolution": "1080x2340",
            "battery": 68,
            "cpu_usage": 32.1,
            "memory_usage": 52.4,
            "status": "online"
        },
        {
            "serial_number": "OPPO_FIND_X5_001",
            "model": "OPPO Find X5",
            "android_version": "12",
            "resolution": "1080x2400",
            "battery": 45,
            "cpu_usage": 18.9,
            "memory_usage": 41.3,
            "status": "idle"
        },
        {
            "serial_number": "VIVO_X90_001",
            "model": "vivo X90",
            "android_version": "13",
            "resolution": "1260x2800",
            "battery": 78,
            "cpu_usage": 22.7,
            "memory_usage": 48.6,
            "status": "online"
        }
    ]
    
    added_count = 0
    for device_data in test_devices:
        # 检查是否已存在
        existing = session.exec(
            select(Device).where(Device.serial_number == device_data["serial_number"])
        ).first()
        
        if not existing:
            device = Device(**device_data)
            session.add(device)
            added_count += 1
            print(f"✅ 添加设备: {device_data['model']} ({device_data['serial_number']})")
        else:
            print(f"⏭️  设备已存在: {device_data['model']}")
    
    session.commit()
    print(f"\n📱 共添加 {added_count} 台测试设备")
    return added_count


def create_test_scripts(session: Session):
    """创建测试脚本"""
    test_scripts = [
        {
            "name": "微信登录测试",
            "type": "python",
            "category": "automation",
            "description": "自动化测试微信登录功能",
            "file_content": """#!/usr/bin/env python3
import subprocess
import time

def test_wechat_login():
    # 启动微信
    subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'com.tencent.mm/.ui.LauncherUI'])
    time.sleep(3)
    
    # 点击登录按钮
    subprocess.run(['adb', 'shell', 'input', 'tap', '540', '1200'])
    time.sleep(2)
    
    print("✅ 微信登录测试完成")

if __name__ == '__main__':
    test_wechat_login()
""",
            "is_active": True
        },
        {
            "name": "抖音视频播放测试",
            "type": "python",
            "category": "automation",
            "description": "测试抖音视频播放功能",
            "file_content": """#!/usr/bin/env python3
import subprocess
import time

def test_douyin_play():
    # 启动抖音
    subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'com.ss.android.ugc.aweme/.main.MainActivity'])
    time.sleep(3)
    
    # 点击视频
    subprocess.run(['adb', 'shell', 'input', 'tap', '540', '960'])
    time.sleep(5)
    
    # 上滑切换视频
    subprocess.run(['adb', 'shell', 'input', 'swipe', '540', '1500', '540', '500', '300'])
    time.sleep(2)
    
    print("✅ 抖音播放测试完成")

if __name__ == '__main__':
    test_douyin_play()
""",
            "is_active": True
        },
        {
            "name": "淘宝搜索测试",
            "type": "python",
            "category": "automation",
            "description": "测试淘宝搜索功能",
            "file_content": """#!/usr/bin/env python3
import subprocess
import time

def test_taobao_search():
    # 启动淘宝
    subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'com.taobao.taobao/.MainActivity'])
    time.sleep(3)
    
    # 点击搜索框
    subprocess.run(['adb', 'shell', 'input', 'tap', '540', '200'])
    time.sleep(1)
    
    # 输入搜索内容
    subprocess.run(['adb', 'shell', 'input', 'text', 'iPhone'])
    time.sleep(1)
    
    # 点击搜索按钮
    subprocess.run(['adb', 'shell', 'input', 'tap', '1000', '200'])
    time.sleep(3)
    
    print("✅ 淘宝搜索测试完成")

if __name__ == '__main__':
    test_taobao_search()
""",
            "is_active": True
        },
        {
            "name": "设备信息采集",
            "type": "batch",
            "category": "utility",
            "description": "采集设备基本信息",
            "file_content": """# 获取设备型号
adb shell getprop ro.product.model

# 获取Android版本
adb shell getprop ro.build.version.release

# 获取屏幕分辨率
adb shell wm size

# 获取电池电量
adb shell dumpsys battery | grep level

# 获取内存信息
adb shell dumpsys meminfo

# 获取CPU信息
adb shell cat /proc/cpuinfo
""",
            "is_active": True
        },
        {
            "name": "应用性能监控",
            "type": "python",
            "category": "performance",
            "description": "监控应用CPU和内存使用情况",
            "file_content": """#!/usr/bin/env python3
import subprocess
import time
import re

def monitor_app_performance(package_name, duration=60):
    print(f"开始监控应用: {package_name}")
    print(f"监控时长: {duration}秒")
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # 获取CPU使用率
        cpu_result = subprocess.run(
            ['adb', 'shell', 'dumpsys', 'cpuinfo', '|', 'grep', package_name],
            capture_output=True, text=True
        )
        
        # 获取内存使用
        mem_result = subprocess.run(
            ['adb', 'shell', 'dumpsys', 'meminfo', package_name],
            capture_output=True, text=True
        )
        
        print(f"\\n[{time.strftime('%H:%M:%S')}]")
        print(f"CPU: {cpu_result.stdout.strip()}")
        print(f"Memory: {mem_result.stdout[:200]}...")
        
        time.sleep(10)
    
    print("\\n✅ 性能监控完成")

if __name__ == '__main__':
    monitor_app_performance('com.tencent.mm', 60)
""",
            "is_active": True
        },
        {
            "name": "批量截图",
            "type": "batch",
            "category": "utility",
            "description": "批量截图并保存",
            "file_content": """# 截图脚本
@echo off
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo 开始截图...
adb shell screencap -p /sdcard/screenshot_%TIMESTAMP%.png
adb pull /sdcard/screenshot_%TIMESTAMP%.png ./screenshots/
adb shell rm /sdcard/screenshot_%TIMESTAMP%.png

echo 截图完成: screenshots/screenshot_%TIMESTAMP%.png
""",
            "is_active": True
        },
        {
            "name": "应用安装卸载测试",
            "type": "python",
            "category": "automation",
            "description": "测试应用的安装和卸载",
            "file_content": """#!/usr/bin/env python3
import subprocess
import time

def test_app_install_uninstall(apk_path, package_name):
    print("开始安装测试...")
    
    # 安装应用
    result = subprocess.run(['adb', 'install', apk_path], capture_output=True, text=True)
    if 'Success' in result.stdout:
        print("✅ 应用安装成功")
    else:
        print("❌ 应用安装失败")
        return
    
    time.sleep(2)
    
    # 启动应用
    subprocess.run(['adb', 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'])
    time.sleep(5)
    
    # 卸载应用
    result = subprocess.run(['adb', 'uninstall', package_name], capture_output=True, text=True)
    if 'Success' in result.stdout:
        print("✅ 应用卸载成功")
    else:
        print("❌ 应用卸载失败")
    
    print("\\n✅ 安装卸载测试完成")

if __name__ == '__main__':
    test_app_install_uninstall('test.apk', 'com.example.test')
""",
            "is_active": True
        },
        {
            "name": "网络连接测试",
            "type": "batch",
            "category": "network",
            "description": "测试设备网络连接状态",
            "file_content": """# 网络连接测试
echo 测试网络连接...

# 检查WiFi状态
adb shell dumpsys wifi | grep "Wi-Fi is"

# Ping测试
adb shell ping -c 4 8.8.8.8

# 检查网络接口
adb shell ifconfig

# 检查DNS
adb shell getprop net.dns1

echo 网络测试完成
""",
            "is_active": True
        }
    ]
    
    added_count = 0
    for script_data in test_scripts:
        # 检查是否已存在
        existing = session.exec(
            select(Script).where(Script.name == script_data["name"])
        ).first()
        
        if not existing:
            script = Script(**script_data)
            session.add(script)
            added_count += 1
            print(f"✅ 添加脚本: {script_data['name']}")
        else:
            print(f"⏭️  脚本已存在: {script_data['name']}")
    
    session.commit()
    print(f"\n📝 共添加 {added_count} 个测试脚本")
    return added_count


def create_test_task_logs(session: Session):
    """创建测试任务日志"""
    # 获取设备和脚本
    devices = session.exec(select(Device)).all()
    scripts = session.exec(select(Script)).all()
    
    if not devices or not scripts:
        print("⚠️  没有设备或脚本，跳过任务日志创建")
        return 0
    
    statuses = ["success", "failed", "running"]
    added_count = 0
    
    # 创建最近7天的任务日志
    for i in range(20):
        device = random.choice(devices)
        script = random.choice(scripts)
        status = random.choice(statuses)
        
        # 随机时间（最近7天）
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        # 执行时间（1-300秒）
        execution_time = random.randint(1, 300)
        
        task_log = TaskLog(
            task_name=f"{script.name} - {device.model}",
            device_id=device.id,
            script_id=script.id,
            status=status,
            duration=execution_time,
            log_content=f"测试日志 - {script.name}\n执行时间: {execution_time}秒\n状态: {status}",
            created_at=created_at
        )
        
        session.add(task_log)
        added_count += 1
    
    session.commit()
    print(f"\n📊 共添加 {added_count} 条任务日志")
    return added_count


def main():
    """主函数"""
    print("=" * 60)
    print("开始初始化测试数据...")
    print("=" * 60)
    print()
    
    with Session(engine) as session:
        # 创建测试设备
        print("📱 创建测试设备...")
        print("-" * 60)
        device_count = create_test_devices(session)
        print()
        
        # 创建测试脚本
        print("📝 创建测试脚本...")
        print("-" * 60)
        script_count = create_test_scripts(session)
        print()
        
        # 创建测试任务日志
        print("📊 创建测试任务日志...")
        print("-" * 60)
        log_count = create_test_task_logs(session)
        print()
    
    print("=" * 60)
    print("✅ 测试数据初始化完成！")
    print("=" * 60)
    print(f"📱 设备: {device_count} 台")
    print(f"📝 脚本: {script_count} 个")
    print(f"📊 任务日志: {log_count} 条")
    print()
    print("请刷新浏览器查看数据")


if __name__ == "__main__":
    main()
