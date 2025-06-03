# Creating Indexes

PreciseSearch supports two types of indexes: **Dense** and **Hybrid**.

- **Dense Indexes**: Store and search data using dense embeddings.
- **Hybrid Indexes**: Combine dense embeddings with sparse embeddings to improve search relevance, especially for keyword-based queries.


## **Dense Indexes**
Dense indexes are the most common type of vector index. They store embeddings as floating-point arrays. 
When creating a dense index, you have two choices for generating and handling dense embeddings:

1. **Integrated Embeddings**
    
    The index automatically generates embeddings during upsert and search (using a built-in model from VectorStack AI).

2. **Non-Integrated Embeddings**

    You manage the embeddings yourself—meaning you supply embeddings during both upsert and search.

### **Using an Integrated Embedding Model**
When you create a dense index with an integrated embedding model, you do not need to specify the vector dimension. The index will automatically:

- Generate dense embeddings from text during upserts.
- Generate embeddings for query text during searches.

The example below creates a dense index with an integrated embedding model (e.g., `e5-small-v2`).
The list of supported embedding models can be found [here](https://docs.vectorstack.ai/precise_search/reference.html#vectorstackai.PreciseSearch.create_index).

```python title="Creating a dense index with an integrated embedding model" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Create the index
client.create_index(
    index_name="my_dense_index",
    embedding_model_name="e5-small-v2",  # Built-in embedding model
    metric="cosine",  # Similarity metric: "cosine" or "dotproduct"
    features_type="dense"
)
```

### **Using a Non-Integrated Embedding Model**
If you prefer to manage your embeddings, set `embedding_model_name="none"` and explicitly provide:

- The dimensionality `(dimension)` of your vectors.
- Dense embeddings during upsert and search.

```python title="Creating a dense index with a non-integrated embedding model" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Create the index
client.create_index(
    index_name="my_dense_index",
    embedding_model_name="none",  # Indicates you'll provide your own vectors
    dimension=384,  # Specify the dimension of your vectors
    metric="cosine",
    features_type="dense"
)
```


## **Hybrid Indexes**
Hybrid indexes represent each data point with both a dense embedding and a sparse embedding:

- **Dense embeddings** capture semantic similarity.
- **Sparse embeddings** (e.g., BM25, TF-IDF, eg. Splade) capture exact or near-exact term matches.

By combining these two representations, hybrid indexes often yield better search relevance, since they account for both semantic meaning and keyword importance.

!!! Note "Performance"
    For performance reasons, hybrid indexes only support the `dotproduct` metric.


### **Choosing an Embedding Strategy**
Similar to dense indexes, hybrid indexes can use either integrated or non-integrated embedding models for the dense embeddings:

1. **Integrated**: 
    The index automatically handles dense embeddings (you only provide sparse embeddings explicitly).
2. **Non-integrated**: 
    You provide your own dense embeddings (in addition to the sparse embeddings).

!!! Note "Sparse Embeddings"
    You must always provide the **sparse embeddings** yourself for hybrid indexes.

### **Using an Integrated Dense Embedding Model**
If you rely on a built-in dense embedding model (e.g., `e5-small-v2`), you do not need to specify the dimension. Sparse embeddings must still be provided by the user.

```python title="Creating a hybrid index with an integrated dense embedding model" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

client.create_index(
    index_name="my_hybrid_index",
    embedding_model_name="e5-small-v2",  # Built-in dense embedding model
    metric="dotproduct",                 # Hybrid indexes support only "dotproduct" metric
    features_type="hybrid"
)
```

### **Using a Non-Integrated Dense Embedding Model**
For cases where you supply your own dense embeddings, set `embedding_model_name="none"` and specify the `dimension`. 
You will provide both the dense and sparse vectors during upsert and search.

```python title="Creating a hybrid index with a non-integrated dense embedding model" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

client.create_index(
    index_name="my_custom_hybrid_index",
    embedding_model_name="none",  # Indicates user-provided dense embeddings
    dimension=384,                # Specify vector dimensionality
    metric="dotproduct",          # Hybrid indexes support only "dotproduct" metric
    features_type="hybrid"
)
```

## **Summary**
1. Dense Indexes:
    - Have two options for dense embeddings:
        - Integrated model (`embedding_model_name="e5-small-v2", etc.`)
            - No need to specify dimension during upsert and search.
        - Non-integrated model (`embedding_model_name="none"`)
            - You provide the dimension and the vectors during upsert and search.
    - Both `cosine` or `dotproduct` metrics are supported.

2. Hybrid Indexes:
    - Combines dense + sparse vectors for better search relevance.
    - Similarity is computed as a weighted sum of dense and sparse similarity scores.
    - Dense embeddings can be integrated or user-provided.
    - Sparse embeddings are always user-provided.
    - Only the `dotproduct` metric is supported.

Use these guidelines when creating indexes in **PreciseSearch** to leverage the 
appropriate embedding approach for your use case.


