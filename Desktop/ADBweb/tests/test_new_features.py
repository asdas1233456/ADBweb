"""
测试新实现的功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.device_health import AlertRule
from app.models.device import Device
from app.models.script import Script


class TestBatchDeviceOperations:
    """测试批量设备操作"""
    
    def test_batch_execute_success(self, client: TestClient, db: Session):
        """测试批量执行脚本成功"""
        # 创建测试设备
        device1 = Device(
            serial_number="test_device_1",
            model="Test Model 1",
            android_version="11",
            status="online"
        )
        device2 = Device(
            serial_number="test_device_2",
            model="Test Model 2",
            android_version="12",
            status="online"
        )
        db.add(device1)
        db.add(device2)
        db.commit()
        db.refresh(device1)
        db.refresh(device2)
        
        # 创建测试脚本
        script = Script(
            name="Test Script",
            type="python",
            category="test",
            file_content="print('test')"
        )
        db.add(script)
        db.commit()
        db.refresh(script)
        
        # 批量执行
        response = client.post(
            "/api/v1/devices/batch/execute",
            json={
                "device_ids": [device1.id, device2.id],
                "script_id": script.id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["message"]
    
    def test_batch_execute_empty_devices(self, client: TestClient):
        """测试批量执行时设备列表为空"""
        response = client.post(
            "/api/v1/devices/batch/execute",
            json={
                "device_ids": [],
                "script_id": 1
            }
        )
        
        assert response.status_code == 400
    
    def test_batch_execute_invalid_script(self, client: TestClient, db: Session):
        """测试批量执行时脚本不存在"""
        device = Device(
            serial_number="test_device",
            model="Test Model",
            android_version="11",
            status="online"
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        
        response = client.post(
            "/api/v1/devices/batch/execute",
            json={
                "device_ids": [device.id],
                "script_id": 99999
            }
        )
        
        assert response.status_code == 404


class TestAlertRuleCRUD:
    """测试告警规则CRUD操作"""
    
    def test_create_alert_rule(self, client: TestClient):
        """测试创建告警规则"""
        response = client.post(
            "/api/v1/device-health/alert-rules",
            params={
                "rule_name": "低电量告警",
                "rule_type": "battery",
                "condition_field": "battery_level",
                "operator": "<",
                "threshold_value": 20,
                "severity": "high",
                "is_enabled": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["rule_name"] == "低电量告警"
        assert data["data"]["threshold_value"] == 20
    
    def test_get_alert_rules(self, client: TestClient, db: Session):
        """测试获取告警规则列表"""
        # 创建测试规则
        rule = AlertRule(
            rule_name="测试规则",
            rule_type="temperature",
            condition_field="temperature",
            operator=">",
            threshold_value=45,
            severity="critical",
            is_enabled=True
        )
        db.add(rule)
        db.commit()
        
        response = client.get("/api/v1/device-health/alert-rules")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]) > 0
    
    def test_update_alert_rule(self, client: TestClient, db: Session):
        """测试更新告警规则"""
        # 创建测试规则
        rule = AlertRule(
            rule_name="原规则名",
            rule_type="cpu_usage",
            condition_field="cpu_usage",
            operator=">",
            threshold_value=80,
            severity="medium",
            is_enabled=True
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        # 更新规则
        response = client.put(
            f"/api/v1/device-health/alert-rules/{rule.id}",
            params={
                "rule_name": "新规则名",
                "threshold_value": 90
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["rule_name"] == "新规则名"
        assert data["data"]["threshold_value"] == 90
    
    def test_toggle_alert_rule(self, client: TestClient, db: Session):
        """测试切换告警规则状态"""
        # 创建测试规则
        rule = AlertRule(
            rule_name="测试规则",
            rule_type="memory_usage",
            condition_field="memory_usage",
            operator=">",
            threshold_value=85,
            severity="high",
            is_enabled=True
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        # 禁用规则
        response = client.put(
            f"/api/v1/device-health/alert-rules/{rule.id}/toggle",
            params={"is_enabled": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["is_enabled"] is False
    
    def test_delete_alert_rule(self, client: TestClient, db: Session):
        """测试删除告警规则"""
        # 创建测试规则
        rule = AlertRule(
            rule_name="待删除规则",
            rule_type="health_score",
            condition_field="health_score",
            operator="<",
            threshold_value=60,
            severity="low",
            is_enabled=True
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        rule_id = rule.id
        
        # 删除规则
        response = client.delete(f"/api/v1/device-health/alert-rules/{rule_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        
        # 验证规则已删除
        deleted_rule = db.get(AlertRule, rule_id)
        assert deleted_rule is None
    
    def test_delete_nonexistent_rule(self, client: TestClient):
        """测试删除不存在的规则"""
        response = client.delete("/api/v1/device-health/alert-rules/99999")
        
        assert response.status_code == 404


class TestDeviceHealthAPI:
    """测试设备健康度API"""
    
    def test_get_device_health_overview(self, client: TestClient):
        """测试获取健康度总览"""
        response = client.get("/api/v1/device-health/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "devices" in data["data"]
        assert "unresolved_alerts" in data["data"]
    
    def test_get_device_health_history(self, client: TestClient, db: Session):
        """测试获取设备健康度历史"""
        # 创建测试设备
        device = Device(
            serial_number="test_device",
            model="Test Model",
            android_version="11",
            status="online"
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        
        response = client.get(
            f"/api/v1/device-health/devices/{device.id}/history",
            params={"hours": 24}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "records" in data["data"]


class TestFailureAnalysisAPI:
    """测试失败分析API"""
    
    def test_get_failure_overview(self, client: TestClient):
        """测试获取失败分析总览"""
        response = client.get(
            "/api/v1/failure-analysis/overview",
            params={"days": 7}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total_failures" in data["data"]
        assert "failure_by_type" in data["data"]
    
    def test_get_failure_trend(self, client: TestClient):
        """测试获取失败趋势"""
        response = client.get(
            "/api/v1/failure-analysis/trend",
            params={"range": "week"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total_failures" in data["data"]
        assert "failure_by_type" in data["data"]


class TestReportAPI:
    """测试报告API"""
    
    def test_delete_report(self, client: TestClient, db: Session):
        """测试删除报告"""
        from app.models.task_log import TaskLog
        from datetime import datetime
        
        # 创建测试设备和脚本
        device = Device(
            serial_number="test_device",
            model="Test Model",
            android_version="11",
            status="online"
        )
        script = Script(
            name="Test Script",
            type="python",
            category="test",
            file_content="print('test')"
        )
        db.add(device)
        db.add(script)
        db.commit()
        db.refresh(device)
        db.refresh(script)
        
        # 创建测试报告
        task_log = TaskLog(
            task_name="Test Task",
            script_id=script.id,
            device_id=device.id,
            status="success",
            start_time=datetime.now()
        )
        db.add(task_log)
        db.commit()
        db.refresh(task_log)
        task_log_id = task_log.id
        
        # 删除报告
        response = client.delete(f"/api/v1/reports/{task_log_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        
        # 验证报告已删除
        deleted_log = db.get(TaskLog, task_log_id)
        assert deleted_log is None


class TestExampleAPI:
    """测试示例库API"""
    
    def test_get_examples(self, client: TestClient):
        """测试获取示例列表"""
        response = client.get(
            "/api/v1/examples",
            params={"page": 1, "page_size": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
    
    def test_get_best_practices(self, client: TestClient):
        """测试获取最佳实践列表"""
        response = client.get(
            "/api/v1/examples/practices/list",
            params={"page": 1, "page_size": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
    
    def test_get_snippets(self, client: TestClient):
        """测试获取代码片段列表"""
        response = client.get(
            "/api/v1/examples/snippets/list",
            params={"page": 1, "page_size": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]


class TestActivityLogAPI:
    """测试活动日志API"""
    
    def test_get_activity_logs(self, client: TestClient):
        """测试获取活动日志"""
        response = client.get(
            "/api/v1/activity-logs",
            params={"limit": 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
    
    def test_filter_activity_logs_by_type(self, client: TestClient):
        """测试按类型筛选活动日志"""
        response = client.get(
            "/api/v1/activity-logs",
            params={
                "activity_type": "device_connect",
                "limit": 50
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
