"""Per-channel (WhatsApp session) operations: JWT + X-Channel-Secret."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from .http import request_bytes, request_json


class Channel:
    """Bound to one session id + channel secret (panel JWT required on all calls)."""

    def __init__(self, session_id: str, channel_secret: str):
        self.session_id = session_id
        self.channel_secret = channel_secret

    def _path(self, suffix: str) -> str:
        return f"/me/sessions/{quote(str(self.session_id), safe='')}{suffix}"

    def _group_path(self, group_jid: str, tail: str) -> str:
        sid = quote(str(self.session_id), safe="")
        gid = quote(str(group_jid), safe="")
        base = f"/me/sessions/{sid}/groups/{gid}"
        return f"{base}{tail}" if tail else base

    def get_channel_secret(self) -> dict:
        sid = quote(str(self.session_id), safe="")
        return request_json("GET", f"/me/sessions/{sid}/channel-secret", auth_bearer=True)

    def rotate_channel_secret(self) -> dict:
        sid = quote(str(self.session_id), safe="")
        return request_json(
            "POST",
            f"/me/sessions/{sid}/channel-secret/rotate",
            body={},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def status(self) -> dict:
        return request_json("GET", self._path("/status"), auth_bearer=True, channel_secret=self.channel_secret)

    def details(self) -> dict:
        return request_json("GET", self._path("/details"), auth_bearer=True, channel_secret=self.channel_secret)

    def qr(self) -> dict:
        return request_json("GET", self._path("/qr"), auth_bearer=True, channel_secret=self.channel_secret)

    def set_webhook(self, webhook_url: str, events: List[str]) -> dict:
        return request_json(
            "POST",
            self._path("/webhook"),
            body={"webhookUrl": webhook_url, "events": events},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def incoming(self) -> dict:
        return request_json("GET", self._path("/incoming"), auth_bearer=True, channel_secret=self.channel_secret)

    def events(self) -> dict:
        return request_json("GET", self._path("/events"), auth_bearer=True, channel_secret=self.channel_secret)

    def calls(self) -> dict:
        return request_json("GET", self._path("/calls"), auth_bearer=True, channel_secret=self.channel_secret)

    def download_inbound_media(self, ticket: str) -> tuple[bytes, str]:
        """GET …/media/:ticket — decrypted file bytes (TTL applies). Ticket is hex."""
        safe = "".join(c for c in str(ticket) if c in "0123456789abcdefABCDEF")
        sid = quote(str(self.session_id), safe="")
        return request_bytes(
            "GET",
            f"/me/sessions/{sid}/media/{safe}",
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def refresh_qr(self) -> dict:
        """POST …/qr/refresh — new pairing QR (unlinked sessions only)."""
        return request_json(
            "POST",
            self._path("/qr/refresh"),
            body={},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_create(
        self, title: str, participants: Optional[List[str]] = None, options: Optional[Dict[str, Any]] = None
    ) -> dict:
        body: Dict[str, Any] = {"title": title, "participants": list(participants or [])}
        if options is not None:
            body["options"] = options
        return request_json(
            "POST",
            f"/me/sessions/{quote(str(self.session_id), safe='')}/groups",
            body=body,
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_get(self, group_jid: str) -> dict:
        return request_json("GET", self._group_path(group_jid, ""), auth_bearer=True, channel_secret=self.channel_secret)

    def group_participants_add(
        self, group_jid: str, participant_ids: List[str], options: Optional[Dict[str, Any]] = None
    ) -> dict:
        body: Dict[str, Any] = {"participantIds": participant_ids}
        if options is not None:
            body["options"] = options
        return request_json(
            "POST",
            self._group_path(group_jid, "/participants/add"),
            body=body,
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_participants_remove(self, group_jid: str, participant_ids: List[str]) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/participants/remove"),
            body={"participantIds": participant_ids},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_admins_promote(self, group_jid: str, participant_ids: List[str]) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/admins/promote"),
            body={"participantIds": participant_ids},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_admins_demote(self, group_jid: str, participant_ids: List[str]) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/admins/demote"),
            body={"participantIds": participant_ids},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_set_subject(self, group_jid: str, subject: str) -> dict:
        return request_json(
            "PATCH",
            self._group_path(group_jid, "/subject"),
            body={"subject": subject},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_set_description(self, group_jid: str, description: str) -> dict:
        return request_json(
            "PATCH",
            self._group_path(group_jid, "/description"),
            body={"description": description},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_invite_code(self, group_jid: str) -> dict:
        return request_json(
            "GET",
            self._group_path(group_jid, "/invite-code"),
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_revoke_invite(self, group_jid: str) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/invite/revoke"),
            body={},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_leave(self, group_jid: str) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/leave"),
            body={},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_set_add_members_admins_only(self, group_jid: str, admins_only: bool) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/settings/add-members-admins-only"),
            body={"adminsOnly": admins_only},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_set_messages_admins_only(self, group_jid: str, admins_only: bool) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/settings/messages-admins-only"),
            body={"adminsOnly": admins_only},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_set_info_admins_only(self, group_jid: str, admins_only: bool) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/settings/info-admins-only"),
            body={"adminsOnly": admins_only},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_set_picture(self, group_jid: str, mimetype: str, base64_data: str) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/picture"),
            body={"mimetype": mimetype, "data": base64_data},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_delete_picture(self, group_jid: str) -> dict:
        return request_json(
            "DELETE",
            self._group_path(group_jid, "/picture"),
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_membership_requests(self, group_jid: str) -> dict:
        return request_json(
            "GET",
            self._group_path(group_jid, "/membership-requests"),
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_membership_approve(
        self, group_jid: str, body: Optional[Dict[str, Any]] = None
    ) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/membership-requests/approve"),
            body=dict(body or {}),
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def group_membership_reject(self, group_jid: str, body: Optional[Dict[str, Any]] = None) -> dict:
        return request_json(
            "POST",
            self._group_path(group_jid, "/membership-requests/reject"),
            body=dict(body or {}),
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def send_message(self, payload: Dict[str, Any]) -> dict:
        return request_json(
            "POST",
            self._path("/messages/send"),
            body=payload,
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def send_chat_state(self, to: str, state: str) -> dict:
        """Typing / recording indicators or clear (`POST …/chat-state`)."""
        if state not in ("typing", "recording", "stop"):
            raise ValueError("state must be 'typing', 'recording', or 'stop'")
        return request_json(
            "POST",
            self._path("/chat-state"),
            body={"to": to, "state": state},
            auth_bearer=True,
            channel_secret=self.channel_secret,
        )

    def send_text(self, to: str, text: str) -> dict:
        return self.send_message({"to": to, "message": text})

    def send_media(
        self,
        to: str,
        *,
        mimetype: str,
        base64_data: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> dict:
        p: Dict[str, Any] = {
            "to": to,
            "media": {"mimetype": mimetype, "data": base64_data},
        }
        if caption is not None:
            p["message"] = caption
        if filename is not None:
            p["media"]["filename"] = filename
        return self.send_message(p)


def channel(session_id: str, channel_secret: str) -> Channel:
    return Channel(session_id, channel_secret)
