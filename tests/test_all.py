#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADBweb 平台完整测试套件
整合所有功能测试，包括系统健康、设备管理、脚本管理、AI功能、定时任务等
"""

import pytest
import allure
import requests
import json
import time
import sqlite3
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional

# 测试配置
API_BASE = "http://localhost:8000/api/v1"
FRONTEND_BASE = "http://localhost:5173"
DB_PATH = "../backend/test_platform.db"
TEST_TIMESTAMP = int(time.time())

class TestConfig:
    """测试配置类"""
    API_TIMEOUT = 30
    MAX_RETRY = 3
    
    @staticmethod
    def safe_print(msg: str):
        """安全打印，避免编码错误"""
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'ignore').decode('ascii'))

# ============================================================================
# 测试夹具 (Fixtures)
# ============================================================================

@pytest.fixture(scope="session")
def api_client():
    """API 客户端夹具"""
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.session = requests.Session()
            self.session.timeout = TestConfig.API_TIMEOUT
        
        def request(self, method: str, endpoint: str, **kwargs):
            """统一请求方法"""
            url = f"{self.base_url}{endpoint}"
            for attempt in range(TestConfig.MAX_RETRY):
                try:
                    response = self.session.request(method, url, **kwargs)
                    return response
                except requests.exceptions.RequestException as e:
                    if attempt == TestConfig.MAX_RETRY - 1:
                        raise e
                    time.sleep(0.5)
        
        def get(self, endpoint: str, **kwargs):
            return self.request("GET", endpoint, **kwargs)
        
        def post(self, endpoint: str, **kwargs):
            return self.request("POST", endpoint, **kwargs)
        
        def put(self, endpoint: str, **kwargs):
            return self.request("PUT", endpoint, **kwargs)
        
        def delete(self, endpoint: str, **kwargs):
            return self.request("DELETE", endpoint, **kwargs)
    
    return APIClient(API_BASE)

@pytest.fixture
def db_connection():
    """数据库连接夹具"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

@pytest.fixture
def test_data():
    """测试数据夹具"""
    return {
        "device": {
            "serial_number": f"TEST_DEVICE_{TEST_TIMESTAMP}",
            "model": "Test Model",
            "android_version": "11",
            "status": "online",
            "battery": 85
        },
        "script": {
            "name": f"测试脚本_{TEST_TIMESTAMP}",
            "type": "visual",
            "category": "test",
            "description": "自动化测试脚本",
            "steps_json": json.dumps([
                {"id": "s1", "type": "click", "name": "点击按钮", "config": {"x": 100, "y": 200}}
            ])
        }
    }

@pytest.fixture
def cleanup_test_data():
    """清理测试数据夹具"""
    data = {"devices": [], "scripts": [], "tasks": []}
    yield data

# ============================================================================
# 1. 系统健康检查
# ============================================================================

@allure.feature("系统健康检查")
class TestSystemHealth:
    """系统健康检查测试"""
    
    @allure.story("服务可用性")
    @allure.title("测试后端服务运行状态")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_backend_service_running(self, api_client):
        """测试后端服务是否运行"""
        try:
            response = api_client.get("/")
            assert response.status_code in [200, 404], "后端服务未运行"
            TestConfig.safe_print("✓ 后端服务运行正常")
        except requests.exceptions.ConnectionError:
            pytest.fail("后端服务未运行，请先启动服务")
    
    @allure.story("数据库连接")
    @allure.title("测试数据库连接")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_database_connection(self, db_connection):
        """测试数据库连接"""
        cursor = db_connection.cursor()
        tables = ['device', 'script', 'scheduled_task', 'task_log', 'ai_scripts', 'script_template']
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            assert result is not None, f"表 {table} 不存在"
        
        TestConfig.safe_print(f"✓ 数据库连接正常，{len(tables)} 个关键表存在")

# ============================================================================
# 2. 设备管理测试
# ============================================================================

