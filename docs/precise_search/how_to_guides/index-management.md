# Index Management

This section covers various operations for managing your indexes, including getting information about specific indexes, listing all indexes, optimizing indexes for performance, and deleting indexes.

## **Getting Index Info**
There are two ways to get detailed information about a specific index:

1. Using the client's `index_info()` method:
```python title="Getting information using the client" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Get info about a specific index
index_info = client.index_info("my_index_name")

# Access specific properties
print(f"Status: {index_info['status']}")
print(f"Number of records: {index_info['num_records']}")
print(f"Dimension: {index_info['dimension']}")
print(f"Metric: {index_info['metric']}")
```

2. Using the index object's `info()` method:
```python title="Getting information using the index object" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Connect to an existing index
index = client.connect_to_index("my_index_name")

# Get info about the index
index_info = index.info()

# Access specific properties
print(f"Status: {index_info['status']}")
print(f"Number of records: {index_info['num_records']}")
```

Both methods return a dictionary containing metadata including:

- `index_name`: Name of the index
- `status`: Current status ("initializing" or "ready")
- `num_records`: Number of vectors stored in the index
- `dimension`: Vector dimension
- `metric`: Distance metric used ("cosine" or "dotproduct")
- `features_type`: Type of features stored ("dense" or "hybrid")
- `embedding_model_name`: Name of the integrated embedding model (if any)
- `optimized_for_latency`: Whether the index is optimized for low-latency queries

!!! Note "Index information during creation"
    If the index is still being created (status is `"initializing"`), only basic information will be available. 
    
    Once the index is ready, you will have access to all metadata fields.

## **Checking Index Status**
The `index_status()` method returns the current status of an index:

```python title="Checking index status" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Get the status of an index
status = client.index_status("my_index_name")

# Print the status
print(f"Index status: {status}")
```

!!! Note "Possible statuses"
    The possible statuses are:

    - "initializing": The index is being initialized.
    - "ready": The index is ready for use.
    - "failed": The index failed to initialize.
    - "deleting": The index is being deleted.
- "undergoing_optimization_for_latency": The index is undergoing optimization for better latency and throughput.

## **Listing Indexes**
The `list_indexes()` method returns information about all indexes associated with your API key:

```python title="Listing all indexes" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

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

## **Optimizing For Latency**

### **Introduction**
When your dataset grows large, searching for the nearest neighbors in high-dimensional vector spaces becomes increasingly resource-intensive. To address this challenge, most modern vector databases use approximate nearest neighbor (ANN) search algorithms. These algorithms are typically built on specialized data structures—such as Inverted File Index (IVF), Hierarchical Navigable Small World (HNSW), or Vamana graphs—that enable fast lookups while preserving a high level of accuracy.

### **Latency Optimization with No Manual Tuning**
Most vector databases require manual configuration of various ANN parameters, such as *nprobe* for IVF or the *number of edges per node* in HNSW. By contrast, ==PreciseSearch is designed to automatically select the best data structure and optimize its parameters, eliminating the need for manual tuning and simplifying setup==.

To optimize for latency in PreciseSearch, you can use the `optimize_for_latency()` method. This method runs an optimization process on the backend to reduce search latency.

- **When to Call**: 
You usually need to call this method only once, ideally after you have loaded most of your data. 
If the size of your index is less than 500,000 vectors, you do not need to call this method.
- **Effect on Indexing**: 
You can still insert additional data afterward, but you will not need to run the optimization again.
- **Asynchronous Execution**: 
Because this operation runs in the background, the method returns immediately while optimization continues behind the scenes.

```python title="Optimizing an index for latency" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Connect to an existing index
index = client.connect_to_index("my_index_name")

# Optimize the index for better search performance
index.optimize_for_latency()
```


## **Deleting Indexes**

!!! Danger "Important considerations when deleting indexes"
    - Deletion is permanent and cannot be undone
    - By default, both methods will ask for confirmation before deletion
    - You can bypass the confirmation by setting `ask_for_confirmation=False`. 
    - Be extremely careful when disabling confirmation, as deleted indexes cannot be recovered.

There are two ways to delete an index:

1. Using the client's `delete_index()` method:
```python title="Deleting using the client" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Delete an index (will ask for confirmation)
client.delete_index("my_index_name")

# Or delete without confirmation
client.delete_index("my_index_name", ask_for_confirmation=False)
```

2. Using the index object's `delete()` method:
```python title="Deleting using the index object" linenums="1"
from vectorstackai import PreciseSearch
client = PreciseSearch(api_key="your_api_key_here")

# Connect to an existing index
index = client.connect_to_index("my_index_name")

# Delete the index (will ask for confirmation)
index.delete()

# Or delete without confirmation
index.delete(ask_for_confirmation=False)
```
