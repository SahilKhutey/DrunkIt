"""Unit tests for password policy validation."""

import pytest
from faccp_platform.security.policies import PasswordPolicyError, validate_password


def test_valid_password():
    validate_password("StrongPassword!123")


@pytest.mark.parametrize(
    "password",
    [
        "short",
        "alllowercase123!",
        "ALLUPPERCASE123!",
        "NoNumberPassword!",
        "NoSpecialCharacter123",
    ],
)
def test_invalid_password(password):
    with pytest.raises(PasswordPolicyError):
        validate_password(password)
