"""Global configuration (base URL, JWT, API key, default session)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    base_url: str = "http://localhost:3000"
    bearer_token: Optional[str] = None
    api_key: Optional[str] = None
    session_id: Optional[str] = None
    channel_secret: Optional[str] = None
    # Set when a reverse proxy (e.g. Cloudflare) blocks Python's default User-Agent.
    user_agent: Optional[str] = None


_config = Config()


def get_config() -> Config:
    return _config


def configure(
    *,
    base_url: Optional[str] = None,
    bearer_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Set one or more global options. Omitted keys are left unchanged."""
    if base_url is not None:
        _config.base_url = base_url.rstrip("/")
    if bearer_token is not None:
        _config.bearer_token = bearer_token or None
    if api_key is not None:
        _config.api_key = api_key or None
    if session_id is not None:
        _config.session_id = session_id or None
    if channel_secret is not None:
        _config.channel_secret = channel_secret or None
    if user_agent is not None:
        _config.user_agent = user_agent.strip() or None


def set_base_url(url: str) -> None:
    configure(base_url=url)


def set_bearer_token(token: str) -> None:
    configure(bearer_token=token)


def set_api_key(key: str) -> None:
    configure(api_key=key)


set_apikey = set_api_key


def set_session(session_id: str, channel_secret: str) -> None:
    configure(session_id=session_id, channel_secret=channel_secret)
