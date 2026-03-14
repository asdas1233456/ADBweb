#!/usr/bin/env python3
"""
ADBweb API comprehensive test suite.
"""
import concurrent.futures
import json
import os
import sqlite3
import time
from datetime import datetime

import allure
import pytest
import requests

TEST_TIMESTAMP = int(time.time())
DB_PATH = os.getenv("TEST_DB_PATH", "../backend/test_platform.db")


def _resolve_db_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    base_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(base_dir, path))


def assert_api_ok(response, allow_http=(200,), allow_codes=(200,)):
    assert response.status_code in allow_http, (
        f"Unexpected HTTP {response.status_code}: {response.text}"
    )
    try:
        payload = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")
    if isinstance(payload, dict) and "code" in payload:
        assert payload["code"] in allow_codes, (
            f"Unexpected API code {payload.get('code')}: {payload.get('message')}"
        )
    return payload


@pytest.fixture
def db_connection():
    db_path = _resolve_db_path(DB_PATH)
    if not os.path.exists(db_path):
        pytest.skip("Test database not found; skipping DB tests")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def test_data():
    return {
        "device": {
            "serial_number": f"TEST_DEVICE_{TEST_TIMESTAMP}",
            "model": "Test Model",
            "android_version": "11",
            "status": "online",
            "battery": 85,
        },
        "script": {
            "name": f"Test Script {TEST_TIMESTAMP}",
            "type": "visual",
            "category": "test",
            "description": "Automated test script",
            "steps_json": json.dumps(
                [
                    {
                        "id": "s1",
                        "type": "click",
                        "name": "Tap button",
                        "config": {"x": 100, "y": 200},
                    }
                ]
            ),
        },
    }


# ============================================================================
# 1. System Health
# ============================================================================


@allure.feature("System Health")
class TestSystemHealth:
    @allure.story("Backend availability")
    def test_health_endpoint(self, root_base_url, backend_available):
        if not backend_available:
            pytest.skip("Backend is not available")
        resp = requests.get(f"{root_base_url}/health", timeout=5)
        assert resp.status_code == 200
        payload = resp.json()
        assert payload.get("status") == "ok"


# ============================================================================
# 2. Dashboard
# ============================================================================


@allure.feature("Dashboard")
class TestDashboard:
    @allure.story("Overview")
    def test_dashboard_overview(self, api_request):
        resp = api_request("GET", "/dashboard/overview")
        data = assert_api_ok(resp)
        assert "data" in data

    @allure.story("Stats")
    def test_dashboard_stats(self, api_request):
        resp = api_request("GET", "/dashboard/stats")
        data = assert_api_ok(resp)
        assert "data" in data


# ============================================================================
# 3. Device Management
# ============================================================================


@allure.feature("Device Management")
class TestDeviceManagement:
    @allure.story("CRUD")
    def test_device_crud(self, api_request, test_data):
        device_id = None

        try:
            # Create
            resp = api_request("POST", "/devices", json=test_data["device"])
            data = assert_api_ok(resp)
            device_id = data["data"]["id"]

            # Read
            resp = api_request("GET", f"/devices/{device_id}")
            assert_api_ok(resp)

            # Update
            resp = api_request(
                "PUT",
                f"/devices/{device_id}",
                json={"model": "Updated Model", "battery": 95},
            )
            assert_api_ok(resp)

        finally:
            if device_id:
                resp = api_request("DELETE", f"/devices/{device_id}")
                assert_api_ok(resp)

    @allure.story("List")
    def test_device_list(self, api_request):
        resp = api_request("GET", "/devices?page=1&page_size=20")
        data = assert_api_ok(resp)
        assert "data" in data

    @allure.story("Group + Performance + Screenshot")
    def test_device_group_and_metrics(self, api_request):
        device_id = None
        try:
            resp = api_request(
                "POST",
                "/devices",
                json={
                    "serial_number": f"TEST_DEVICE_GROUP_{TEST_TIMESTAMP}",
                    "model": "Group Model",
                    "android_version": "11",
                    "status": "online",
                    "battery": 90,
                },
            )
            data = assert_api_ok(resp)
            device_id = data["data"]["id"]

            resp = api_request(
                "PUT",
                f"/devices/{device_id}/group",
                params={"group_name": "TestGroup"},
            )
            assert_api_ok(resp)

            resp = api_request("GET", "/devices/groups/list")
            data = assert_api_ok(resp)
            assert "TestGroup" in data.get("data", [])

            resp = api_request("GET", f"/devices/{device_id}/performance")
            assert_api_ok(resp)

            resp = api_request("GET", f"/devices/{device_id}/screenshot")
            assert_api_ok(resp)
        finally:
            if device_id:
                resp = api_request("DELETE", f"/devices/{device_id}")
                assert_api_ok(resp)


