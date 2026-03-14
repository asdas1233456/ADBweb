"""
Pytest configuration and shared fixtures for ADBweb tests.
"""
from __future__ import annotations

import os
from datetime import datetime

import allure
import pytest
import requests
import logging


def pytest_configure(config):
    """Write Allure environment metadata if the plugin is enabled."""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("tests").info("pytest configured: starting test session")
    allure_dir = getattr(config.option, "allure_report_dir", None)
    if not allure_dir:
        return

    env = {
        "Environment": os.getenv("TEST_ENV", "local"),
        "API_BASE_URL": os.getenv("API_BASE_URL", "http://localhost:8000/api/v1"),
        "FRONTEND_BASE_URL": os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"),
        "DB_PATH": os.getenv("TEST_DB_PATH", "../backend/test_platform.db"),
        "Python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    os.makedirs(allure_dir, exist_ok=True)
    env_file = os.path.join(allure_dir, "environment.properties")
    with open(env_file, "w", encoding="utf-8") as f:
        for key, value in env.items():
            f.write(f"{key}={value}\n")


def pytest_sessionstart(session):
    logging.getLogger("tests").info("pytest session started")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach failure details and duration to Allure."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    allure.attach(
        f"{report.duration:.2f}s",
        name="duration",
        attachment_type=allure.attachment_type.TEXT,
    )

    if report.failed:
        allure.attach(
            str(report.longrepr),
            name="failure",
            attachment_type=allure.attachment_type.TEXT,
        )


@pytest.fixture(scope="session", autouse=True)
def test_session_info():
    allure.dynamic.feature("ADBweb API Tests")
    allure.dynamic.description("Full-stack API and integration tests for ADBweb")
    yield


@pytest.fixture(autouse=True)
def test_info(request):
    test_name = request.node.name
    allure.dynamic.label("test_case", test_name)
    yield


# =========================
# Shared API fixtures
# =========================

def _get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1").rstrip("/")


def _get_root_url(api_base_url: str) -> str:
    if api_base_url.endswith("/api/v1"):
        return api_base_url[:-7]
    return api_base_url


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return _get_api_base_url()


@pytest.fixture(scope="session")
def root_base_url(api_base_url: str) -> str:
    return _get_root_url(api_base_url)


@pytest.fixture(scope="session")
def api_key() -> str:
    return (
        os.getenv("TEST_API_KEY")
        or os.getenv("API_ACCESS_KEY")
        or "CHANGE_ME"
    )


@pytest.fixture(scope="session")
def api_headers(api_key: str) -> dict:
    if api_key:
        return {"X-API-Key": api_key}
    return {}


@pytest.fixture(scope="session")
def backend_available(root_base_url: str) -> bool:
    try:
        resp = requests.get(f"{root_base_url}/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def api_session(api_base_url: str, api_headers: dict, backend_available: bool):
    if not backend_available:
        pytest.skip("Backend is not available; skipping API integration tests")
    session = requests.Session()
    session.headers.update(api_headers)
    session.base_url = api_base_url
    return session


@pytest.fixture
def api_request(api_session):
    def _request(method: str, path: str, **kwargs):
        url = (
            f"{api_session.base_url}{path}"
            if path.startswith("/")
            else f"{api_session.base_url}/{path}"
        )
        timeout = kwargs.pop("timeout", 30)
        return api_session.request(method, url, timeout=timeout, **kwargs)

    return _request
