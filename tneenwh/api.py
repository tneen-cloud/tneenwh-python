"""High-level API functions (use global config from `configure` / setters)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .channel import Channel, channel as _channel
from .config import get_config
from .exceptions import FeatureNotSupportedError, TneenwhApiError
from .http import request_json


def _resolve_session(
    session_id: Optional[str], channel_secret: Optional[str]
) -> tuple[str, str]:
    c = get_config()
    sid = session_id or c.session_id
    sec = channel_secret or c.channel_secret
    if not sid or not sec:
        raise TneenwhApiError(
            "Pass session_id and channel_secret, or call set_session(id, secret) / configure(...)",
            0,
            None,
        )
    return sid, sec


# --- Public API ---


def health() -> dict:
    return request_json("GET", "/health", auth_bearer=False)


def signup_send_otp(
    *,
    name: str,
    phone: str,
    email: str,
    password: str,
) -> dict:
    """Start signup; server sends WhatsApp OTP when configured (POST /auth/signup/start)."""
    return request_json(
        "POST",
        "/auth/signup/start",
        body={"name": name, "phone": phone, "email": email, "password": password},
        auth_bearer=False,
    )


def generate_otp(**kwargs) -> dict:
    """Alias for :func:`signup_send_otp`."""
    return signup_send_otp(**kwargs)


def request_signup_otp(**kwargs) -> dict:
    """Alias for :func:`signup_send_otp`."""
    return signup_send_otp(**kwargs)


def signup_verify(*, email: str, code: str) -> dict:
    """Verify email with 6-digit code (POST /auth/signup/verify)."""
    return request_json("POST", "/auth/signup/verify", body={"email": email, "code": code}, auth_bearer=False)


def verify_otp(*, email: str, code: str) -> dict:
    """Alias for :func:`signup_verify`."""
    return signup_verify(email=email, code=code)


def login(*, email: str, password: str) -> dict:
    """Login; stores JWT in global config for subsequent panel calls."""
    data = request_json("POST", "/auth/login", body={"email": email, "password": password}, auth_bearer=False)
    token = data.get("token")
    if isinstance(token, str) and token:
        from .config import configure

        configure(bearer_token=token)
    return data


def logout() -> dict:
    return request_json("POST", "/auth/logout", body={}, auth_bearer=False)


def me() -> dict:
    return request_json("GET", "/me", auth_bearer=True)


def profile() -> dict:
    return request_json("GET", "/me/profile", auth_bearer=True)


def channel_secrets() -> dict:
    return request_json("GET", "/me/channel-secrets", auth_bearer=True)


def rotate_swagger_portal() -> dict:
    return request_json("POST", "/me/credentials/swagger-portal/rotate", body={}, auth_bearer=True)


def sessions_list() -> dict:
    return request_json("GET", "/me/sessions", auth_bearer=True)


def session_create(name: str) -> dict:
    return request_json("POST", "/me/sessions", body={"name": name}, auth_bearer=True)


def session_update(session_id: str, channel_secret: str, name: str) -> dict:
    return request_json(
        "PATCH",
        f"/me/sessions/{session_id}",
        body={"name": name},
        auth_bearer=True,
        channel_secret=channel_secret,
    )


def session_delete(session_id: str, channel_secret: str) -> dict:
    return request_json(
        "DELETE",
        f"/me/sessions/{session_id}",
        auth_bearer=True,
        channel_secret=channel_secret,
    )


def session_disconnect(session_id: str, channel_secret: str) -> dict:
    return request_json(
        "POST",
        f"/me/sessions/{session_id}/disconnect",
        body={},
        auth_bearer=True,
        channel_secret=channel_secret,
    )


def get_channel_secret(session_id: str) -> dict:
    return request_json("GET", f"/me/sessions/{session_id}/channel-secret", auth_bearer=True)


def rotate_channel_secret(session_id: str, channel_secret: str) -> dict:
    """Rotate X-Channel-Secret for a session (POST …/channel-secret/rotate)."""
    return request_json(
        "POST",
        f"/me/sessions/{session_id}/channel-secret/rotate",
        body={},
        auth_bearer=True,
        channel_secret=channel_secret,
    )


def v1_sessions_list() -> dict:
    """Sub-API: list sessions (GET /v1/sessions, x-api-key)."""
    return request_json("GET", "/v1/sessions", auth_bearer=False, api_key=True)


def v1_send_message(
    session_id: str,
    channel_secret: str,
    payload: Dict[str, Any],
) -> dict:
    return request_json(
        "POST",
        f"/v1/sessions/{session_id}/messages/send",
        body=payload,
        auth_bearer=False,
        api_key=True,
        channel_secret=channel_secret,
    )


def send_message(
    payload: Dict[str, Any],
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    """POST /me/sessions/.../messages/send using default or explicit session."""
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).send_message(payload)


def send_text(
    to: str,
    text: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    return send_message({"to": to, "message": text}, session_id=session_id, channel_secret=channel_secret)


def send_media(
    to: str,
    *,
    mimetype: str,
    base64_data: str,
    caption: Optional[str] = None,
    filename: Optional[str] = None,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).send_media(
        to, mimetype=mimetype, base64_data=base64_data, caption=caption, filename=filename
    )


def session(session_id: str, channel_secret: str) -> Channel:
    """Return a :class:`Channel` for chained calls."""
    return _channel(session_id, channel_secret)


def session_status(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).status()


def session_details(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).details()


def session_qr(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).qr()


def session_incoming(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).incoming()


def session_events(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).events()


def session_calls(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).calls()


def set_webhook(
    webhook_url: str,
    events: List[str],
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).set_webhook(webhook_url, events)


def download_inbound_media(
    ticket: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> tuple[bytes, str]:
    """Download decrypted inbound media by ticket from GET …/media/:ticket."""
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).download_inbound_media(ticket)


def refresh_session_qr(
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    """POST …/qr/refresh — force new QR (session must not be linked)."""
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).refresh_qr()


def create_group(
    title: str,
    participants: Optional[List[str]] = None,
    *,
    options: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    """POST …/groups — create a WhatsApp group (session must be **linked** / ready)."""
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_create(title, participants, options)


def group_get(
    group_jid: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_get(group_jid)


def group_participants_add(
    group_jid: str,
    participant_ids: List[str],
    *,
    options: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_participants_add(group_jid, participant_ids, options)


def group_participants_remove(
    group_jid: str,
    participant_ids: List[str],
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_participants_remove(group_jid, participant_ids)


def group_admins_promote(
    group_jid: str,
    participant_ids: List[str],
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_admins_promote(group_jid, participant_ids)


def group_admins_demote(
    group_jid: str,
    participant_ids: List[str],
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_admins_demote(group_jid, participant_ids)


def group_set_subject(
    group_jid: str,
    subject: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_set_subject(group_jid, subject)


def group_set_description(
    group_jid: str,
    description: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_set_description(group_jid, description)


def group_invite_code(
    group_jid: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_invite_code(group_jid)


def group_revoke_invite(
    group_jid: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_revoke_invite(group_jid)


def group_leave(
    group_jid: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_leave(group_jid)


def group_set_add_members_admins_only(
    group_jid: str,
    admins_only: bool,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_set_add_members_admins_only(group_jid, admins_only)


def group_set_messages_admins_only(
    group_jid: str,
    admins_only: bool,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_set_messages_admins_only(group_jid, admins_only)


def group_set_info_admins_only(
    group_jid: str,
    admins_only: bool,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_set_info_admins_only(group_jid, admins_only)


def group_set_picture(
    group_jid: str,
    *,
    mimetype: str,
    base64_data: str,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_set_picture(group_jid, mimetype, base64_data)


def group_delete_picture(
    group_jid: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_delete_picture(group_jid)


def group_membership_requests(
    group_jid: str,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_membership_requests(group_jid)


def group_membership_approve(
    group_jid: str,
    body: Optional[Dict[str, Any]] = None,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_membership_approve(group_jid, body)


def group_membership_reject(
    group_jid: str,
    body: Optional[Dict[str, Any]] = None,
    *,
    session_id: Optional[str] = None,
    channel_secret: Optional[str] = None,
) -> dict:
    sid, sec = _resolve_session(session_id, channel_secret)
    return _channel(sid, sec).group_membership_reject(group_jid, body)


# --- Not in stock HTTP API (parity with JS `advanced`) ---


def set_status(*_args, **_kwargs) -> None:
    raise FeatureNotSupportedError("set_status", "Not mapped in the default API.")


def send_list_message(*_args, **_kwargs) -> None:
    raise FeatureNotSupportedError("send_list_message", "Implement on the server if needed.")