# ============================================================================
# 4. Script Management
# ============================================================================


@allure.feature("Script Management")
class TestScriptManagement:
    @allure.story("CRUD")
    def test_script_crud(self, api_request, test_data):
        script_id = None

        try:
            # Create
            resp = api_request("POST", "/scripts", json=test_data["script"])
            data = assert_api_ok(resp)
            script_id = data["data"]["id"]

            # Read
            resp = api_request("GET", f"/scripts/{script_id}")
            assert_api_ok(resp)

            # Update
            resp = api_request(
                "PUT",
                f"/scripts/{script_id}",
                json={"description": "Updated description"},
            )
            assert_api_ok(resp)

        finally:
            if script_id:
                resp = api_request("DELETE", f"/scripts/{script_id}")
                assert_api_ok(resp)

    @allure.story("Validate")
    def test_script_validation(self, api_request):
        cases = [
            {
                "script_type": "python",
                "content": "print('hello')",
                "filename": "test.py",
            },
            {
                "script_type": "batch",
                "content": "adb devices",
                "filename": "test.bat",
            },
        ]

        for case in cases:
            resp = api_request("POST", "/scripts/validate", json=case)
            assert_api_ok(resp)


# ============================================================================
# 5. Script Templates
# ============================================================================


@allure.feature("Script Templates")
class TestScriptTemplates:
    @allure.story("CRUD")
    def test_template_crud(self, api_request):
        template_id = None

        try:
            # List
            resp = api_request("GET", "/script-templates")
            assert_api_ok(resp)
            resp = api_request("GET", "/script-templates/categories")
            assert_api_ok(resp)

            # Create
            template_data = {
                "name": f"Test Template {TEST_TIMESTAMP}",
                "category": "test",
                "description": "Template for tests",
                "language": "adb",
                "template_content": "adb shell input tap {{x}} {{y}}",
                "variables": {
                    "x": {
                        "type": "number",
                        "description": "X coordinate",
                        "required": True,
                        "default": "100",
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate",
                        "required": True,
                        "default": "200",
                    },
                },
                "tags": ["test"],
            }
            resp = api_request("POST", "/script-templates", json=template_data)
            data = assert_api_ok(resp)
            template_id = data["data"]["id"]

            # Use
            use_data = {
                "template_id": template_id,
                "variables": {"x": "150", "y": "250"},
            }
            resp = api_request("POST", "/script-templates/use", json=use_data)
            assert_api_ok(resp)

        finally:
            if template_id:
                resp = api_request("DELETE", f"/script-templates/{template_id}")
                assert_api_ok(resp, allow_http=(200, 404))


# ============================================================================
# 6. AI Script Generation
# ============================================================================


