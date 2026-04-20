from pydantic import ValidationError

from app.api.auth import AuthIn


def test_password_over_72_utf8_bytes_is_rejected():
    over_limit_password = "a" * 73

    try:
        AuthIn(username="alice", password=over_limit_password)
        assert False, "Expected ValidationError for password longer than 72 bytes"
    except ValidationError as exc:
        assert "72 bytes" in str(exc)
