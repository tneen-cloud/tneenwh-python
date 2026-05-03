# tneenwh (Python)

Python client for the **[TNEENWH](https://pypi.org/project/tneenwh/)** WhatsApp HTTP API — authentication, OTP signup, sessions, outbound messaging, webhooks, and groups (when the server exposes them).

- **PyPI:** [`pip install tneenwh`](https://pypi.org/project/tneenwh/) — package page: https://pypi.org/project/tneenwh/
- **Requirements:** Python 3.9+
- **HTTP:** stdlib only (`urllib`) — no `requests` dependency

The HTTP contract is defined by **`openapi.json`** on the API host (e.g. `GET https://api.tneenwh.com/openapi.json`). Swagger UI is often at **`/api-docs/`**.

---

## Table of contents

1. [Install](#install)
2. [API base URL](#api-base-url)
3. [Setup every script needs](#setup-every-script-needs)
4. [Configuration API](#configuration-api)
5. [Health & authentication](#health--authentication)
6. [Account & credentials](#account--credentials)
7. [Sessions (panel JWT)](#sessions-panel-jwt)
8. [Messaging (default session)](#messaging-default-session)
9. [Channel object (`session(...)`)](#channel-object-session)
10. [Sub-API (`x-api-key`)](#sub-api-x-api-key)
11. [Groups](#groups)
12. [OTP helper (no HTTP)](#otp-helper-no-http)
13. [Not available on stock HTTP mapping](#not-available-on-stock-http-mapping)
14. [Errors](#errors)

---

## Install

```bash
pip install tneenwh
```

From a clone of the TNEENWH repo (editable):

```bash
pip install -e ./packages/tneenwh-python
```

---

## API base URL

Use this deployment as **`base_url`** everywhere (no trailing slash):

**`https://api.tneenwh.com`**

Use the **same host** you open in the browser for the dashboard. Paths like `/me/...` are appended automatically.

**Reverse proxies (Cloudflare):** If `GET /health` returns an HTML error or **403** from Cloudflare, set a browser-like user agent:

```python
tneenwh.configure(
    base_url="https://api.tneenwh.com",
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
)
```

(`user_agent` requires a recent `tneenwh` package; upgrade if `configure` rejects the keyword.)

---

## Setup every script needs

After `import tneenwh`, configure the API origin, log in (stores the panel JWT), and bind the WhatsApp **session** you want to use for `send_*` and channel helpers:

```python
import tneenwh

tneenwh.configure(base_url="https://api.tneenwh.com")
tneenwh.login(email="you@example.com", password="your-secure-password")

tneenwh.set_session("your-session-uuid", "your-channel-secret-hex")
```

Get **`session` UUID** and **`channel_secret`** from the dashboard for that channel. For Sub-API-only flows, set **`set_api_key(...)`** from `GET /me` instead of `login()` (see [Sub-API](#sub-api-x-api-key)).

---

## Configuration API

| Call | Purpose |
|------|---------|
| `configure(base_url=..., bearer_token=..., api_key=..., session_id=..., channel_secret=..., user_agent=...)` | Merge options into global config |
| `get_config()` | Return current config dataclass |
| `set_base_url(url)` | API origin |
| `set_bearer_token(token)` | Panel JWT (`Authorization: Bearer`) |
| `set_api_key(key)` / `set_apikey(key)` | Hex API key for `/v1/...` |
| `set_session(session_id, channel_secret)` | Default channel for messaging helpers |

---

## Health & authentication

```python
import tneenwh

tneenwh.configure(base_url="https://api.tneenwh.com")

tneenwh.health()  # GET /health — often unauthenticated

tneenwh.signup_send_otp(name="Ada", phone="+10000000000", email="a@b.com", password="SecurePass123")
tneenwh.signup_verify(email="a@b.com", code="123456")
# Aliases: generate_otp(**kwargs), request_signup_otp(**kwargs), verify_otp(email=, code=)

tneenwh.login(email="a@b.com", password="SecurePass123")  # stores JWT in config; returns dict with token
tneenwh.logout()  # POST /auth/logout
```

---

## Account & credentials

Requires **`login()`** first (Bearer token).

```python
tneenwh.configure(base_url="https://api.tneenwh.com")
# tneenwh.login(...)  # if not already logged in

tneenwh.me()
tneenwh.profile()
tneenwh.channel_secrets()
tneenwh.rotate_swagger_portal()
```

---

## Sessions (panel JWT)

```python
tneenwh.configure(base_url="https://api.tneenwh.com")
# tneenwh.login(...)

tneenwh.sessions_list()
tneenwh.session_create("My phone")
tneenwh.session_update(session_id, channel_secret, name="Renamed")
tneenwh.session_delete(session_id, channel_secret)
tneenwh.session_disconnect(session_id, channel_secret)
tneenwh.get_channel_secret(session_id)
tneenwh.rotate_channel_secret(session_id, channel_secret)
```

---

## Messaging (default session)

Call **`set_session(id, secret)`** once, or pass **`session_id=`** / **`channel_secret=`** on each call. (Use `base_url="https://api.tneenwh.com"`.)

### Text

```python
tneenwh.configure(base_url="https://api.tneenwh.com")
# tneenwh.login(...) ; tneenwh.set_session(...)

tneenwh.send_text("201234567890@c.us", "Hello from Python")
```

### Raw payload (text, media, location, poll, options — match OpenAPI `ChatSendRequest`)

```python
tneenwh.send_message(
    {"to": "201234567890@c.us", "message": "Hi", "options": {"linkPreview": False}},
)
```

### Media (base64, no `data:` prefix)

```python
import base64

with open("photo.jpg", "rb") as f:
    b64 = base64.standard_b64encode(f.read()).decode("ascii")

tneenwh.send_media(
    "201234567890@c.us",
    mimetype="image/jpeg",
    base64_data=b64,
    caption="Optional caption",
    filename="photo.jpg",
)
```

### QR, status, webhook, inbound queues

Webhook path is always **`/whatsapp/webhook`** (e.g. `https://api.tneenwh.com/whatsapp/webhook` when your HTTPS server uses this host).

```python
tneenwh.session_status()
tneenwh.session_details()
tneenwh.session_qr()
tneenwh.refresh_session_qr()

tneenwh.session_incoming()
tneenwh.session_events()
tneenwh.session_calls()

tneenwh.set_webhook("https://api.tneenwh.com/whatsapp/webhook", ["message", "message_create"])

raw_bytes, content_type = tneenwh.download_inbound_media("hex-ticket-from-webhook")
```

---

## Channel object (`session(...)`)

Bound calls for one session without relying on global `set_session`:

```python
tneenwh.configure(base_url="https://api.tneenwh.com")
# tneenwh.login(...)  # panel JWT required for /me/sessions/...

ch = tneenwh.session("session-uuid", "channel-secret-hex")

ch.status()
ch.details()
ch.qr()
ch.refresh_qr()
ch.set_webhook("https://api.tneenwh.com/whatsapp/webhook", ["message"])

ch.incoming()
ch.events()
ch.calls()

data, ctype = ch.download_inbound_media("ticket")

ch.send_text("201234567890@c.us", "Hi")
ch.send_message({"to": "…@c.us", "message": "x"})
ch.send_media("…@c.us", mimetype="image/png", base64_data=b64, caption="…")

ch.get_channel_secret()
ch.rotate_channel_secret()
```

---

## Sub-API (`x-api-key`)

Use when you only have **API key + channel secret** (no browser JWT). Set the key from **`GET /me`** (`apiKey` field).

```python
import tneenwh

tneenwh.configure(base_url="https://api.tneenwh.com")
tneenwh.set_api_key("hex-api-key-from-me")

tneenwh.v1_sessions_list()

tneenwh.v1_send_message(
    "session-uuid",
    "channel-secret-hex",
    {"to": "201234567890@c.us", "message": "Hello via v1"},
)
```

---

## Groups

All group helpers require **`set_session`** (or `session_id` / `channel_secret` kwargs). Availability depends on your server exposing WhatsApp group routes.

```python
tneenwh.configure(base_url="https://api.tneenwh.com")
# tneenwh.login(...) ; tneenwh.set_session(...)

tneenwh.create_group("Team chat", participants=["201...@c.us"])

tneenwh.group_get("120...@g.us")
tneenwh.group_participants_add("120...@g.us", ["201...@c.us"])
tneenwh.group_participants_remove("120...@g.us", ["201...@c.us"])
tneenwh.group_admins_promote("120...@g.us", ["201...@c.us"])
tneenwh.group_admins_demote("120...@g.us", ["201...@c.us"])

tneenwh.group_set_subject("120...@g.us", "New title")
tneenwh.group_set_description("120...@g.us", "About text")

tneenwh.group_invite_code("120...@g.us")
tneenwh.group_revoke_invite("120...@g.us")
tneenwh.group_leave("120...@g.us")

tneenwh.group_set_add_members_admins_only("120...@g.us", True)
tneenwh.group_set_messages_admins_only("120...@g.us", True)
tneenwh.group_set_info_admins_only("120...@g.us", True)

tneenwh.group_set_picture("120...@g.us", mimetype="image/jpeg", base64_data=b64)
tneenwh.group_delete_picture("120...@g.us")

tneenwh.group_membership_requests("120...@g.us")
tneenwh.group_membership_approve("120...@g.us", body={})
tneenwh.group_membership_reject("120...@g.us", body={})
```

---

## OTP helper (no HTTP)

Build the OTP **message text** for `send_text` (not the signup HTTP OTP):

```python
from tneenwh import format_otp_notification_message, OtpNotificationParams

text = format_otp_notification_message(OtpNotificationParams(code="123456", brand="MyApp"))
```

---

## Not available on stock HTTP mapping

These exist for parity but **raise `FeatureNotSupportedError`** unless your server adds routes:

```python
tneenwh.set_status(...)           # not mapped on default API
tneenwh.send_list_message(...)    # not mapped on default API
```

---

## Errors

```python
import tneenwh
from tneenwh import TneenwhApiError, FeatureNotSupportedError

tneenwh.configure(base_url="https://api.tneenwh.com")
# tneenwh.login(...) ; tneenwh.set_session(...)

try:
    tneenwh.send_text("201234567890@c.us", "Hi")
except FeatureNotSupportedError as e:
    print("Unsupported:", e.feature)
except TneenwhApiError as e:
    print(e.status, e.body)  # JSON body when present
    if e.is_unauthorized():
        ...
```

Helpers: `is_api_error(exc)`, `is_feature_not_supported(exc)`. See **`TneenwhApiError`** predicate methods on the exception instance (`is_config_or_transport_error`, `is_bad_request`, …).

---

## More documentation

| Doc | Content |
|-----|---------|
| Repo **`docs/TNEENWH-LIBRARY-REFERENCE.md`** | Full parity tables, TypeScript mirror, error catalog |
| Repo **`docs/TNEENWH-SDK.md`** | Short onboarding |
| **`openapi.json`** — `GET https://api.tneenwh.com/openapi.json` | Canonical request/response schemas |

MIT License.