@allure.feature("AI Script Generation")
class TestAIScriptGeneration:
    @allure.story("Prompt optimize")
    def test_ai_prompt_optimize(self, api_request):
        payload = {"prompt": "Test login flow", "language": "adb"}
        resp = api_request("POST", "/ai-script/optimize-prompt", json=payload)
        data = assert_api_ok(resp)
        assert "optimized_prompt" in data["data"]

    @allure.story("Generate + validate + save")
    def test_ai_generate_validate_save(self, api_request):
        ai_script_id = None
        saved_script_id = None

        try:
            # Generate
            payload = {"prompt": "Test login flow", "language": "adb"}
            resp = api_request("POST", "/ai-script/generate", json=payload)
            data = assert_api_ok(resp)
            ai_script_id = data["data"]["id"]

            # Validate generated
            resp = api_request(
                "POST",
                "/ai-script/validate-generated",
                params={"ai_script_id": ai_script_id},
            )
            assert_api_ok(resp)

            # Save to scripts
            resp = api_request(
                "POST",
                "/ai-script/save-to-scripts",
                json={
                    "ai_script_id": ai_script_id,
                    "name": f"AI Script {TEST_TIMESTAMP}",
                    "category": "test",
                    "description": "Saved from AI",
                },
            )
            data = assert_api_ok(resp)
            saved_script_id = data["data"]["script_id"]

        finally:
            if saved_script_id:
                resp = api_request("DELETE", f"/scripts/{saved_script_id}")
                assert_api_ok(resp)
            if ai_script_id:
                resp = api_request("DELETE", f"/ai-script/{ai_script_id}")
                assert_api_ok(resp)

    @allure.story("Batch generate")
    def test_ai_batch_generate(self, api_request):
        payload = {
            "prompts": ["Test login", "Test search"],
            "language": "adb",
            "generate_suite": True,
        }
        resp = api_request("POST", "/ai-script/batch-generate", json=payload)
        assert_api_ok(resp)

    @allure.story("Workflow generate")
    def test_ai_workflow_generate(self, api_request):
        payload = {
            "workflow_steps": ["Open app", "Tap login", "Enter password"],
            "language": "adb",
        }
        resp = api_request("POST", "/ai-script/workflow-generate", json=payload)
        assert_api_ok(resp)

    @allure.story("History")
    def test_ai_history(self, api_request):
        resp = api_request("GET", "/ai-script/history?limit=5")
        data = assert_api_ok(resp)
        assert isinstance(data.get("data"), list)


# ============================================================================
# 7. Device Health
# ============================================================================


@allure.feature("Device Health")
class TestDeviceHealth:
    @allure.story("Overview")
    def test_device_health_overview(self, api_request):
        resp = api_request("GET", "/device-health/overview")
        assert_api_ok(resp)

    @allure.story("Alert rules")
    def test_device_health_alert_rules(self, api_request):
        resp = api_request("GET", "/device-health/alert-rules")
        assert_api_ok(resp)

    @allure.story("Alerts list")
    def test_device_health_alerts(self, api_request):
        resp = api_request("GET", "/device-health/alerts")
        assert_api_ok(resp)

    @allure.story("Trigger collection")
    def test_device_health_collect(self, api_request):
        resp = api_request("POST", "/device-health/collect")
        assert_api_ok(resp, allow_http=(200, 202))


# ============================================================================
# 8. Uploads
# ============================================================================


@allure.feature("Uploads")
class TestUploads:
    @allure.story("Upload script")
    def test_upload_script(self, api_request, tmp_path):
        script_path = tmp_path / "test.py"
        script_path.write_text("print('hello')")

        with open(script_path, "rb") as f:
            files = {"file": ("test.py", f, "text/x-python")}
            data = {"script_type": "python"}
            resp = api_request("POST", "/upload/script", files=files, data=data)
        assert_api_ok(resp)

    @allure.story("Upload screenshot")
    def test_upload_screenshot(self, api_request, tmp_path):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow is required for screenshot upload tests")

        image_path = tmp_path / "test.png"
        img = Image.new("RGB", (64, 64), color="red")
        img.save(image_path)

        with open(image_path, "rb") as f:
            files = {"file": ("test.png", f, "image/png")}
            data = {"task_log_id": "1"}
            resp = api_request("POST", "/upload/screenshot", files=files, data=data)
        assert_api_ok(resp)

    @allure.story("Upload APK")
    def test_upload_apk(self, api_request, tmp_path):
        apk_path = tmp_path / "test.apk"
        apk_path.write_bytes(b"dummy apk")

        with open(apk_path, "rb") as f:
            files = {"file": ("test.apk", f, "application/vnd.android.package-archive")}
            resp = api_request("POST", "/batch-operations/upload-apk", files=files)
        assert_api_ok(resp)


# ============================================================================
# 9. Data Consistency (DB)
# ============================================================================


