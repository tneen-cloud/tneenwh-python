"""HTTP and feature errors."""

from __future__ import annotations


class TneenwhApiError(Exception):
    """Non-2xx response from the API, or transport/config failure (``status == 0``)."""

    def __init__(self, message: str, status: int, body: object = None):
        super().__init__(message)
        self.status = status
        self.body = body

    def is_config_or_transport_error(self) -> bool:
        """Missing token, missing API key, DNS/TLS/network (see ``body``)."""
        return self.status == 0

    def is_informational(self) -> bool:
        return 100 <= self.status < 200

    def is_success(self) -> bool:
        return 200 <= self.status < 300

    def is_redirect(self) -> bool:
        return 300 <= self.status < 400

    def is_client_error(self) -> bool:
        return 400 <= self.status < 500

    def is_server_error(self) -> bool:
        return 500 <= self.status < 600

    def is_bad_request(self) -> bool:
        return self.status == 400

    def is_unauthorized(self) -> bool:
        return self.status == 401

    def is_forbidden(self) -> bool:
        return self.status == 403

    def is_not_found(self) -> bool:
        return self.status == 404

    def is_conflict(self) -> bool:
        return self.status == 409

    def is_gone(self) -> bool:
        return self.status == 410

    def is_payload_too_large(self) -> bool:
        return self.status == 413

    def is_unprocessable_entity(self) -> bool:
        return self.status == 422

    def is_too_many_requests(self) -> bool:
        return self.status == 429

    def is_bad_gateway(self) -> bool:
        return self.status == 502

    def is_service_unavailable(self) -> bool:
        return self.status == 503


class FeatureNotSupportedError(Exception):
    """The stock HTTP server does not expose this WhatsApp feature yet."""

    def __init__(self, feature: str, hint: str = ""):
        msg = f"Not supported by the default API: {feature}"
        if hint:
            msg += f". {hint}"
        super().__init__(msg)
        self.feature = feature


def is_api_error(exc: BaseException) -> bool:
    return isinstance(exc, TneenwhApiError)


def is_feature_not_supported(exc: BaseException) -> bool:
    return isinstance(exc, FeatureNotSupportedError)
