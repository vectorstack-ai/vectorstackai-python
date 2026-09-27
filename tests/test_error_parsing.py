import pytest

import vectorstackai
from vectorstackai import error


@pytest.fixture
def client():
    return vectorstackai.PreciseSearch(api_key="test-key", max_retries=1, timeout=2)


def test_structured_error_is_raised_as_its_declared_type(api, client):
    api.respond(403, {"error": {"type": "AuthenticationError", "message": "invalid key",
                                "http_status": 403, "code": "bad_key"}})
    with pytest.raises(error.AuthenticationError) as exc_info:
        client.list_indexes()
    assert exc_info.value.user_message == "invalid key"
    assert exc_info.value.code == "bad_key"


def test_non_json_error_body_is_kept_as_message(api, client):
    api.respond(405, "<html>Method Not Allowed</html>")
    with pytest.raises(error.MethodNotAllowedError, match="Method Not Allowed"):
        client.list_indexes()


def test_json_error_body_without_error_key_is_kept_as_message(api, client):
    api.respond(405, ["unexpected", "shape"])
    with pytest.raises(error.MethodNotAllowedError, match="unexpected"):
        client.list_indexes()
