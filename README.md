# tneenwh (Python)

Python client for the **TNEENWH** WhatsApp HTTP API.

## Install

From the repository root:

```bash
pip install -e ./packages/tneenwh-python
```

## Minimal example

```python
import tneenwh

tneenwh.configure(base_url="http://localhost:3000")
tneenwh.login(email="you@example.com", password="your-secure-password")

tneenwh.set_session("your-session-uuid", "your-channel-secret-hex")
tneenwh.send_text("201234567890@c.us", "Hello from Python")
```

Full method list, examples, and error handling: **`docs/TNEENWH-LIBRARY-REFERENCE.md`**. Short guide: **`docs/TNEENWH-SDK.md`**.

## Requirements

- Python 3.9+
- Standard library only (uses `urllib` — no `requests` dependency)
