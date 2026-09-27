import pytest

from vectorstackai.objects import IndexObject


def make_index(embedding_model_name="none", features_type="dense"):
    """Build an IndexObject without hitting the network."""
    index = IndexObject.__new__(IndexObject)
    index.index_name = "test-index"
    index.connection_params = {"api_key": "test-key", "request_timeout": 1}
    index.dimension = 2
    index.embedding_model_name = embedding_model_name
    index.features_type = features_type
    index.dense_similarity_scale = 1.0
    index.sparse_similarity_scale = 1.0
    return index


@pytest.fixture
def no_requests(monkeypatch):
    """Record API calls instead of sending them."""
    calls = []
    import vectorstackai.api_resources as api_resources
    for name in ("upsert", "delete_vectors", "get_metadata"):
        monkeypatch.setattr(api_resources.Index, name,
                            lambda *args, _name=name, **kwargs: calls.append(_name))
    return calls


# delete_vectors / get_metadata
#########################################################
def test_delete_vectors_rejects_non_string_ids(no_requests):
    with pytest.raises(AssertionError, match="each element of ids must be a string"):
        make_index().delete_vectors(["a", 1])
    assert no_requests == []


def test_get_metadata_rejects_non_string_ids(no_requests):
    with pytest.raises(AssertionError, match="each element of vector_ids must be a string"):
        make_index().get_metadata(["a", None])
    assert no_requests == []


def test_delete_vectors_and_get_metadata_accept_string_ids(no_requests):
    index = make_index()
    index.delete_vectors(["a", "b"])
    index.get_metadata(["a", "b"])
    assert no_requests == ["delete_vectors", "get_metadata"]


# upsert
#########################################################
def test_upsert_rejects_non_string_batch_ids(no_requests):
    with pytest.raises(AssertionError, match="each element of batch_ids must be a string"):
        make_index().upsert(batch_ids=["a", 2], batch_vectors=[[0.1, 0.2], [0.3, 0.4]])


def test_upsert_rejects_non_dict_metadata(no_requests):
    with pytest.raises(AssertionError, match="each element of batch_metadata must be a dictionary"):
        make_index().upsert(batch_ids=["a", "b"],
                            batch_vectors=[[0.1, 0.2], [0.3, 0.4]],
                            batch_metadata=[{"k": 1}, "not-a-dict"])


def test_upsert_requires_text_key_for_integrated_models(no_requests):
    index = make_index(embedding_model_name="e5-small-v2")
    with pytest.raises(AssertionError, match="must contain a 'text' key"):
        index.upsert(batch_ids=["a", "b"], batch_metadata=[{"text": "x"}, {"title": "y"}])
    assert no_requests == []


def test_upsert_rejects_non_numeric_sparse_values(no_requests):
    index = make_index(features_type="hybrid")
    with pytest.raises(AssertionError, match="values in batch_sparse_values must be numbers"):
        index.upsert(batch_ids=["a"], batch_vectors=[[0.1, 0.2]],
                     batch_sparse_values=[[0.5, "0.8"]], batch_sparse_indices=[[0, 3]])


def test_upsert_rejects_non_int_sparse_indices(no_requests):
    index = make_index(features_type="hybrid")
    with pytest.raises(AssertionError, match="values in batch_sparse_indices must be ints"):
        index.upsert(batch_ids=["a"], batch_vectors=[[0.1, 0.2]],
                     batch_sparse_values=[[0.5, 0.8]], batch_sparse_indices=[[0, 3.0]])


def test_upsert_accepts_integer_sparse_values(no_requests):
    # The hybrid search tutorial passes raw token counts (ints) as sparse values.
    index = make_index(features_type="hybrid")
    index.upsert(batch_ids=["a"], batch_vectors=[[0.1, 0.2]],
                 batch_sparse_values=[[2, 1]], batch_sparse_indices=[[101, 2054]],
                 batch_metadata=[{"text": "x"}])
    assert no_requests == ["upsert"]
