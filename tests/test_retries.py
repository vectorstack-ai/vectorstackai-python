import base64
import socket

import numpy as np
import pytest

import vectorstackai
from vectorstackai import error
from vectorstackai.api_resources import Index
from vectorstackai.api_resources.base import BaseAPIResource

INDEX_INFO = {"index_name": "idx", "status": "ready", "num_records": 0, "dimension": 2,
              "metric": "dotproduct", "features_type": "dense",
              "embedding_model_name": "none", "optimized_for_latency": False}


def embed(max_retries=3, timeout=2):
    client = vectorstackai.Client(api_key="test-key", max_retries=max_retries, timeout=timeout)
    return client.embed(texts=["hello"], model="vstackai-law-1")


def list_indexes(max_retries=3, timeout=2):
    client = vectorstackai.PreciseSearch(api_key="test-key", max_retries=max_retries, timeout=timeout)
    return client.list_indexes()


# Status codes without VectorStackAI error data map to typed errors
#########################################################
@pytest.mark.parametrize("status, exception_class", [
    (400, error.BadRequestError),
    (401, error.AuthenticationError),
    (403, error.AuthenticationError),
    (404, error.ServiceUnavailableError),
    (408, error.Timeout),
    (429, error.RateLimitError),
    (500, error.InternalServerError),
    (502, error.ServiceUnavailableError),
    (503, error.ServiceUnavailableError),
    (504, error.ServiceUnavailableError),
])
def test_plain_error_status_maps_to_typed_error(api, status, exception_class):
    api.respond(status, "upstream says no")
    with pytest.raises(exception_class, match="upstream says no") as exc_info:
        list_indexes(max_retries=1)
    assert exc_info.value.http_status == status


def test_unknown_plain_error_status_is_generic(api):
    api.respond(418, "teapot")
    with pytest.raises(error.VectorStackAIError, match="Unexpected error: teapot") as exc_info:
        list_indexes(max_retries=1)
    assert type(exc_info.value) is error.VectorStackAIError


# Only transient errors are retried
#########################################################
@pytest.mark.parametrize("status, body", [
    (401, {"error": {"type": "AuthenticationError", "message": "bad key"}}),
    (400, {"error": {"type": "BadRequestError", "message": "bad input"}}),
    (422, "validation failed"),
])
def test_client_errors_are_not_retried(api, status, body):
    api.respond(status, body)
    with pytest.raises(error.VectorStackAIError):
        embed(max_retries=3)
    assert api.hits == 1


@pytest.mark.parametrize("status, body", [
    (429, "slow down"),
    (500, "boom"),
    (503, "unavailable"),
    (429, {"error": {"type": "RateLimitError", "message": "slow down"}}),
])
def test_transient_errors_are_retried_up_to_max_retries(api, status, body):
    api.respond(status, body)
    with pytest.raises(error.VectorStackAIError):
        embed(max_retries=3)
    assert api.hits == 3


def test_embed_recovers_after_transient_errors(api):
    vectors = np.arange(4, dtype=np.float16)
    api.respond(503, "unavailable")
    api.respond(429, "slow down")
    api.respond(200, {"output": {"embeddings": base64.b64encode(vectors.tobytes()).decode()}})
    result = embed(max_retries=3)
    assert api.hits == 3
    np.testing.assert_array_equal(result.embeddings, vectors.reshape(1, -1))


def test_precise_search_retries_transient_errors(api):
    api.respond(503, "unavailable")
    api.respond(503, "unavailable")
    api.respond(200, [INDEX_INFO])
    assert list_indexes(max_retries=3) == [INDEX_INFO]
    assert api.hits == 3


def test_index_object_retries_transient_errors(api):
    api.respond(200, [INDEX_INFO])  # list_indexes (connect_to_index)
    api.respond(200, INDEX_INFO)    # info (IndexObject.__init__)
    api.respond(503, "unavailable")
    api.respond(200, {"search_results": []})
    client = vectorstackai.PreciseSearch(api_key="test-key", max_retries=3)
    index = client.connect_to_index("idx")
    assert index.search(query_vector=[0.1, 0.2], top_k=1) == []
    assert [path for _, path, _ in api.requests][-2:] == ["/precise_search/search/idx"] * 2


def test_urllib3_does_not_retry_on_its_own(api):
    # urllib3 used to retry GETs on 503 + Retry-After behind tenacity's back
    api.respond(503, "unavailable", headers={"Retry-After": "0"})
    with pytest.raises(error.ServiceUnavailableError):
        list_indexes(max_retries=1)
    assert api.hits == 1


# Transport failures map to typed, retryable errors
#########################################################
@pytest.mark.parametrize("call", [embed, list_indexes])
def test_timeout_raises_timeout_error_and_is_retried(api, call):
    api.respond(200, {}, delay=1.0)
    with pytest.raises(error.Timeout):
        call(max_retries=2, timeout=0.2)
    assert api.hits == 2


def test_connection_refused_raises_connection_error_and_is_retried(monkeypatch, retry_waits):
    # Grab a free port and close it, so nothing is listening there
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    monkeypatch.setattr(Index, "CLASS_URL", f"http://127.0.0.1:{port}/precise_search/")

    attempts = []
    send_request = BaseAPIResource._send_request.__func__

    def counting_send_request(cls, *args, **kwargs):
        attempts.append(1)
        return send_request(cls, *args, **kwargs)

    monkeypatch.setattr(BaseAPIResource, "_send_request", classmethod(counting_send_request))

    with pytest.raises(error.APIConnectionError, match="Failed to connect"):
        list_indexes(max_retries=3)
    assert len(attempts) == 3


def test_index_repr_does_not_call_the_api(api):
    api.respond(200, [INDEX_INFO])  # list_indexes (connect_to_index)
    api.respond(200, INDEX_INFO)    # info (IndexObject.__init__)
    index = vectorstackai.PreciseSearch(api_key="test-key").connect_to_index("idx")
    hits = api.hits
    assert repr(index).startswith("IndexObject(index_name='idx', dimension=2")
    assert api.hits == hits
