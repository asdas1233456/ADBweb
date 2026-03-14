"""
API 访问控制与安全工具
"""
import hmac
from typing import Optional

from fastapi import HTTPException, Request, WebSocket

from app.core.config import settings


def auth_required() -> bool:
    """判断是否启用 API Key 校验"""
    return bool(settings.API_AUTH_ENABLED and settings.API_ACCESS_KEY)


def _extract_key_from_auth_header(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return None


def extract_api_key_from_request(request: Request) -> Optional[str]:
    """从 HTTP 请求中提取 API Key"""
    key = request.headers.get("x-api-key")
    if key:
        return key.strip()
    return _extract_key_from_auth_header(request.headers.get("authorization"))


def extract_api_key_from_websocket(websocket: WebSocket) -> Optional[str]:
    """从 WebSocket 连接中提取 API Key"""
    key = websocket.query_params.get("api_key") or websocket.query_params.get("token")
    if key:
        return key.strip()
    header_key = websocket.headers.get("x-api-key")
    if header_key:
        return header_key.strip()
    return _extract_key_from_auth_header(websocket.headers.get("authorization"))


def verify_api_key(api_key: Optional[str]) -> bool:
    """校验 API Key"""
    if not api_key or not settings.API_ACCESS_KEY:
        return False
    return hmac.compare_digest(api_key, settings.API_ACCESS_KEY)


def enforce_api_key(request: Request) -> None:
    """在 HTTP 请求中强制校验 API Key"""
    if not auth_required():
        return
    api_key = extract_api_key_from_request(request)
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")


def enforce_api_key_ws(websocket: WebSocket) -> bool:
    """在 WebSocket 连接中强制校验 API Key"""
    if not auth_required():
        return True
    api_key = extract_api_key_from_websocket(websocket)
    return verify_api_key(api_key)
