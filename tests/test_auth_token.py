import time
from datetime import timedelta

import pytest
from app.application.services import auth_service


def test_create_and_decode_token():
    payload = {"sub": "123", "role": "patient"}
    token = auth_service.create_access_token(data=payload)
    decoded = auth_service.decode_token(token)
    assert decoded["sub"] == "123"
    assert decoded["role"] == "patient"


def test_token_expiry():
    payload = {"sub": "321"}
    # create token with 1 second expiry
    token = auth_service.create_access_token(
        data=payload, expires_delta=timedelta(seconds=1)
    )
    time.sleep(2)
    with pytest.raises(Exception):
        auth_service.decode_token(token)
