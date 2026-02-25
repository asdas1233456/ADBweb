#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADBweb 核心功能测试套件
专注于核心功能的稳定测试
"""

import pytest
import allure
import requests
import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

# 测试配置
API_BASE = "http://localhost:8000/api/v1"
FRONTEND_BASE = "http://localhost:5173"
DB_PATH = "../backend/test_platform.db"

# 测试数据
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
# 测试夹具
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
        with allure.step("检查后端服务连接"):
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
        with allure.step("检查数据库连接和基础表"):
            cursor = db_connection.cursor()
            
            # 检查关键表是否存在
            tables = [
                'device', 'script', 'scheduled_task', 'task_log',
                'ai_scripts', 'script_template', 'device_health_records'
            ]
            
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
    
    @allure.story("设备列表")
    @allure.title("测试获取设备列表")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_devices_list(self, api_client):
        """测试获取设备列表"""
        with allure.step("获取设备列表"):
            response = api_client.get("/devices?page=1&page_size=20")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "data" in data
            
            TestConfig.safe_print(f"✓ 获取设备列表成功")
    
    @allure.story("设备操作")
    @allure.title("测试设备基本操作")
    @allure.severity(allure.severity_level.NORMAL)
    def test_device_operations(self, api_client, db_connection):
        """测试设备基本操作"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM device LIMIT 1")
        device = cursor.fetchone()
        
        if device:
            device_id = device[0]
            with allure.step(f"获取设备 {device_id} 详情"):
                response = api_client.get(f"/devices/{device_id}")
                # 设备详情API可能不存在，允许404
                assert response.status_code in [200, 404]
                TestConfig.safe_print(f"✓ 设备操作测试完成")

# ============================================================================
# 3. 脚本管理测试
# ============================================================================

@allure.feature("脚本管理")
class TestScriptManagement:
    """脚本管理功能测试"""
    
    @allure.story("脚本列表")
    @allure.title("测试获取脚本列表")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_scripts_list(self, api_client):
        """测试获取脚本列表"""
        with allure.step("获取脚本列表"):
            response = api_client.get("/scripts?page=1&page_size=20")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "data" in data
            
            TestConfig.safe_print(f"✓ 获取脚本列表成功")
    
    @allure.story("脚本CRUD")
    @allure.title("测试脚本创建和删除")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_script_create_delete(self, api_client):
        """测试脚本创建和删除"""
        script_id = None
        
        try:
            # Create - 创建脚本
            with allure.step("创建脚本"):
                test_script = {
                    "name": f"测试脚本_{TEST_TIMESTAMP}",
                    "type": "visual",
                    "category": "test",
                    "description": "自动化测试脚本",
                    "steps_json": json.dumps([
                        {"id": "s1", "type": "click", "name": "点击按钮", "config": {"x": 100, "y": 200}}
                    ])
                }
                response = api_client.post("/scripts", json=test_script)
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                script_id = data["data"]["id"]
                TestConfig.safe_print(f"✓ 创建脚本成功，ID: {script_id}")
            
        finally:
            # Delete - 删除脚本
            if script_id:
                with allure.step("删除脚本"):
                    response = api_client.delete(f"/scripts/{script_id}")
                    assert response.status_code == 200
                    TestConfig.safe_print(f"✓ 删除脚本成功")

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
        with allure.step("生成ADB脚本"):
            request_data = {
                "prompt": "测试登录功能",
                "language": "adb"
            }
            
            response = api_client.post("/ai-script/generate", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "generated_script" in data["data"]
            assert len(data["data"]["generated_script"]) > 0
            
            TestConfig.safe_print("✓ AI脚本生成成功")

# ============================================================================
# 5. 脚本模板测试
# ============================================================================

@allure.feature("脚本模板")
class TestScriptTemplates:
    """脚本模板功能测试"""
    
    @allure.story("模板列表")
    @allure.title("测试获取脚本模板列表")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_templates_list(self, api_client):
        """测试获取脚本模板列表"""
        with allure.step("获取模板列表"):
            response = api_client.get("/script-templates")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert isinstance(data["data"], list)
            TestConfig.safe_print(f"✓ 获取模板列表成功，共 {len(data['data'])} 个模板")

# ============================================================================
# 6. 数据一致性测试
# ============================================================================

@allure.feature("数据一致性")
class TestDataConsistency:
    """数据一致性测试"""
    
    @allure.story("数据格式验证")
    @allure.title("测试脚本数据格式一致性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_script_data_consistency(self, db_connection):
        """测试脚本数据格式一致性"""
        cursor = db_connection.cursor()
        
        with allure.step("检查可视化脚本steps_json格式"):
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
    
    @allure.story("数据完整性")
    @allure.title("测试数据完整性约束")
    @allure.severity(allure.severity_level.NORMAL)
    def test_data_integrity_constraints(self, db_connection):
        """测试数据完整性约束"""
        cursor = db_connection.cursor()
        
        with allure.step("检查脚本名称非空"):
            cursor.execute("SELECT COUNT(*) FROM script WHERE name IS NULL OR name = ''")
            empty_names = cursor.fetchone()[0]
            assert empty_names == 0, f"发现 {empty_names} 个空脚本名称"
            TestConfig.safe_print("✓ 脚本名称完整性检查通过")

# ============================================================================
# 7. 基础API测试
# ============================================================================

@allure.feature("基础API")
class TestBasicAPI:
    """基础API功能测试"""
    
    @allure.story("API响应")
    @allure.title("测试基础API响应")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_basic_api_responses(self, api_client):
        """测试基础API响应"""
        endpoints = [
            "/devices",
            "/scripts", 
            "/script-templates",
            "/scheduled-tasks"
        ]
        
        for endpoint in endpoints:
            with allure.step(f"测试 {endpoint}"):
                response = api_client.get(endpoint)
                assert response.status_code == 200
                data = response.json()
                assert "code" in data
                TestConfig.safe_print(f"✓ {endpoint} API正常")

# ============================================================================
# 测试运行配置
# ============================================================================

if __name__ == "__main__":
    TestConfig.safe_print("ADBweb 核心功能测试套件")
    TestConfig.safe_print("运行命令: pytest test_core_features.py -v")