import pytest

from server import (
    execution_request_authorized,
    is_loopback_bind,
    validate_server_security,
)


@pytest.mark.parametrize("host", ["127.0.0.1", "::1", "localhost"])
def test_loopback_hosts_are_recognized(host):
    assert is_loopback_bind(host)


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.20", "example.com"])
def test_non_loopback_hosts_are_not_treated_as_local(host):
    assert not is_loopback_bind(host)


def test_legacy_unauthenticated_execution_is_loopback_only():
    assert execution_request_authorized(None, "", "127.0.0.1")
    assert not execution_request_authorized(None, "", "0.0.0.0")


def test_configured_token_is_required_even_on_loopback():
    assert not execution_request_authorized(None, "secret-token", "127.0.0.1")
    assert not execution_request_authorized(
        "Basic secret-token", "secret-token", "127.0.0.1"
    )
    assert not execution_request_authorized(
        "Bearer wrong-token", "secret-token", "127.0.0.1"
    )
    assert execution_request_authorized(
        "Bearer secret-token", "secret-token", "127.0.0.1"
    )


def test_bearer_scheme_is_case_insensitive_and_whitespace_is_trimmed():
    assert execution_request_authorized(
        "bearer   secret-token  ", "secret-token", "10.0.0.8"
    )


def test_non_loopback_bind_fails_closed_without_token():
    with pytest.raises(RuntimeError, match="NEXORA_EXECUTION_TOKEN"):
        validate_server_security("0.0.0.0", "")


def test_loopback_bind_keeps_local_first_default():
    validate_server_security("127.0.0.1", "")


def test_non_loopback_bind_is_allowed_when_token_is_configured():
    validate_server_security("0.0.0.0", "configured-token")



def test_non_loopback_bind_rejects_short_tokens():
    with pytest.raises(RuntimeError, match="at least 32 UTF-8 bytes"):
        validate_server_security("0.0.0.0", "too-short")


def test_non_loopback_bind_accepts_32_byte_token():
    validate_server_security("0.0.0.0", "x" * 32)


def test_unicode_bearer_token_comparison_is_supported():
    token = "🔐" * 8
    assert execution_request_authorized(
        "Bearer " + token, token, "127.0.0.1"
    )
