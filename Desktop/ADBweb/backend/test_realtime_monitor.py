"""
测试实时任务监控功能
"""
import asyncio
import requests
import json
from datetime import datetime


async def test_realtime_monitor():
    """测试实时监控"""
    print("=" * 60)
    print("实时任务监控测试")
    print("=" * 60)
    
    # 1. 创建测试任务
    print("\n1. 创建测试任务...")
    task_data = {
        "task_name": "实时监控测试任务",
        "script_id": 1,
        "device_id": 5  # 使用在线设备
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/tasks/execute",
            json=task_data,
            timeout=10
        )
        result = response.json()
        
        if result.get("code") == 200:
            task_id = result["data"]["task_log_id"]
            print(f"✅ 任务创建成功! Task ID: {task_id}")
            print(f"   状态: {result['data']['status']}")
            
            # 2. 等待任务执行
            print(f"\n2. 任务正在执行...")
            print(f"   提示: 请在浏览器中访问 http://localhost:5173/realtime-test")
            print(f"   查看实时监控效果")
            
            # 等待一段时间让任务执行
            await asyncio.sleep(15)
            
            # 3. 查询任务状态
            print(f"\n3. 查询任务最终状态...")
            response = requests.get(
                f"http://localhost:8000/api/v1/tasks/{task_id}/logs",
                timeout=10
            )
            result = response.json()
            
            if result.get("code") == 200:
                task_log = result["data"]
                print(f"✅ 任务状态: {task_log.get('status')}")
                print(f"   开始时间: {task_log.get('start_time')}")
                print(f"   结束时间: {task_log.get('end_time')}")
                print(f"   执行时长: {task_log.get('duration')}秒")
            else:
                print(f"❌ 查询失败: {result.get('message')}")
        else:
            print(f"❌ 任务创建失败: {result.get('message')}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_realtime_monitor())