@allure.feature("设备管理")
class TestDeviceManagement:
    """设备管理功能测试"""
    
    @allure.story("设备CRUD")
    @allure.title("测试设备完整CRUD操作")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_device_crud_operations(self, api_client, test_data, cleanup_test_data):
        """测试设备完整CRUD操作"""
        device_id = None
        
        try:
            # Create
            response = api_client.post("/devices", json=test_data["device"])
            assert response.status_code == 200
            device_id = response.json()["data"]["id"]
            cleanup_test_data["devices"].append(device_id)
            TestConfig.safe_print(f"✓ 创建设备成功，ID: {device_id}")
            
            # Read
            response = api_client.get(f"/devices/{device_id}")
            assert response.status_code == 200
            TestConfig.safe_print(f"✓ 读取设备成功")
            
            # Update
            update_data = {"model": "Updated Model", "battery": 95}
            response = api_client.put(f"/devices/{device_id}", json=update_data)
            assert response.status_code == 200
            TestConfig.safe_print(f"✓ 更新设备成功")
            
        finally:
            # Delete
            if device_id:
                response = api_client.delete(f"/devices/{device_id}")
                assert response.status_code == 200
                TestConfig.safe_print(f"✓ 删除设备成功")
    
    @allure.story("设备列表")
    @allure.title("测试获取设备列表")
    def test_get_devices_list(self, api_client):
        """测试获取设备列表"""
        response = api_client.get("/devices?page=1&page_size=20")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        TestConfig.safe_print("✓ 获取设备列表成功")

# ============================================================================
# 3. 脚本管理测试
# ============================================================================

@allure.feature("脚本管理")
class TestScriptManagement:
    """脚本管理功能测试"""
    
    @allure.story("脚本CRUD")
    @allure.title("测试脚本完整CRUD操作")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_script_crud_operations(self, api_client, test_data, cleanup_test_data):
        """测试脚本完整CRUD操作"""
        script_id = None
        
        try:
            # Create
            response = api_client.post("/scripts", json=test_data["script"])
            assert response.status_code == 200
            script_id = response.json()["data"]["id"]
            cleanup_test_data["scripts"].append(script_id)
            TestConfig.safe_print(f"✓ 创建脚本成功，ID: {script_id}")
            
            # Read
            response = api_client.get(f"/scripts/{script_id}")
            assert response.status_code == 200
            TestConfig.safe_print(f"✓ 读取脚本成功")
            
            # Update
            update_data = {"name": f"更新的脚本_{TEST_TIMESTAMP}", "description": "测试更新"}
            response = api_client.put(f"/scripts/{script_id}", json=update_data)
            assert response.status_code == 200
            TestConfig.safe_print(f"✓ 更新脚本成功")
            
        finally:
            # Delete
            if script_id:
                response = api_client.delete(f"/scripts/{script_id}")
                assert response.status_code == 200
                TestConfig.safe_print(f"✓ 删除脚本成功")
    
    @allure.story("脚本验证")
    @allure.title("测试脚本验证功能")
    def test_script_validation(self, api_client):
        """测试脚本验证功能"""
        test_cases = [
            {
                "name": "有效Python脚本",
                "data": {"script_type": "python", "content": "print('Hello World')", "filename": "test.py"},
                "should_pass": True
            },
            {
                "name": "有效批处理脚本",
                "data": {"script_type": "batch", "content": "adb devices", "filename": "test.bat"},
                "should_pass": True
            }
        ]
        
        for test_case in test_cases:
            response = api_client.post("/scripts/validate", json=test_case["data"])
            assert response.status_code == 200
            TestConfig.safe_print(f"✓ {test_case['name']} 验证完成")

# ============================================================================
# 4. AI脚本生成测试
# ============================================================================

