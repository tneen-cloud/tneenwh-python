"""Minimal JSON HTTP using stdlib (no extra dependencies)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .config import get_config
from .exceptions import TneenwhApiError


def _url(path: str) -> str:
    cfg = get_config()
    base = cfg.base_url.rstrip("/")
    p = path if path.startswith("/") else f"/{path}"
    return f"{base}{p}"


def request_json(
    method: str,
    path: str,
    *,
    body: Optional[dict] = None,
    auth_bearer: bool = False,
    api_key: bool = False,
    channel_secret: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Any:
    cfg = get_config()
    url = _url(path)
    headers: Dict[str, str] = {"Accept": "application/json"}
    if cfg.user_agent:
        headers["User-Agent"] = cfg.user_agent
    if extra_headers:
        headers.update(extra_headers)
    data: Optional[bytes] = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    if auth_bearer:
        if not cfg.bearer_token:
            raise TneenwhApiError("bearer_token not set — login() or set_bearer_token()", 0, None)
        headers["Authorization"] = f"Bearer {cfg.bearer_token}"
    if api_key:
        if not cfg.api_key:
            raise TneenwhApiError("api_key not set — set_api_key()", 0, None)
        headers["X-Api-Key"] = cfg.api_key
    if channel_secret is not None:
        headers["X-Channel-Secret"] = channel_secret

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        msg = _json_error_message(parsed, e.code)
        raise TneenwhApiError(msg, e.code, parsed) from e
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        msg = str(reason) if reason is not None else str(e)
        raise TneenwhApiError(msg, 0, {"type": "URLError", "reason": msg}) from e


def _json_error_message(parsed: object, http_code: int) -> str:
    if not isinstance(parsed, dict):
        return f"HTTP {http_code}"
    err = parsed.get("error")
    if isinstance(err, str) and err.strip():
        return err.strip()
    detail = parsed.get("detail")
    if isinstance(detail, str) and detail.strip():
        return detail.strip()
    title = parsed.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return f"HTTP {http_code}"


def request_bytes(
    method: str,
    path: str,
    *,
    auth_bearer: bool = False,
    api_key: bool = False,
    channel_secret: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> tuple[bytes, str]:
    """Binary response (e.g. inbound media). Returns (body, content-type or '')."""
    cfg = get_config()
    url = _url(path)
    headers: Dict[str, str] = {}
    if cfg.user_agent:
        headers["User-Agent"] = cfg.user_agent
    if extra_headers:
        headers.update(extra_headers)
    if auth_bearer:
        if not cfg.bearer_token:
            raise TneenwhApiError("bearer_token not set — login() or set_bearer_token()", 0, None)
        headers["Authorization"] = f"Bearer {cfg.bearer_token}"
    if api_key:
        if not cfg.api_key:
            raise TneenwhApiError("api_key not set — set_api_key()", 0, None)
        headers["X-Api-Key"] = cfg.api_key
    if channel_secret is not None:
        headers["X-Channel-Secret"] = channel_secret

    req = urllib.request.Request(url, headers=headers, method=method)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            body = resp.read()
            ct = resp.headers.get("Content-Type") or ""
            return body, str(ct)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        msg = _json_error_message(parsed, e.code)
        raise TneenwhApiError(msg, e.code, parsed) from e
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        msg = str(reason) if reason is not None else str(e)
        raise TneenwhApiError(msg, 0, {"type": "URLError", "reason": msg}) from e
