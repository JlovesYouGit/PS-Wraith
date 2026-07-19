"""
middleware.py — Light-ASI LLM Gateway Phase 3
Auth middleware for the HTTP API — validates Bearer tokens per request.
Ruleset reference: LLM_GATEWAY_RULESET.md § 7
"""

import logging
from typing import Optional
from engine.auth.auth import AuthManager, User

logger = logging.getLogger("light-asi.api.middleware")


def extract_bearer(authorization_header: str) -> Optional[str]:
    """Pull the token out of 'Bearer <token>'."""
    if not authorization_header:
        return None
    parts = authorization_header.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def authenticate_request(headers: dict, auth: AuthManager) -> tuple[Optional[User], str]:
    """
    Validate Bearer token from request headers.
    Returns (user, error_message). If user is None, error_message explains why.
    """
    auth_header = headers.get("Authorization", "") or headers.get("authorization", "")
    token = extract_bearer(auth_header)
    if not token:
        return None, "Missing Authorization header. Use: Bearer <token>"
    user = auth.authenticate(token)
    if not user:
        return None, "Invalid or expired token."
    if not auth.check_rate(user):
        return None, f"Rate limit exceeded for role '{user.role}'."
    return user, ""
