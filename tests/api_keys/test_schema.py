from datetime import timedelta

import pytest
from pydantic import ValidationError

from knowledge_gateway.api_keys.schema import ApiKeyCreate
from knowledge_gateway.utils import utc_now


def test_api_key_create_accepts_future_timezone_aware_expiration() -> None:
    expires_at = utc_now() + timedelta(days=1)

    schema = ApiKeyCreate(expires_at=expires_at)

    assert schema.expires_at == expires_at


def test_api_key_create_rejects_naive_expiration() -> None:
    expires_at = (utc_now() + timedelta(days=1)).replace(tzinfo=None)

    with pytest.raises(ValidationError, match="expires_at must include timezone"):
        ApiKeyCreate(expires_at=expires_at)


def test_api_key_create_rejects_past_expiration() -> None:
    expires_at = utc_now() - timedelta(days=1)

    with pytest.raises(ValidationError, match="expires_at must be in the future"):
        ApiKeyCreate(expires_at=expires_at)
