# **Searching**

The search method enables you to find the most relevant vectors in your index based on a query. 
It returns a ranked list of the closest matches, sorted by similarity score.

## **Response format**
Each search result (in the returned list) contains:

- `id` – The identifier of the matching document/vector.
- `similarity` – The similarity score for the match (higher is typically more relevant).
- `metadata` – Any additional metadata stored with the vector (only returned if `return_metadata=True`).

```python title="Example showing how to search an index and handle the list of results"
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

## **Required Arguments**
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

## **Optional Arguments**
In addition to these required arguments, you may also specify following **optional arguments**:

- **`top_k` (int, default=10)**  
  The number of results to return. 

- **`return_metadata` (bool, default=True)**  
  When set to True, metadata for each result is returned. 
  If you only need IDs and similarity scores, set this to False to speed up the query.

## **Detailed Search Scenarios**
Below are code examples demonstrating how to search your index based on different configurations. Each example shows the required and optional arguments needed for successful searching.

### **Dense Indexes**
#### **With Integrated Embedding Model**
To search a dense index configured with an integrated embedding model, you only need to provide a `query_text`. The method will automatically generate a dense query vector from this text.

- Required: `query_text` 
- Optional: `top_k`, `return_metadata`

```python title="Searching a dense index with an integrated embedding model"
# Search using query's text
results = index.search(
    query_text="What is a document?", 
    top_k=5
)
```

#### **With Non-Integrated Embedding Model**
To search a dense index configured with a non-integrated embedding model, you must explicitly provide the dense vector representation of the query (via `query_vector`).

- Required: `query_vector` 
- Optional: `top_k`, `return_metadata`

```python title="Searching a dense index with a non-integrated embedding model"
# Search using query's dense vector representation
results = index.search(
    query_vector=[0.1, 0.2, 0.3, 0.4],
    top_k=5
)
```

### **Hybrid Indexes**
A hybrid index combines both dense and sparse vector representations to enhance search quality. 
**Dense vectors** capture the semantic meaning of text (through continuous embeddings), while **sparse vectors** (e.g., TF-IDF or BM25) capture exact keyword matches.

#### **Similarity Score in a Hybrid Index**
When searching, the similarity score between a query and a document is computed as a weighted sum of the query–document similarity in both dense and sparse vector spaces:

- `dense_similarity`: reflects how similar is the query’s dense representation to the document’s dense representation
- `sparse_similarity`: reflects how similar is the query’s sparse representation to the document’s sparse representation

```python title="Similarity score calculation in a hybrid index"
similarity_score = (
    dense_similarity * dense_scale
    + sparse_similarity * sparse_scale
)
```

Here, `dense_scale` and `sparse_scale` are floating-point numbers between 0.0 and 1.0 that control the relative contribution of each representation. 
**By default both are set to 1.0, giving equal weight to the dense and sparse vectors**.
You can adjust these values as needed via the `index.set_similarity_scale()` method. 
For example, to make the sparse representation twice as influential as the dense representation, set:

```python title="Setting the similarity scale for a hybrid index"
index.set_similarity_scale(dense_scale=0.5, sparse_scale=1.0)
```

**Note:** Setting weights to 0.0 for either representation will effectively disable that representation in the final similarity score.

#### **With Integrated Embedding Model**
To search a hybrid index configured with an integrated embedding model, you need to provide the `query_text` and its sparse vector representation (via `query_sparse_values` and `query_sparse_indices`). 
The dense vector will be automatically generated from the `query_text`.

- Required: 
    - `query_text` 
    - `query_sparse_values` 
    - `query_sparse_indices` 
- Optional: `top_k`, `return_metadata`

```python title="Searching a hybrid index with an integrated embedding model"
# Search using text query
results = index.search(
    query_text="What is a document?",
    query_sparse_values=[0.5, 0.8, 0.3],
    query_sparse_indices=[0, 3, 5],
    top_k=5
)
```

#### **With Non-Integrated Embedding Model**
To search a hybrid index configured with a non-integrated embedding model, you must explicitly provide the dense and sparse vector representations of the query. The dense vector is provided via `query_vector` and the sparse vector is provided via `query_sparse_values` and `query_sparse_indices` respectively.

- Required: 
    - `query_vector` 
    - `query_sparse_values` 
    - `query_sparse_indices` 
- Optional: `top_k`, `return_metadata`

```python title="Searching a hybrid index with a non-integrated embedding model"
# Search using text query
results = index.search(
    query_vector=[0.1, 0.2, 0.3, 0.4],
    query_sparse_values=[0.5, 0.8, 0.3],
    query_sparse_indices=[0, 3, 5],
    top_k=5
)
```

