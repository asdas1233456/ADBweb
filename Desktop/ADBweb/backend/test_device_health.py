"""
测试设备健康度功能
"""
import requests
import json


def test_device_health():
    """测试设备健康度"""
    print("=" * 60)
    print("设备健康度监控测试")
    print("=" * 60)
    
    # 1. 测试健康度总览
    print("\n1. 获取健康度总览...")
    response = requests.get("http://localhost:8000/api/v1/device-health/overview")
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ 在线设备数: {len(data['devices'])}")
        print(f"✅ 未解决告警: {data['unresolved_alerts']}")
        
        if data['devices']:
            print("\n   设备健康度:")
            for device in data['devices'][:5]:
                print(f"   - {device['device_name']}: {device['health_score']}分 ({device['level_name']})")
                print(f"     电量: {device['battery_level']}%, 温度: {device['temperature']:.1f}°C")
    
    # 2. 测试单个设备健康度
    print("\n2. 获取设备5的健康度...")
    response = requests.get("http://localhost:8000/api/v1/device-health/devices/5/health")
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ 设备: {data['device_name']}")
        print(f"   健康度: {data['health_score']}分 ({data['level_name']})")
        print(f"   电量: {data['battery_level']}%")
        print(f"   温度: {data['temperature']:.1f}°C")
        print(f"   CPU: {data['cpu_usage']:.1f}%")
        print(f"   内存: {data['memory_usage']:.1f}%")
        print(f"   存储: {data['storage_usage']:.1f}%")
        print(f"   网络: {data['network_status']}")
    
    # 3. 测试告警规则
    print("\n3. 获取告警规则...")
    response = requests.get("http://localhost:8000/api/v1/device-health/alert-rules")
    if response.status_code == 200:
        rules = response.json()['data']
        print(f"✅ 共有 {len(rules)} 条告警规则:")
        for rule in rules:
            status = "✅ 启用" if rule['is_enabled'] else "❌ 禁用"
            print(f"   {status} {rule['rule_name']}: {rule['condition_field']} {rule['operator']} {rule['threshold_value']}")
    
    # 4. 测试告警列表
    print("\n4. 获取告警列表...")
    response = requests.get("http://localhost:8000/api/v1/device-health/alerts")
    if response.status_code == 200:
        alerts = response.json()['data']
        if alerts:
            print(f"✅ 共有 {len(alerts)} 条告警:")
            for alert in alerts[:5]:
                status = "✅ 已解决" if alert['is_resolved'] else "⚠️  未解决"
                print(f"   {status} [{alert['severity']}] {alert['message']}")
        else:
            print("✅ 暂无告警")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_device_health()
