"""
测试失败场景 - 创建一个会失败的任务来测试失败分析功能
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def create_failing_script():
    """创建一个会失败的测试脚本"""
    print("📝 创建失败测试脚本...")
    
    # 创建一个包含错误的脚本
    script_data = {
        "name": "失败测试脚本",
        "description": "用于测试失败分析功能的脚本",
        "category": "测试",
        "steps_json": json.dumps([
            {
                "name": "启动应用",
                "type": "launch_app",
                "config": {"package": "com.example.app"}
            },
            {
                "name": "点击登录按钮",
                "type": "click",
                "config": {"selector": "不存在的元素"}  # 这会导致失败
            },
            {
                "name": "输入用户名",
                "type": "input",
                "config": {"selector": "username", "text": "test"}
            }
        ]),
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/scripts", json=script_data)
    
    if response.status_code == 200:
        script = response.json()["data"]
        print(f"✅ 脚本已创建: ID={script['id']}")
        return script["id"]
    else:
        print(f"❌ 创建脚本失败: {response.text}")
        return None

def execute_failing_task(script_id, device_id):
    """执行会失败的任务"""
    print(f"\n🚀 执行失败测试任务...")
    
    task_data = {
        "task_name": "失败分析功能测试",
        "script_id": script_id,
        "device_id": device_id
    }
    
    response = requests.post(f"{BASE_URL}/tasks/execute", json=task_data)
    
    if response.status_code == 200:
        result = response.json()
        task_log_id = result["data"]["task_log_id"]
        print(f"✅ 任务已创建: ID={task_log_id}")
        return task_log_id
    else:
        print(f"❌ 任务创建失败: {response.text}")
        return None

def wait_for_task(task_log_id, max_wait=30):
    """等待任务完成"""
    print(f"\n⏳ 等待任务完成...")
    
    waited = 0
    while waited < max_wait:
        response = requests.get(f"{BASE_URL}/tasks/{task_log_id}/logs")
        
        if response.status_code == 200:
            task_log = response.json()["data"]
            status = task_log["status"]
            
            if status in ["success", "failed"]:
                print(f"✅ 任务已完成: {status}")
                return status
            
            print(f"   状态: {status} (已等待 {waited}秒)")
        
        time.sleep(2)
        waited += 2
    
    print("⚠️ 等待超时")
    return None

def check_failure_analysis(task_log_id):
    """检查失败分析结果"""
    print(f"\n🔍 检查失败分析...")
    
    # 等待一下，让分析完成
    time.sleep(2)
    
    response = requests.get(f"{BASE_URL}/failure-analysis/tasks/{task_log_id}")
    
    if response.status_code == 200:
        analysis = response.json()["data"]
        
        print("\n" + "="*60)
        print("📊 失败分析结果")
        print("="*60)
        print(f"失败类型: {analysis['failure_type']} {analysis.get('failure_icon', '')}")
        print(f"严重程度: {analysis['severity']}")
        print(f"失败步骤: 第 {analysis['failed_step_index']} 步")
        print(f"步骤名称: {analysis['failed_step_name']}")
        print(f"错误信息: {analysis['error_message']}")
        print(f"置信度: {analysis['confidence']}%")
        
        if analysis.get('suggestions'):
            print(f"\n💡 解决建议:")
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                print(f"  {i}. {suggestion}")
        
        if analysis.get('screenshot_path'):
            print(f"\n📸 失败截图: {analysis['screenshot_path']}")
        
        print(f"\n⏰ 分析时间: {analysis['created_at']}")
        print("="*60)
        
        return True
    else:
        print(f"❌ 未找到失败分析: {response.text}")
        return False

def main():
    """主流程"""
    print("\n" + "🎯 失败分析功能完整测试")
    print("="*60)
    
    # 1. 获取一个在线设备
    print("\n1️⃣ 获取测试设备...")
    devices_resp = requests.get(f"{BASE_URL}/devices")
    
    if devices_resp.status_code != 200:
        print("❌ 无法获取设备列表")
        return
    
    devices_data = devices_resp.json()
    devices = devices_data.get("data", devices_data)
    if isinstance(devices, dict):
        devices = devices.get("items", [])
    
    online_devices = [d for d in devices if d.get("status") == "online"]
    
    if not online_devices:
        print("❌ 没有在线设备")
        return
    
    device = online_devices[0]
    device_id = device.get("id")
    print(f"✅ 使用设备: ID={device_id}")
    
    # 2. 创建会失败的脚本
    print("\n2️⃣ 创建失败测试脚本...")
    script_id = create_failing_script()
    
    if not script_id:
        print("❌ 无法创建脚本")
        return
    
    # 3. 执行任务
    print("\n3️⃣ 执行任务...")
    task_log_id = execute_failing_task(script_id, device_id)
    
    if not task_log_id:
        print("❌ 无法创建任务")
        return
    
    # 4. 等待任务完成
    print("\n4️⃣ 等待任务完成...")
    status = wait_for_task(task_log_id)
    
    if status == "failed":
        print("✅ 任务按预期失败")
    else:
        print(f"⚠️ 任务状态: {status}")
    
    # 5. 检查失败分析
    print("\n5️⃣ 检查失败分析...")
    if check_failure_analysis(task_log_id):
        print("\n✅ 失败分析功能正常工作！")
    else:
        print("\n⚠️ 失败分析未生成")
    
    # 6. 查看统计
    print("\n6️⃣ 查看失败统计...")
    stats_resp = requests.get(f"{BASE_URL}/failure-analysis/scripts/{script_id}/stats")
    if stats_resp.status_code == 200:
        stats = stats_resp.json()["data"]
        print(f"   总失败次数: {stats['total_failures']}")
        if stats.get('failure_by_type'):
            print(f"   失败类型: {list(stats['failure_by_type'].keys())}")
    
    print("\n" + "="*60)
    print("🎉 测试完成！")
    print("="*60)

if __name__ == "__main__":
    main()
