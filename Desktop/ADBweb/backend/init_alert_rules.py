"""
初始化默认告警规则
"""
from app.core.database import engine
from sqlmodel import Session, select
from app.models.device_health import AlertRule
import json


def init_alert_rules():
    """初始化默认告警规则"""
    print("🔧 初始化告警规则...")
    
    default_rules = [
        {
            "rule_name": "低电量告警",
            "rule_type": "low_battery",
            "condition_field": "battery_level",
            "operator": "<",
            "threshold_value": 20.0,
            "severity": "warning",
            "is_enabled": True,
            "notification_channels": json.dumps(["websocket"])
        },
        {
            "rule_name": "高温告警",
            "rule_type": "high_temp",
            "condition_field": "temperature",
            "operator": ">",
            "threshold_value": 45.0,
            "severity": "critical",
            "is_enabled": True,
            "notification_channels": json.dumps(["websocket"])
        },
        {
            "rule_name": "CPU过高告警",
            "rule_type": "high_cpu",
            "condition_field": "cpu_usage",
            "operator": ">",
            "threshold_value": 80.0,
            "severity": "warning",
            "is_enabled": True,
            "notification_channels": json.dumps(["websocket"])
        },
        {
            "rule_name": "内存不足告警",
            "rule_type": "high_memory",
            "condition_field": "memory_usage",
            "operator": ">",
            "threshold_value": 85.0,
            "severity": "warning",
            "is_enabled": True,
            "notification_channels": json.dumps(["websocket"])
        },
        {
            "rule_name": "存储空间不足告警",
            "rule_type": "storage_full",
            "condition_field": "storage_usage",
            "operator": ">",
            "threshold_value": 90.0,
            "severity": "warning",
            "is_enabled": True,
            "notification_channels": json.dumps(["websocket"])
        }
    ]
    
    with Session(engine) as session:
        # 检查是否已存在规则
        existing_rules = session.exec(select(AlertRule)).all()
        if existing_rules:
            print(f"   已存在 {len(existing_rules)} 条规则，跳过初始化")
            return
        
        # 创建默认规则
        for rule_data in default_rules:
            rule = AlertRule(**rule_data)
            session.add(rule)
            print(f"   ✅ 创建规则: {rule.rule_name}")
        
        session.commit()
        print(f"✅ 成功创建 {len(default_rules)} 条告警规则")


if __name__ == "__main__":
    init_alert_rules()
