# Managing Data
This section describes how to manage data in PreciseSearch, specifically how to upsert and delete data.

## Upserting Data
**Upserting** is an operation that combines **insert** and **update**, allowing you to add new vectors or update existing ones based on their Unique ID. When upserting a vector with an ID that already exists in the index, the existing vector and its metadata will be updated with the new values. For new IDs, a new vector will be inserted into the index.

!!! Tip "Batching"
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
        ```python title="Specification of a sparse vector with 3 non-zero values"
        sparse_values = [0.5, 0.8, 0.3]   # Non-zero values
        sparse_indices = [0, 3, 5]        # Their positions in the sparse vector
        ```
        This represents a sparse vector where position 0 has value 0.5, position 3 has value 0.8, etc.

- **Metadata (dictionary)** 
    - Optional key-value pairs with additional item information.
    - For indexes with integrated embedding models, must include a "text" field, whose value will be used for dense vector generation.
    - Example:
```python title="An example of metadata dictionary"
{
    "text": "Product description here",
    "category": "Electronics", 
    "price": 299.99,
    "in_stock": True
}
```

The exact specifics/requirements of an upsert operation depend on your index type (dense or hybrid) and whether you are using an integrated or non-integrated embedding model.
Below, we will go through the different scenarios in detail.

## **Upserting to Dense Indexes**
TODO: Describe the high-leval requirement for upserting to dense indexes. Mirror that in the hybrid section.

### **Dense Index with an Integrated Embedding Model**
To upsert data in a dense index configured with an integrated embedding model, you only need to provide following information for each item in the batch:

- IDs (unique for each item)
- Metadata (containing a "text" field)

The index will automatically generate the dense vector from the "text" field. 
You may include additional metadata (e.g., "price") for filtering or reference, but it will not affect the vector creation.

```python title="Upserting to a dense index with an integrated model"
from vectorstackai import Client
client = Client(api_key="your_api_key_here")

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

### **Dense Index with a Non-Integrated Embedding Model**
To upsert data in a dense index configured with a non-integrated embedding model, you must explicitly provide 
following information for each item in the batch:

- IDs (unique for each item)
- Dense vectors (via `vectors`)
- Metadata (optional)

> **Important:** Ensure the dimensionality of each `vector` matches the dimension specified when you created the index.

```python title="Upserting to a dense index with a non-integrated model"
from vectorstackai import Client
client = Client(api_key="your_api_key_here")

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

## **Upserting to Hybrid Indexes**
When upserting to a hybrid index, you must provide both dense and sparse representations, along with a unique ID and any optional metadata. 
The **key difference** from a dense index is the required **sparse vector**, which you must explicitly supply using `sparse_values` and `sparse_indices`. 

For the dense vector component in hybrid indexes, there are two options, just like with dense indexes:

- Automatically generated (if your index uses an integrated embedding model, in which case you only need to include text in the metadata), or
- Explicitly provided (if your index uses a non-integrated embedding model).


### **Hybrid Index with an Integrated Embedding Model**
For hybrid indexes configured with an integrated embedding model (for the dense vectors), 
you need to supply following information for each item in the batch:

- IDs
- Sparse vectors (via `sparse_values` and `sparse_indices`)
- Metadata (including a `"text"` field, from which dense vectors are automatically generated)

```python title="Upserting to a hybrid index with an integrated model"
from vectorstackai import Client
client = Client(api_key="your_api_key_here")

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

### **With Non-Integrated Embedding Model**
For hybrid indexes configured with a non-integrated embedding model, you must explicitly provide:

- IDs
- Dense vectors (via `vectors`)
- Sparse vectors (via `sparse_values` and `sparse_indices`)
- Metadata (optional fields)

```python title="Upserting to a hybrid index with a non-integrated model"
from vectorstackai import Client
client = Client(api_key="your_api_key_here")

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

## **Deleting Vectors**
To remove vectors from the index, call `delete_vectors` with the `ids` of the vectors you want to delete. This operation:

- Is performed synchronously and cannot be undone.
- All provided `ids` must exist in the index, otherwise an error is raised and no vectors are deleted.

```python title="Deleting vectors by ID"
from vectorstackai import Client
client = Client(api_key="your_api_key_here")

# Connect to an existing index
index = client.connect_to_index("my_index")

# Delete vectors by ID
index.delete_vectors(ids=["doc1", "doc2"])
```
