"""
auth.py — Light-ASI LLM Gateway
Token-based authentication and user management.
Ruleset reference: LLM_GATEWAY_RULESET.md § 7.
"""

import hashlib
import hmac
import os
import time
import logging
from dataclasses import dataclass, field
from typing import Optional

from engine.core.constants import (
    TOKEN_EXPIRY_SECONDS, TOKEN_MAX_LIFETIME_SECONDS,
    ROLE_RATE_LIMITS, ROLE_MAX_QUERY_DEPTH,
)

logger = logging.getLogger("light-asi.auth")

VALID_ROLES = {"admin", "developer", "user", "guest"}


# ─── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class User:
    username: str
    role: str
    token: str
    issued_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    request_count: int = 0
    _window_start: float = field(default_factory=time.time, repr=False)
    _window_count: int = field(default=0, repr=False)

    def is_expired(self) -> bool:
        age = time.time() - self.issued_at
        idle = time.time() - self.last_used
        return age > TOKEN_MAX_LIFETIME_SECONDS or idle > TOKEN_EXPIRY_SECONDS

    def rate_ok(self) -> bool:
        limit = ROLE_RATE_LIMITS.get(self.role)
        if limit is None:
            return True  # admin — unlimited
        now = time.time()
        if now - self._window_start > 60:
            # reset 1-minute window
            self._window_start = now
            self._window_count = 0
        self._window_count += 1
        return self._window_count <= limit

    def max_depth(self) -> Optional[int]:
        return ROLE_MAX_QUERY_DEPTH.get(self.role)


# ─── Auth Manager ─────────────────────────────────────────────────────────────

class AuthManager:
    """
    Manages users and Bearer token authentication.
    Tokens are generated with os.urandom (2^256 entropy equivalent via SHA3-256).
    Ruleset § 7.1 — 'tokens generated per-user with 2^256 entropy seed'.
    """

    def __init__(self):
        self._users: dict[str, User] = {}    # username → User
        self._token_map: dict[str, str] = {} # token → username

    # ── User Creation ──────────────────────────────────────────────────────

    def create_user(self, username: str, role: str = "user") -> User:
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role '{role}'. Valid: {VALID_ROLES}")
        if username in self._users:
            raise ValueError(f"User '{username}' already exists.")

        token = self._generate_token(username)
        user = User(username=username, role=role, token=token)
        self._users[username] = user
        self._token_map[token] = username
        logger.info(f"User created: {username} role={role}")
        return user

    def _generate_token(self, username: str) -> str:
        """Generate a token using os.urandom (2^256 entropy via SHA3-256)."""
        entropy = os.urandom(32)  # 256 bits
        payload = f"{username}:{time.time()}".encode()
        raw = hmac.new(entropy, payload, hashlib.sha3_256).hexdigest()
        return raw

    # ── Authentication ─────────────────────────────────────────────────────

    def authenticate(self, token: str) -> Optional[User]:
        """Validate a Bearer token. Returns User or None."""
        username = self._token_map.get(token)
        if not username:
            logger.warning("Auth failed: unknown token")
            return None
        user = self._users[username]
        if user.is_expired():
            logger.warning(f"Auth failed: token expired for {username}")
            self._revoke(username)
            return None
        user.last_used = time.time()
        user.request_count += 1
        return user

    def check_rate(self, user: User) -> bool:
        """Return True if the user is within their rate limit."""
        ok = user.rate_ok()
        if not ok:
            logger.warning(f"Rate limit exceeded: {user.username} ({user.role})")
        return ok

    # ── Revoke ─────────────────────────────────────────────────────────────

    def _revoke(self, username: str) -> None:
        user = self._users.pop(username, None)
        if user:
            self._token_map.pop(user.token, None)
            logger.info(f"Token revoked: {username}")

    def revoke_user(self, username: str) -> None:
        self._revoke(username)

    # ── Listing ────────────────────────────────────────────────────────────

    def list_users(self) -> list[dict]:
        return [
            {
                "username": u.username,
                "role": u.role,
                "requests": u.request_count,
                "expired": u.is_expired(),
            }
            for u in self._users.values()
        ]

    def __repr__(self) -> str:
        return f"AuthManager(users={len(self._users)})"