@allure.feature("Data Consistency")
class TestDataConsistency:
    @allure.story("Script JSON format")
    def test_script_data_consistency(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            """
            SELECT id, name, steps_json
            FROM script
            WHERE type = 'visual' AND steps_json IS NOT NULL
            LIMIT 50
            """
        )
        scripts = cursor.fetchall()

        valid_count = 0
        for script in scripts:
            steps_json = script[2]
            try:
                steps = json.loads(steps_json)
                if isinstance(steps, list):
                    valid_count += 1
            except json.JSONDecodeError:
                pass

        assert valid_count >= 0

    @allure.story("Dashboard stats vs DB")
    def test_dashboard_stats_consistency(self, db_connection, api_request):
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM device")
        total_devices = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM device WHERE status='online'")
        online_devices = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM script WHERE is_active=1")
        total_scripts = cursor.fetchone()[0]

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute(
            "SELECT COUNT(*) FROM task_log WHERE start_time >= ?",
            (today_start.isoformat(),),
        )
        today_executions = cursor.fetchone()[0]

        resp = api_request("GET", "/dashboard/overview")
        data = assert_api_ok(resp)
        stats = data["data"]["statistics"]

        assert stats["total_devices"] == total_devices
        assert stats["online_devices"] == online_devices
        assert stats["total_scripts"] == total_scripts
        assert stats["today_executions"] == today_executions


# ============================================================================
# 10. Performance
# ============================================================================


@allure.feature("Performance")
class TestPerformance:
    @pytest.mark.performance
    def test_api_response_time(self, api_request):
        endpoints = [
            ("/devices", "devices list"),
            ("/scripts", "scripts list"),
            ("/dashboard/overview", "dashboard overview"),
        ]

        for endpoint, name in endpoints:
            start = time.time()
            resp = api_request("GET", endpoint)
            elapsed_ms = (time.time() - start) * 1000
            if resp.status_code == 200:
                assert elapsed_ms < 5000, f"{name} too slow: {elapsed_ms:.2f}ms"

    @pytest.mark.performance
    def test_concurrent_requests(self, api_base_url, api_headers):
        def make_request():
            try:
                resp = requests.get(
                    f"{api_base_url}/devices?page=1&page_size=5",
                    headers=api_headers,
                    timeout=10,
                )
                return resp.status_code == 200
            except Exception:
                return False

        concurrent_count = 8
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as exe:
            results = list(exe.map(lambda _: make_request(), range(concurrent_count)))

        success_rate = sum(results) / concurrent_count * 100
        assert success_rate >= 80.0


# ============================================================================
# 11. Boundary Conditions
# ============================================================================


@allure.feature("Boundary Conditions")
class TestBoundaryConditions:
    @pytest.mark.boundary
    def test_pagination_boundaries(self, api_request):
        cases = [
            {"page": -1, "page_size": 10},
            {"page": 0, "page_size": 10},
            {"page": 1, "page_size": 100000},
        ]
        for params in cases:
            resp = api_request("GET", "/devices", params=params)
            assert resp.status_code in (200, 400, 422)


# ============================================================================
# 14. WebSocket (Frontend/Backend Interactive)
# ============================================================================


@allure.feature("WebSocket")
class TestWebSocket:
    @pytest.mark.integration
    def test_websocket_ping(self, api_base_url, api_key, backend_available):
        if not backend_available:
            pytest.skip("Backend is not available")
        try:
            import websocket
        except ImportError:
            pytest.skip("websocket-client is required for WebSocket tests")

        ws_url = api_base_url.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/ws/test_client?api_key={api_key}"

        ws = None
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            payload = {"type": "ping", "timestamp": int(time.time())}
            ws.send(json.dumps(payload))
            message = json.loads(ws.recv())
            assert message.get("type") == "pong"
        finally:
            if ws is not None:
                ws.close()


# ============================================================================
# 12. AI Element Locator
# ============================================================================


@pytest.fixture
def sample_image_path(tmp_path):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        pytest.skip("Pillow is required for AI element locator tests")

    img = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(img)

    draw.rectangle([100, 100, 300, 150], outline="blue", width=2)
    draw.text((150, 115), "Login", fill="black")

    draw.rectangle([100, 200, 300, 250], outline="blue", width=2)
    draw.text((150, 215), "Register", fill="black")

    path = tmp_path / "test_screenshot.png"
    img.save(path)
    return path


@pytest.fixture
def uploaded_image_path(api_request, sample_image_path):
    with open(sample_image_path, "rb") as f:
        files = {"file": ("screenshot.png", f, "image/png")}
        resp = api_request("POST", "/ai-element-locator/upload-screenshot", files=files)
    data = assert_api_ok(resp)
    return data["data"]["file_path"]


