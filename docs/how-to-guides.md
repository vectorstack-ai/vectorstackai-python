#  How-to Guides for PreciseSearch 

This document provides how-to guides for various tasks which can be performed using the PreciseSearch.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Creating Indexes](#creating-indexes)
    - [Dense Indexes](#dense-indexes)
    - [Hybrid Indexes](#hybrid-indexes)
- [Managing Data](#managing-data)
    - [Upserting Data](#upserting-data)
    - [Deleting Vectors](#deleting-vectors)
- [Searching](#searching)
    - [Basic Search](#basic-search)
    - [Advanced Search Options](#advanced-search-options)
- [Index Management](#index-management)
    - [Listing Indexes](#listing-indexes)
    - [Getting Index Info](#getting-index-info)
    - [Optimizing Indexes](#optimizing-indexes)
    - [Deleting Indexes](#deleting-indexes)

## **Installation**
PreciseSearch is a product by VectorStackAI, designed to provide seamless vector search capabilities. 
Currently, we offer a Python SDK to interact with the PreciseSearch service.
To get started, install the VectorStackAI Python SDK using pip:

```bash
pip install vectorstackai
```

## **Getting Started**  
To use the VectorStack AI SDK, you'll need an **API key**. You can obtain it by signing up on our [website](https://vectorstack.ai).
Once, you have the API key, you can either set it as an environment variable or pass it directly when initializing the client.  

### Option 1: Pass API Key Directly  
```python
from vectorstackai import Client

# Initialize the client with your API key
client = Client(api_key="your_api_key_here")
```
### Option 2: Set API Key as Environment Variable  
If you've set the `VECTORSTACK_API_KEY` environment variable, you can initialize the client without explicitly passing the API key:
```python
from vectorstackai import Client

# Initialize the client using the API key from environment variables
client = Client()
```
This allows for better security and flexibility when managing API credentials.

## **Creating Indexes**
PreciseSearch supports two types of indexes: **Dense** and **Hybrid**. Dense indexes store and search using dense embeddings, while hybrid indexes combine dense embeddings with sparse embeddings for improved search quality. 

### Dense Indexes
Dense indexes are the most common type of vector index. They store dense embeddings as floating-point arrays. When creating a dense index, you have two choices to choose from for dense embeddings:

- **Integrated Embeddings**: The index will automatically generate embeddings during upsert and search using an embedding model managed by VectorStack AI.
- **Non-Integrated Embeddings**: The index will require you to compute the embeddings yourself and provide them during upsert and search.

#### Using an Integrated Embedding Model
The following command creates a dense index with an integrated embedding model (e.g., `e5-small-v2`). The index will automatically generate embeddings during upsert and search. Note, in this case, you do not need to specify the dimension of your vectors.
```python
client.create_index(
    index_name="my_dense_index",
    embedding_model_name="e5-small-v2",  # Built-in embedding model
    metric="cosine",  # Similarity metric: "cosine" or "dotproduct"
    features_type="dense"
)
```
#### Using a Non-Integrated Embedding Model
For cases where you manage embeddings yourself, set embedding_model_name="none" and specify the vector dimension. You must provide vectors explicitly during upsert and search.
```python
client.create_index(
    index_name="my_dense_index",
    embedding_model_name="none",  # Indicates you'll provide your own vectors
    dimension=384,  # Specify the dimension of your vectors
    metric="cosine",
    features_type="dense"
)
```

### Hybrid Indexes
Hybrid indexes represent each data point using **both a dense vector and a sparse vector**, combining the strengths of both approaches:

- **Dense embeddings** capture semantic similarity, meaning they help find conceptually related results.
- **Sparse embeddings** (e.g., BM25, TF-IDF, eg. Splade) capture keyword importance, ensuring exact or near-exact term matches.

By integrating both representations, hybrid indexes improve search relevance in scenarios where pure semantic search may miss important keywords, and keyword-based retrieval lacks deeper contextual understanding. Note for performance reasons, hybrid indexes only support the `dotproduct` metric. The similarity of query with data points is computed as a weighted sum of the dense and sparse similarities.

```python
similarity_score = dense_scale * dense_similarity + sparse_scale * sparse_similarity
```

By default, the dense_scale and sparse_scale are set to 1.0 (i.e. equal weights/ importance). You can change these values with:
```python
index.set_similarity_scale(dense_scale=0.2, sparse_scale=0.9)
```

#### Choosing an Embedding Strategy
Similar to dense indexes, hybrid indexes can use either integrated or non-integrated embedding models for the dense embeddings:

- **Integrated**: The index will automatically generate dense embeddings during upsert and search using an embedding model managed by VectorStack AI.
- **Non-integrated**: The index will require you to compute the dense embeddings yourself and provide them during upsert and search.

In contrast to dense indexes, the **sparse embedding** component must always be provided by the user.

#### Using an Integrated Dense Embedding Model
The following command creates a hybrid index with an integrated dense embedding model (e.g., `e5-small-v2`).

```python
client.create_index(
    index_name="my_hybrid_index",
    embedding_model_name="e5-small-v2",  # Built-in dense embedding model
    metric="dotproduct",  # Hybrid indexes support only "dotproduct" metric
    features_type="hybrid"
)
```

#### Using a Non-Integrated Dense Embedding Model
For cases where you manage dense embeddings yourself, set embedding_model_name="none" and specify the vector dimension.
```python
client.create_index(
    index_name="my_custom_hybrid_index",
    embedding_model_name="none",  # Indicates user-provided dense embeddings
    dimension=384,  # Specify vector dimensionality
    metric="dotproduct",  # Hybrid indexes support only "dotproduct" metric
    features_type="hybrid"
)
```

## **Managing Data**

### Upserting Data

"Upsert" is a combination of "insert" and "update" - it adds new vectors or updates existing ones if the ID already exists.

#### Upserting to a Dense Index with Integrated Model

```python
# Connect to an existing index
index = client.connect_to_index("my_dense_index")

# Upsert data
index.upsert(
    batch_ids=["doc1", "doc2"],
    batch_metadata=[
        {"text": "This is the first document", "category": "A"},
        {"text": "This is the second document", "category": "B"}
    ]
)
```

### Deleting Vectors

You can delete vectors from an index by their IDs:

```python
# Delete vectors by ID
index.delete_vectors(ids=["doc1", "doc2"])
```

## Searching

### Basic Search

```python
# Search using text query
results = index.search(
    top_k=5,  # Return top 5 results
    query_text="What is a document?",
    return_metadata=True  # Include metadata in results
)
```

## Index Management

### Listing Indexes

You can list all your indexes:

```python
# Get a list of all indexes
indexes = client.list_indexes()
```

### Getting Index Info

```python
# Get info about a specific index
index_info = client.get_index_info("my_dense_index")
```

### Optimizing Indexes

```python
# Optimize the index for better latency
index.optimize_for_latency()
```

### Deleting Indexes

```python
# Delete an index
client.delete_index("my_dense_index")
