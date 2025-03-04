# Index Management

This section covers various operations for managing your indexes, including getting information about specific indexes, listing all indexes, optimizing indexes for performance, and deleting indexes.

## Getting Index Info
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

## Listing Indexes
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

## Optimizing Indexes
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

## Deleting Indexes
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
