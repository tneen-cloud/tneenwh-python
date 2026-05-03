"""Build a ready-to-send WhatsApp text body for a one-time code (no HTTP call)."""

from __future__ import annotations

from typing import TypedDict


class OtpNotificationParams(TypedDict):
    from_name: str
    receiver_id: str
    otp: str
    user_name: str


def format_otp_notification_message(
    *,
    from_name: str,
    receiver_id: str,
    otp: str,
    user_name: str,
) -> str:
    """Return markdown-friendly text suitable for :func:`send_text`."""
    name = (user_name or "").strip() or "there"
    from_n = (from_name or "").strip() or "Verification"
    code = str(otp or "").strip()
    rid = (receiver_id or "").strip()
    lines = [
        f"Hello *{name}*,",
        "",
        f"Your verification code is: *{code}*",
        "",
        f"— {from_n}",
    ]
    if rid:
        lines.append(f"(Ref: {rid})")
    return "\n".join(lines)