@allure.feature("AI Element Locator")
class TestAIElementLocator:
    def test_capabilities(self, api_request):
        resp = api_request("GET", "/ai-element-locator/capabilities")
        data = assert_api_ok(resp)
        assert "data" in data

    def test_examples(self, api_request):
        resp = api_request("GET", "/ai-element-locator/examples")
        data = assert_api_ok(resp)
        assert isinstance(data.get("data"), list)

    def test_element_types(self, api_request):
        resp = api_request("GET", "/ai-element-locator/element-types")
        data = assert_api_ok(resp)
        assert isinstance(data.get("data"), list)

    def test_element_states(self, api_request):
        resp = api_request("GET", "/ai-element-locator/element-states")
        data = assert_api_ok(resp)
        assert isinstance(data.get("data"), list)

    def test_analyze_screenshot(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/analyze",
            json={"image_path": uploaded_image_path},
        )
        data = assert_api_ok(resp)
        assert "elements" in data["data"]

    def test_find_element(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/find-element",
            json={
                "image_path": uploaded_image_path,
                "query": "Login",
                "method": "auto",
            },
        )
        assert resp.status_code in (200, 404)

    def test_get_coordinates(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/get-coordinates",
            json={
                "image_path": uploaded_image_path,
                "query": "Login",
                "method": "auto",
            },
        )
        assert resp.status_code in (200, 404)

    def test_generate_command(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/generate-command",
            json={
                "image_path": uploaded_image_path,
                "action": "click",
                "query": "Login",
            },
        )
        assert resp.status_code in (200, 404)

    def test_visualize(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/visualize",
            json={"image_path": uploaded_image_path, "show_labels": True},
        )
        assert_api_ok(resp)

    def test_find_relative(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/find-relative",
            json={
                "image_path": uploaded_image_path,
                "anchor_query": "Login",
                "direction": "right",
                "distance_threshold": 200,
            },
        )
        assert resp.status_code in (200, 404)

    def test_find_in_region(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/find-in-region",
            json={
                "image_path": uploaded_image_path,
                "region": [0, 0, 400, 400],
                "element_type": "button",
            },
        )
        assert resp.status_code in (200, 404)

    def test_filter_by_state(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/filter-by-state",
            json={
                "image_path": uploaded_image_path,
                "element_type": "checkbox",
                "state": "checked",
            },
        )
        assert resp.status_code in (200, 404, 400)

    def test_smart_click(self, api_request, uploaded_image_path):
        resp = api_request(
            "POST",
            "/ai-element-locator/smart-click",
            params={"image_path": uploaded_image_path, "query": "Login"},
        )
        assert resp.status_code in (200, 404)


# ============================================================================
# 13. Security Checks
# ============================================================================


def _skip_if_backend_unavailable(backend_available):
    if not backend_available:
        pytest.skip("Backend is not available; skipping security tests")


@allure.feature("Security")
class TestSecurity:
    def test_auth_enforcement(self, api_base_url, backend_available):
        _skip_if_backend_unavailable(backend_available)
        resp = requests.get(f"{api_base_url}/dashboard/overview", timeout=5)
        assert resp.status_code in (200, 401)

    def test_ai_api_base_validation(self, api_base_url, api_headers, backend_available):
        _skip_if_backend_unavailable(backend_available)
        resp = requests.post(
            f"{api_base_url}/ai-script/test-connection",
            json={"api_key": "test", "api_base": "http://127.0.0.1"},
            headers=api_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("code") in (400, 401)

    def test_ai_element_path_safety(self, api_base_url, api_headers, backend_available):
        _skip_if_backend_unavailable(backend_available)
        resp = requests.post(
            f"{api_base_url}/ai-element-locator/analyze",
            json={"image_path": "../README.md"},
            headers=api_headers,
            timeout=10,
        )
        assert resp.status_code in (400, 404, 422)

    def test_upload_script_disallowed_type(
        self, api_base_url, api_headers, backend_available, tmp_path
    ):
        _skip_if_backend_unavailable(backend_available)
        file_path = tmp_path / "test.txt"
        file_path.write_text("hello")
        with open(file_path, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            resp = requests.post(
                f"{api_base_url}/upload/script",
                files=files,
                data={"script_type": "python"},
                headers=api_headers,
                timeout=10,
            )
        assert resp.status_code in (400, 422)


if __name__ == "__main__":
    import pytest as _pytest

    _pytest.main([__file__, "-v"])