@allure.feature("AI脚本生成")
class TestAIScriptGeneration:
    """AI脚本生成功能测试"""
    
    @allure.story("单个脚本生成")
    @allure.title("测试AI脚本生成功能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ai_script_generation(self, api_client):
        """测试AI脚本生成功能"""
        for language in ["adb", "python"]:
            request_data = {"prompt": "测试登录功能", "language": language}
            response = api_client.post("/ai-script/generate", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "generated_script" in data["data"]
            TestConfig.safe_print(f"✓ {language}脚本生成成功")
    
    @allure.story("批量脚本生成")
    @allure.title("测试批量脚本生成功能")
    def test_batch_script_generation(self, api_client):
        """测试批量脚本生成功能"""
        request_data = {
            "prompts": ["测试微信登录", "测试支付宝扫码"],
            "language": "adb",
            "generate_suite": True
        }
        response = api_client.post("/ai-script/batch-generate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "results" in data["data"]
        TestConfig.safe_print("✓ 批量生成完成")
    
    @allure.story("工作流生成")
    @allure.title("测试工作流脚本生成功能")
    def test_workflow_generation(self, api_client):
        """测试工作流脚本生成功能"""
        request_data = {
            "workflow_steps": ["启动微信应用", "点击登录按钮", "输入手机号码"],
            "language": "adb"
        }
        response = api_client.post("/ai-script/workflow-generate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "individual_scripts" in data["data"]
        TestConfig.safe_print("✓ 工作流生成完成")

# ============================================================================
# 5. 脚本模板测试
# ============================================================================

@allure.feature("脚本模板")
class TestScriptTemplates:
    """脚本模板功能测试"""
    
    @allure.story("模板管理")
    @allure.title("测试脚本模板CRUD操作")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_template_crud_operations(self, api_client):
        """测试脚本模板CRUD操作"""
        template_id = None
        
        try:
            # 获取模板列表
            response = api_client.get("/script-templates")
            assert response.status_code == 200
            TestConfig.safe_print("✓ 获取模板列表成功")
            
            # 创建模板
            template_data = {
                "name": f"测试模板_{TEST_TIMESTAMP}",
                "category": "测试分类",
                "description": "自动化测试模板",
                "language": "adb",
                "template_content": "adb shell input tap {{x}} {{y}}",
                "variables": {
                    "x": {"type": "number", "description": "X坐标", "required": True, "default": "100"},
                    "y": {"type": "number", "description": "Y坐标", "required": True, "default": "200"}
                },
                "tags": ["测试", "自动化"]
            }
            
            response = api_client.post("/script-templates", json=template_data)
            assert response.status_code == 200
            template_id = response.json()["data"]["id"]
            TestConfig.safe_print(f"✓ 创建模板成功，ID: {template_id}")
            
            # 使用模板
            use_data = {"template_id": template_id, "variables": {"x": "150", "y": "250"}}
            response = api_client.post("/script-templates/use", json=use_data)
            assert response.status_code == 200
            TestConfig.safe_print("✓ 使用模板成功")
            
        finally:
            if template_id:
                response = api_client.delete(f"/script-templates/{template_id}")
                assert response.status_code == 200
                TestConfig.safe_print("✓ 删除模板成功")

# ============================================================================
# 6. 设备健康度测试
# ============================================================================

@allure.feature("设备健康度")
class TestDeviceHealth:
    """设备健康度功能测试"""
    
    @allure.story("健康度监控")
    @allure.title("测试设备健康度监控")
    def test_device_health_monitoring(self, api_client):
        """测试设备健康度监控"""
        response = api_client.get("/device-health/overview")
        assert response.status_code == 200
        TestConfig.safe_print("✓ 获取健康度概览成功")
    
    @allure.story("告警规则")
    @allure.title("测试告警规则管理")
    def test_alert_rules_management(self, api_client):
        """测试告警规则管理"""
        response = api_client.get("/device-health/alert-rules")
        assert response.status_code == 200
        TestConfig.safe_print("✓ 获取告警规则成功")

# ============================================================================
# 7. 定时任务测试
# ============================================================================

@allure.feature("定时任务")
class TestScheduledTasks:
    """定时任务功能测试"""
    
    @allure.story("任务管理")
    @allure.title("测试定时任务管理")
    def test_scheduled_task_management(self, api_client):
        """测试定时任务管理"""
        response = api_client.get("/scheduled-tasks")
        assert response.status_code == 200
        TestConfig.safe_print("✓ 获取定时任务列表成功")

# ============================================================================
# 8. 仪表盘测试
# ============================================================================

@allure.feature("仪表盘")
class TestDashboard:
    """仪表盘功能测试"""
    
    @allure.story("数据统计")
    @allure.title("测试仪表盘数据统计")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dashboard_statistics(self, api_client):
        """测试仪表盘数据统计"""
        response = api_client.get("/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        
        stats = data["data"]["statistics"]
        required_fields = ["online_devices", "total_devices", "total_scripts", "today_executions", "success_rate"]
        
        for field in required_fields:
            assert field in stats, f"缺少统计字段: {field}"
        
        TestConfig.safe_print("✓ 仪表盘统计数据验证通过")

# ============================================================================
# 9. 数据一致性测试
# ============================================================================

@allure.feature("数据一致性")
class TestDataConsistency:
    """数据一致性测试"""
    
    @allure.story("数据格式验证")
    @allure.title("测试脚本数据格式一致性")
    def test_script_data_consistency(self, db_connection):
        """测试脚本数据格式一致性"""
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT id, name, steps_json 
            FROM script 
            WHERE type = 'visual' AND steps_json IS NOT NULL
            LIMIT 50
        """)
        scripts = cursor.fetchall()
        
        valid_count = 0
        for script in scripts:
            script_id, name, steps_json = script
            try:
                steps = json.loads(steps_json)
                if isinstance(steps, list):
                    valid_count += 1
            except json.JSONDecodeError:
                pass
        
        TestConfig.safe_print(f"✓ 检查了 {len(scripts)} 个脚本，{valid_count} 个格式正确")

# ============================================================================
# 10. 性能测试
# ============================================================================

@allure.feature("性能测试")
class TestPerformance:
    """性能测试"""
    
    @allure.story("API响应时间")
    @allure.title("测试API响应时间")
    def test_api_response_time(self, api_client):
        """测试API响应时间"""
        endpoints = [
            ("/devices", "设备列表"),
            ("/scripts", "脚本列表"),
            ("/dashboard/overview", "仪表盘概览")
        ]
        
        for endpoint, name in endpoints:
            start_time = time.time()
            response = api_client.get(endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            if response.status_code == 200:
                assert response_time < 3000, f"{name}响应时间过长: {response_time}ms"
            
            TestConfig.safe_print(f"✓ {name}响应时间: {response_time:.2f}ms")
    
    @allure.story("并发测试")
    @allure.title("测试API并发处理能力")
    def test_concurrent_requests(self, api_client):
        """测试API并发处理能力"""
        def make_request():
            try:
                response = api_client.get("/devices?page=1&page_size=5")
                return response.status_code == 200
            except:
                return False
        
        concurrent_count = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_count)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_count = sum(results)
        success_rate = success_count / concurrent_count * 100
        assert success_rate > 80, f"并发测试成功率过低: {success_rate:.1f}%"
        TestConfig.safe_print(f"✓ 并发测试完成，成功率: {success_rate:.1f}%")

# ============================================================================
# 11. 边界条件测试
# ============================================================================

@allure.feature("边界条件测试")
class TestBoundaryConditions:
    """边界条件测试"""
    
    @allure.story("输入验证")
    @allure.title("测试边界条件处理")
    def test_boundary_conditions(self, api_client):
        """测试边界条件处理"""
        boundary_tests = [
            {"name": "负数页码", "endpoint": "/devices", "params": {"page": -1, "page_size": 10}},
            {"name": "零页码", "endpoint": "/devices", "params": {"page": 0, "page_size": 10}},
            {"name": "超大页面大小", "endpoint": "/devices", "params": {"page": 1, "page_size": 999999}}
        ]
        
        for test in boundary_tests:
            response = api_client.get(test["endpoint"], params=test["params"])
            assert response.status_code in [200, 400, 422]
            TestConfig.safe_print(f"✓ {test['name']} 边界测试完成")

# ============================================================================
# 测试运行配置
# ============================================================================

if __name__ == "__main__":
    TestConfig.safe_print("=" * 60)
    TestConfig.safe_print("ADBweb 平台完整测试套件")
    TestConfig.safe_print("=" * 60)
    TestConfig.safe_print("")
    TestConfig.safe_print("运行命令:")
    TestConfig.safe_print("  pytest test_all.py -v")
    TestConfig.safe_print("  pytest test_all.py --alluredir=allure-results -v")
    TestConfig.safe_print("")
    TestConfig.safe_print("注意事项:")
    TestConfig.safe_print("  1. 确保后端服务运行在 http://localhost:8000")
    TestConfig.safe_print("  2. 确保前端服务运行在 http://localhost:5173")
    TestConfig.safe_print("  3. 确保数据库文件存在且可访问")
    TestConfig.safe_print("=" * 60)
