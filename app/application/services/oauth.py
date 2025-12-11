"""OAuth / auth service placeholders

Implement authentication logic here (create JWTs, verify tokens, manage expirations).
"""

from typing import Optional


class AuthService:
    def create_token(self, subject: str) -> str:
        """Return a JWT for subject (TODO: implement)."""
        raise NotImplementedError()

    def verify_token(self, token: str) -> Optional[str]:
        """Verify token and return subject id, or None if invalid (TODO: implement)."""
        raise NotImplementedError()
