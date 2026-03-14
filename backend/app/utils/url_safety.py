"""
URL 安全校验工具
"""
from typing import List
from urllib.parse import urlparse
import ipaddress
import socket

from app.core.config import settings


def _parse_allowed_hosts() -> List[str]:
    raw = settings.ALLOWED_AI_API_HOSTS or ""
    hosts = [h.strip().lower() for h in raw.split(",") if h.strip()]
    return hosts


def _is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _is_private_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


def _resolve_host_ips(host: str) -> List[str]:
    try:
        infos = socket.getaddrinfo(host, None)
        return list({info[4][0] for info in infos})
    except Exception:
        return []


def validate_ai_api_base(api_base: str) -> str:
    """
    校验 AI API Base URL，防止 SSRF
    规则：
    - 必须是 https
    - 必须有 hostname
    - hostname 必须在允许列表中
    - 禁止内网/回环地址
    """
    if not api_base:
        raise ValueError("AI API Base URL 不能为空")

    base = api_base.strip().rstrip("/")
    parsed = urlparse(base)

    if parsed.scheme.lower() != "https":
        raise ValueError("AI API Base URL 必须使用 https")

    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("AI API Base URL 缺少 hostname")

    allowed_hosts = _parse_allowed_hosts()
    if allowed_hosts and host not in allowed_hosts:
        raise ValueError("AI API Base URL 不在允许列表中")

    if _is_ip_address(host) and _is_private_ip(host):
        raise ValueError("AI API Base URL 不能使用内网 IP")

    # 解析域名到 IP，防止解析到内网
    for ip in _resolve_host_ips(host):
        if _is_private_ip(ip):
            raise ValueError("AI API Base URL 解析到内网 IP，已拒绝")

    if parsed.query or parsed.fragment:
        raise ValueError("AI API Base URL 不能包含 query 或 fragment")

    # 允许带路径（例如 /v1）
    normalized = f"{parsed.scheme}://{host}{parsed.path}".rstrip("/")
    return normalized
