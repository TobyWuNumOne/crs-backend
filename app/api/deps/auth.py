"""Auth dependency utilities (e.g., get_current_user)

These helpers will be registered as dependencies for routes.
"""

from typing import Optional
from fastapi import Depends, HTTPException


# TODO: Implement token verification using the AuthService


def get_current_user(token: Optional[str] = None):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    # TODO: call AuthService.verify_token
    raise NotImplementedError()
