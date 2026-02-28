"""
Pytest 配置文件
提供全局 fixtures 和 hooks
"""
import pytest
import allure
import json
from datetime import datetime


def pytest_configure(config):
    """Pytest 配置钩子"""
    # 设置 Allure 环境信息
    allure_env = {
        "测试环境": "开发环境",
        "API地址": "http://localhost:8000",
        "数据库": "SQLite",
        "操作系统": "Windows 10",
        "Python版本": "3.11.8",
        "测试框架": "Pytest 7.4.3",
        "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 写入环境信息
    allure_results_dir = config.option.allure_report_dir
    if allure_results_dir:
        import os
        env_file = os.path.join(allure_results_dir, "environment.properties")
        os.makedirs(allure_results_dir, exist_ok=True)
        with open(env_file, "w", encoding="utf-8") as f:
            for key, value in allure_env.items():
                f.write(f"{key}={value}\n")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    在测试失败时自动截图和附加日志
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # 添加测试结果到 Allure
        if report.failed:
            allure.attach(
                str(report.longrepr),
                name="失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 添加测试时长
        allure.attach(
            f"{report.duration:.2f} 秒",
            name="执行时长",
            attachment_type=allure.attachment_type.TEXT
        )


@pytest.fixture(scope="session", autouse=True)
def test_session_info():
    """测试会话信息"""
    allure.dynamic.feature("ADBweb 平台测试")
    allure.dynamic.description("全功能自动化测试套件")
    yield


@pytest.fixture(autouse=True)
def test_info(request):
    """为每个测试添加基本信息"""
    # 添加测试用例 ID
    test_name = request.node.name
    allure.dynamic.label("test_case", test_name)
    
    # 添加测试类别
    if "test_" in test_name:
        category = test_name.split("test_")[1].split("_")[0]
        allure.dynamic.tag(category)
    
    yield
