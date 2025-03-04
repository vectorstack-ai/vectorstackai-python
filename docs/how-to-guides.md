#  How-to Guides for PreciseSearch 

This document provides how-to guides for various tasks which can be performed using the PreciseSearch.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Creating Indexes](#creating-indexes)
    - [Dense Indexes](#creating-dense-indexes)
    - [Hybrid Indexes](#creating-hybrid-indexes)
- [Managing Data](#managing-data)
    - [Upserting Data](#upserting-data)
    - [Deleting Vectors](#deleting-vectors)
- [Searching](#searching)
    - [Required Arguments](#required-arguments)
    - [Detailed Search Scenarios](#detailed-search-scenarios)
- [Index Management](#index-management)
    - [Getting Index Info](#getting-index-info)
    - [Listing Indexes](#listing-indexes)
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
PreciseSearch supports two types of indexes: **Dense** and **Hybrid**.

- **Dense Indexes**: Store and search data using dense embeddings.
- **Hybrid Indexes**: Combine dense embeddings with sparse embeddings to improve search relevance, especially for keyword-based queries.


<a name="creating-dense-indexes"> </a>

### **Dense Indexes** 
Dense indexes are the most common type of vector index. They store embeddings as floating-point arrays. 
When creating a dense index, you have two choices for generating and handling dense embeddings:

1. **Integrated Embeddings**
    
    The index automatically generates embeddings during upsert and search (using a built-in model from VectorStack AI).

2. **Non-Integrated Embeddings**

    You manage the embeddings yourself—meaning you supply embeddings during both upsert and search.

#### Using an Integrated Embedding Model
When you create a dense index with an integrated embedding model, you do not need to specify the vector dimension. The index will automatically:

- Generate dense embeddings from text during upserts.
- Generate embeddings for query text during searches.

The example below creates a dense index with an integrated embedding model (e.g., `e5-small-v2`).
The list of supported embedding models can be found [here](https://vectorstack.ai/docs/embedding-models).

```python
client.create_index(
    index_name="my_dense_index",
    embedding_model_name="e5-small-v2",  # Built-in embedding model
    metric="cosine",  # Similarity metric: "cosine" or "dotproduct"
    features_type="dense"
)
```
#### Using a Non-Integrated Embedding Model
If you prefer to manage your embeddings, set `embedding_model_name="none"` and explicitly provide:
- The dimensionality `(dimension)` of your vectors.
- Dense embeddings during upsert and search.

```python
client.create_index(
    index_name="my_dense_index",
    embedding_model_name="none",  # Indicates you'll provide your own vectors
    dimension=384,  # Specify the dimension of your vectors
    metric="cosine",
    features_type="dense"
)
```

<a name="creating-hybrid-indexes"></a>

### **Hybrid Indexes** 
Hybrid indexes represent each data point with both a dense embedding and a sparse embedding:

- **Dense embeddings** capture semantic similarity.
- **Sparse embeddings** (e.g., BM25, TF-IDF, eg. Splade) capture exact or near-exact term matches.

By combining these two representations, hybrid indexes often yield better search relevance, since they account for both semantic meaning and keyword importance.
> **Note:** For performance reasons, hybrid indexes only support the `dotproduct` metric.


#### Choosing an Embedding Strategy
Similar to dense indexes, hybrid indexes can use either integrated or non-integrated embedding models for the dense embeddings:

1. **Integrated**: 
    The index automatically handles dense embeddings (you only provide sparse embeddings explicitly).
2. **Non-integrated**: 
    You provide your own dense embeddings (in addition to the sparse embeddings).

> **Important:** You must always provide the **sparse embeddings** yourself for hybrid indexes.

#### Using an Integrated Dense Embedding Model
If you rely on a built-in dense embedding model (e.g., `e5-small-v2`), you do not need to specify the dimension. Sparse embeddings must still be provided by the user.

```python
client.create_index(
    index_name="my_hybrid_index",
    embedding_model_name="e5-small-v2",  # Built-in dense embedding model
    metric="dotproduct",                 # Hybrid indexes support only "dotproduct" metric
    features_type="hybrid"
)
```

#### Using a Non-Integrated Dense Embedding Model
For cases where you supply your own dense embeddings, set `embedding_model_name="none"` and specify the `dimension`. 
You will provide both the dense and sparse vectors during upsert and search.

```python
client.create_index(
    index_name="my_custom_hybrid_index",
    embedding_model_name="none",  # Indicates user-provided dense embeddings
    dimension=384,                # Specify vector dimensionality
    metric="dotproduct",          # Hybrid indexes support only "dotproduct" metric
    features_type="hybrid"
)
```

### **Summary**
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


## **Managing Data**
This section below describes how to manage data in PreciseSearch, specifically how to upsert and delete data.

### Upserting Data
**Upserting** is an operation that combines **insert** and **update**, allowing you to add new vectors or update existing ones if the ID already exists. 
To improve performance, our SDK supports **batching**, enabling you to upsert multiple data points in a single call.

On a high level, you need following information for each item for an upsert operation:

- **Unique ID (string)**
    - Required for all items. Must be unique within the index.
    - Used to identify items for retrieval, updates, and deletion.
    - Examples: `"doc_123"`, `"product_456"`, `"user_789"`

- **Dense Vector (required for non-integrated models)**
    - Dense numerical representation of the item, represented as a list of floats.
    - Must match the dimension specified when creating the index.
    - Example: `[0.1, 0.2, ..., 0.9]` (vector of specified dimension)

- **Sparse Vector (required for hybrid indexes)**
    - Sparse representation of the item using two parallel lists:
        - `sparse_values`: Non-zero values in the sparse vector, represented as a list of floats.
        - `sparse_indices`: Positions of those non-zero values, represented as a list of integers.
    - Example:
        ```python
        sparse_values = [0.5, 0.8, 0.3]   # Non-zero values
        sparse_indices = [0, 3, 5]        # Their positions in the sparse vector
        ```
        This represents a sparse vector where position 0 has value 0.5, position 3 has value 0.8, etc.

- **Metadata (dictionary)** 
    - Optional key-value pairs with additional item information.
    - For indexes with integrated embedding models, must include a "text" field, whose value will be used for dense vector generation.
    - Example:

```python
{
    "text": "Product description here",
    "category": "Electronics", 
    "price": 299.99,
    "in_stock": True
}
```

The exact specifics/requirements of an upsert operation depend on your index type (dense or hybrid) and whether you are using an integrated or non-integrated embedding model.
Below, we will go through the different scenarios in detail.

#### Upserting to Dense Indexes

##### With Integrated Embedding Model
For a dense index configured with an integrated embedding model, you only need to provide following information for each item in the batch:

- IDs (unique for each item)
- Metadata (containing a "text" field)

The index will automatically generate the dense vector from the "text" field. 
You may include additional metadata (e.g., "price") for filtering or reference, but it will not affect the vector creation.

```python
# Connect to an existing dense index with integrated model
index = client.connect_to_index("my_dense_index")

# Upsert data - dense vectors will be automatically generated from the 'text' field in metadata
index.upsert(
    batch_ids=["1", "2"],                 
    batch_metadata=[                      
        {"text": "This is the first document to embed", "price": 100},
        {"text": "This is the second document to embed", "price": 200}
    ]
)
```

##### With Non-Integrated Embedding Model
For a dense index configured with a non-integrated embedding model, you must explicitly provide following information for each item in the batch:

- IDs (unique for each item)
- Dense vectors (via `vectors`)
- Metadata (optional)

> **Important:** Ensure the dimensionality of each `vector` matches the dimension specified when you created the index.

```python
# Connect to a dense index with non-integrated model
index = client.connect_to_index("my_dense_index")

# Upsert data with dense vectors specified explicitly
index.upsert(
    batch_ids=["1", "2"],                 
    batch_vectors=[                      
        [0.1, 0.2, 0.3, 0.4],            
        [0.5, 0.6, 0.7, 0.8]
    ],
    batch_metadata=[                      
        {"price": 100},
        {"price": 200}
    ]
)
```

#### Upserting to Hybrid Indexes
When upserting to a hybrid index, you must provide both dense and sparse representations, along with a unique ID and any optional metadata. 
The **key difference** from a purely dense index is the required **sparse vector**, which you must explicitly supply using `sparse_values` and `sparse_indices`. 
The dense vector can either be:

- Automatically generated (if your index uses an integrated embedding model, in which case you only need to include text in the metadata), or
- Explicitly provided (if your index uses a non-integrated embedding model).


##### With Integrated Embedding Model
For hybrid indexes configured with an integrated embedding model (for the dense vectors), you need to supply following information for each item in the batch:

- IDs
- Metadata (including a `"text"` field, from which dense vectors are automatically generated)
- Sparse vectors (via `sparse_values` and `sparse_indices`)

```python
# Connect to a hybrid index with integrated model
index = client.connect_to_index("my_hybrid_index")

# Upsert data - dense vectors will be automatically generated from the 'text' field in metadata
index.upsert(
    batch_ids=["1", "2"],
    batch_metadata=[
        {"text": "This is the first document to embed", "price": 100},
        {"text": "This is the second document to embed", "price": 200}
    ],
    batch_sparse_values=[[0.5, 0.8, 0.3], [0.2, 0.4, 0.6]],
    batch_sparse_indices=[[0, 3, 5], [1, 2, 4]]
)
```

##### With Non-Integrated Embedding Model
For hybrid indexes configured with a non-integrated embedding model, you must explicitly provide:

- IDs
- Dense vectors (via `vectors`)
- Sparse vectors (via `sparse_values` and `sparse_indices`)
- Metadata (optional fields)

```python
# Connect to a hybrid index with non-integrated model
index = client.connect_to_index("my_hybrid_index")

# Upsert data with explicit vectors
index.upsert(
    batch_ids=["1", "2"],
    batch_vectors=[[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
    batch_sparse_values=[[0.5, 0.8, 0.3], [0.2, 0.4, 0.6]],
    batch_sparse_indices=[[0, 3, 5], [1, 2, 4]],
    batch_metadata=[
        {"price": 100},
        {"price": 200}
    ]
)
```

### **Deleting Vectors**
To remove vectors from the index, call `delete_vectors` with the `ids` of the vectors you want to delete. This operation:

- Is performed synchronously and cannot be undone.
- All provided `ids` must exist in the index, otherwise an error is raised and no vectors are deleted.

```python
# Delete vectors by ID
index.delete_vectors(ids=["doc1", "doc2"])
```

## **Searching**

The search method enables you to find the most relevant vectors in your index based on a query. 
It returns a ranked list of the closest matches, sorted by similarity score.

Each search result (in the returned list) contains:

- `id` – The identifier of the matching document/vector.
- `similarity` – The similarity score for the match (higher is typically more relevant).
- `metadata` – Any additional metadata stored with the vector (only returned if `return_metadata=True`).

Below is a simple example of how to handle the list of results returned from `index.search()`:

```python
results = index.search(
    query_text="What is a document?",
    top_k=5,
    return_metadata=True
)

for item in results:
    print("ID:", item["id"])
    print("Similarity:", item["similarity"])
    if "metadata" in item:
        print("Metadata:", item["metadata"])
    print("---")
```

### Required Arguments
Depending on your exact setup, the required inputs for each search can vary. 
Use this table to see which arguments you must provide for each combination of index type and embedding model.

| **Index Type** | **Embedding Model** | **Required Arguments**                                         |
|----------------|----------------------|---------------------------------------------------------------|
| **Dense**      | Integrated          | `query_text`                                                   |
|                | Non-integrated      | `query_vector`                                                 |
| **Hybrid**     | Integrated          | `query_text`, `query_sparse_values`, `query_sparse_indices`    |
|                | Non-integrated      | `query_vector`, `query_sparse_values`, `query_sparse_indices`  |

In the table above, the following terms apply:

- **`query_text` (string)**  
  A text-based query string. For indexes configured with an integrated embedding model, dense vector representation is automatically generated from this text. 

- **`query_vector` (list of floats)**  
  A list of floats representing the dense vector for the query. This is required for indexes configured with non-integrated embedding models, where you handle the dense vector generation yourself.

- **`query_sparse_values` (list of floats)** and **`query_sparse_indices` (list of ints)**  
  The numerical values and their corresponding indices for a sparse representation of the query (e.g., TF-IDF, BM25, etc.). 

### Optional Arguments
In addition to these required arguments, you may also specify following **optional arguments**:

- **`top_k` (int, default=10)**  
  The number of results to return. 

- **`return_metadata` (bool, default=False)**  
  When set to True, metadata for each result is returned. 
  If you only need IDs and similarity scores, leave this as False to speed up the query.

### **Detailed Search Scenarios**
Below are code examples demonstrating how to search your index based on different configurations. Each example shows the required and optional arguments needed for successful searching.

#### Dense Indexes
##### With Integrated Embedding Model
To search a dense index configured with an integrated embedding model, you only need to provide a `query_text`. The method will automatically generate a dense query vector from this text.

- Required: `query_text` 
- Optional: `top_k`, `return_metadata`

```python
# Search using query's text
results = index.search(
    query_text="What is a document?", 
    top_k=5, 
    return_metadata=True
)
```

##### With Non-Integrated Embedding Model
To search a dense index configured with a non-integrated embedding model, you must explicitly provide the dense vector representation of the query (via `query_vector`).

- Required: `query_vector` 
- Optional: `top_k`, `return_metadata`

```python
# Search using query's dense vector representation
results = index.search(
    query_vector=[0.1, 0.2, 0.3, 0.4],
    top_k=5,
    return_metadata=True
)
```

#### Hybrid Indexes
A hybrid index combines both dense and sparse vector representations to enhance search quality. 
**Dense vectors** capture the semantic meaning of text (through continuous embeddings), while **sparse vectors** (e.g., TF-IDF or BM25) capture exact keyword matches.

##### Similarity Score in a Hybrid Index
When searching, the similarity score between a query and a document is computed as a weighted sum of the query–document similarity in both dense and sparse vector spaces:

- `dense_similarity`: reflects how similar is the query’s dense representation to the document’s dense representation
- `sparse_similarity`: reflects how similar is the query’s sparse representation to the document’s sparse representation

```python
similarity_score = (
    dense_similarity * dense_similarity_scale
    + sparse_similarity * sparse_similarity_scale
)
```

Here, `dense_similarity_scale` and `sparse_similarity_scale` are floating-point numbers between 0.0 and 1.0 that control the relative contribution of each representation. 
**By default both are set to 1.0, giving equal weight to the dense and sparse vectors**.
You can adjust these values as needed via the `index.set_similarity_scale()` method. 
For example, to make the sparse representation twice as influential as the dense representation, set:

```python
index.set_similarity_scale(dense_scale=0.5, sparse_scale=1.0)
```

**Note:** Setting weights to 0.0 for either representation will effectively disable that representation in the final similarity score.

##### With Integrated Embedding Model
To search a hybrid index configured with an integrated embedding model, you need to provide the `query_text` and its sparse vector representation (via `query_sparse_values` and `query_sparse_indices`). 
The dense vector will be automatically generated from the `query_text`.

- Required: 
    - `query_text` 
    - `query_sparse_values` 
    - `query_sparse_indices` 
- Optional: `top_k`, `return_metadata`

```python
# Search using text query
results = index.search(
    query_text="What is a document?",
    query_sparse_values=[0.5, 0.8, 0.3],
    query_sparse_indices=[0, 3, 5],
    top_k=5,
    return_metadata=True
)
```

##### With Non-Integrated Embedding Model
To search a hybrid index configured with a non-integrated embedding model, you must explicitly provide the dense and sparse vector representations of the query. The dense vector is provided via `query_vector` and the sparse vector is provided via `query_sparse_values` and `query_sparse_indices` respectively.

- Required: 
    - `query_vector` 
    - `query_sparse_values` 
    - `query_sparse_indices` 
- Optional: `top_k`, `return_metadata`

```python
# Search using text query
results = index.search(
    top_k=5,  # Return top 5 results
    query_vector=[0.1, 0.2, 0.3, 0.4],
    query_sparse_values=[0.5, 0.8, 0.3],
    query_sparse_indices=[0, 3, 5],
    return_metadata=True  # Include metadata in results
)
```

## Index Management
This section covers various operations for managing your indexes, including getting information about specific indexes, listing all indexes, optimizing indexes for performance, and deleting indexes.

### Getting Index Info
To get detailed information about a specific index, use the `get_index_info()` method:

```python
# Get info about a specific index
index_info = client.get_index_info("my_index_name")

# Access specific properties
print(f"Status: {index_info['status']}")
print(f"Number of records: {index_info['num_records']}")
print(f"Dimension: {index_info['dimension']}")
print(f"Metric: {index_info['metric']}")
```

The returned dictionary contains metadata including:

- `index_name`: Name of the index
- `status`: Current status ("initializing" or "ready")
- `num_records`: Number of vectors stored in the index
- `dimension`: Vector dimension
- `metric`: Distance metric used ("cosine" or "dotproduct")
- `features_type`: Type of features stored ("dense" or "hybrid")
- `embedding_model_name`: Name of the integrated embedding model (if any)
- `optimized_for_latency`: Whether the index is optimized for low-latency queries

If the index is still being created (status is `"initializing"`), only basic information will be available. 
Once the index is ready, you'll have access to all metadata fields.

### Listing Indexes
The `list_indexes()` method returns information about all indexes associated with your API key:

```python
# Get a list of all indexes
indexes = client.list_indexes()

# Print information about each index
for index in indexes:
    print(f"Index name: {index['index_name']}")
    print(f"Status: {index['status']}")
    print(f"Number of records: {index['num_records']}")
    print("---")
```

Each index in the returned list contains the same metadata fields as described in the [Getting Index Info](#getting-index-info) section.

### Optimizing Indexes
The `optimize_for_latency()` method triggers an optimization process on the backend to improve search performance. You should call this method if you are experiencing high latency in your search operations (true for indexes with > 500k vectors). This is an asynchronous operation, meaning that the method will return immediately and the optimization will run in the background.

```python
# Connect to an existing index
index = client.connect_to_index("my_index_name")

# Optimize the index for better search performance
index.optimize_for_latency()
```

Key points about optimization:
- The optimization process runs in the background
- The index is available for searches during optimization
- Optimization can improve both latency and throughput of search operations
- The process may take some time depending on the index size (usually under a minute)

### Deleting Indexes
You can delete an index using either the client's `delete_index()` method or the index object's `delete()` method:

```python
# Method 1: Using the client
client.delete_index("my_index_name")

# Method 2: Using the index object
index = client.connect_to_index("my_index_name")
index.delete()
```

Important considerations when deleting indexes:
- Deletion is permanent and cannot be undone
- By default, both methods will ask for confirmation before deletion
- You can bypass the confirmation by setting `ask_for_confirmation=False`:

```python
# Delete without confirmation
client.delete_index("my_index_name", ask_for_confirmation=False)
# or
index.delete(ask_for_confirmation=False)
```

> **Warning**: Be extremely careful when disabling confirmation, as deleted indexes cannot be recovered.
