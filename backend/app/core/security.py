"""
Security utilities, SSRF filters, and Cryptographic Audit Chaining for FLOODTWIN RESPONDER.
"""

import hashlib
import ipaddress
import json
import urllib.parse
from typing import Any, Dict, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def compute_audit_hash(
    actor_id: str,
    action: str,
    resource_id: str,
    details: Dict[str, Any],
    previous_hash: Optional[str] = None
) -> str:
    """
    Computes cryptographic SHA-256 Merkle-linked integrity hash for audit event.
    Ensures immutable chaining of system decisions.
    """
    payload = {
        "actor_id": actor_id,
        "action": action,
        "resource_id": resource_id,
        "details": details,
        "previous_hash": previous_hash or "GENESIS_ROOT_HASH_FLOODTWIN_2026"
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_safe_external_url(url_str: str) -> bool:
    """
    SSRF Protection: Rejects localhost, private IP ranges (RFC 1918, RFC 3927),
    and non-HTTP/HTTPS schemes.
    """
    try:
        parsed = urllib.parse.urlparse(url_str)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False

        # Disallow loopback names
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
            return False

        # Attempt to parse IP address
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except ValueError:
            # Domain name (e.g. s3.amazonaws.com)
            pass

        return True
    except Exception:
        return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects defensive HTTP security headers into all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        return response
