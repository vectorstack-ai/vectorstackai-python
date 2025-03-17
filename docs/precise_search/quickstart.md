# **PreciseSearch Quickstart**

This guide will show you how to get started with **PreciseSearch**. 

!!! Note "Code for this quickstart"
    You can find and run the code for this quickstart in [Colab Notebook](https://colab.research.google.com/github/vectorstack-ai/vectorstackai-python/blob/add_vector_store_resource/examples/quickstart.ipynb)

## **1. Install the SDK**
**PreciseSearch** is a search-as-a-service product by [VectorStackAI](https://vectorstack.ai), 
designed to provide seamless vector search capabilities. 
Currently, we offer a Python SDK to interact with the PreciseSearch service.
To get started, install the VectorStackAI Python SDK using pip:

```bash
pip install vectorstackai
```

## **2. Get an API key**
You will need an API key to use the SDK. 
You can get it by signing up on the [VectorStackAI website](https://vectorstack.ai).

## **3. Create an index**
**PreciseSearch** supports two types of indexes: Dense Indexes and Hybrid Indexes.
Dense indexes search over dense vector representations of the data, where 
as hybrid indexes search over a combination of dense 
and sparse representations of the data. 

In this quickstart, you will create a dense index with an integrated embedding model (hosted by [VectorStackAI](https://vectorstack.ai)).
With dense indexes configured with an integrated embedding model, during upsert and search, you only need to provide the text data.
**PreciseSearch** will generate the dense vector representations of the data automatically.

```python linenums="1"
from vectorstackai import PreciseSearch
import time

# Initialize the client with your API key
client = PreciseSearch(api_key="your_api_key")

# Create the index with an integrated embedding model (e.g., 'e5-small-v2')
client.create_index(index_name="my_dense_index", embedding_model_name="e5-small-v2")

# Wait for the index to be ready
while client.index_status(index_name="my_dense_index") != "ready":
    time.sleep(2)
    print("Index is not ready yet. Waiting for 2 seconds...")

index = client.connect_to_index(index_name="my_dense_index")
```

!!! Note "Learn More"
    To read about the different types of indexes you can create with **PreciseSearch**, see the [Creating Indexes](./how_to_guides/creating-indexes.md) guide.

## **4. Upsert Data into the Index**
To upsert data into the index, you need to provide the text data and assign a unique ID to each data point.

For this example, let's create a dataset with *10 random facts about food and history*.

```python linenums="18"
dataset = [
    {"id": "1", "text": "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after just 38 minutes."},
    {"id": "2", "text": "Ancient Romans used bread as plates. After the meal, these edible plates were either eaten or given to the poor."},
    {"id": "3", "text": "The first chocolate bar was made in England by Fry's in 1847, marking the beginning of the modern chocolate industry."},
    {"id": "4", "text": "The Battle of Hastings in 1066 changed English history forever when William the Conqueror defeated King Harold II."},
    {"id": "5", "text": "The Great Wall of China took over 2000 years to build, with construction starting in the 7th century BCE."},
    {"id": "6", "text": "Ketchup was sold as medicine in the 1830s to treat diarrhea, indigestion, and other stomach problems."},
    {"id": "7", "text": "Pizza was invented in Naples, Italy in the late 1700s. The classic Margherita pizza was created in 1889."},
    {"id": "8", "text": "The first Thanksgiving feast in 1621 lasted for three days and included deer, fish, and wild fowl."},
    {"id": "9", "text": "The signing of the Magna Carta in 1215 limited the power of English monarchs and influenced modern democracy."},
    {"id": "10", "text": "During World War II, carrots were promoted by the British as helping pilots see better at night to hide radar technology."}
]

# Parse the ids and texts for batch upsert
batch_ids = [item['id'] for item in dataset] 
batch_metadata = [{'text': item['text']} for item in dataset] 

# Upsert the data into the index
index.upsert(batch_ids=batch_ids, 
             batch_metadata=batch_metadata)

# Once the upsert is complete, you can check the number of vectors in the index via the index info
index_info = index.info()
for key, value in index_info.items():
    print(f"{key}: {value}")
```

The index info will look like this:
```
index_name: my_dense_index
num_records: 10
dimension: 384
metric: dotproduct
features_type: dense
status: ready
embedding_model_name: e5-small-v2
optimized_for_latency: False
```

!!! Note "Learn More"
    For more details, see the How-To Guide on [Upserting Data](./how_to_guides/managing-data.md).

## **5. Search the index**
Now that you have your index ready, you can search it.
In this example, you will search the index for the query "Where was pizza invented?".

Since the index is configured with an integrated embedding model, you only need to provide the query text. 

```python linenums="42"
# Search the index
search_results = index.search(query_text="Where was pizza invented?", 
                              top_k=5)

# Print the results
for result in search_results:
    print(f"ID: {result['id']}, Similarity: {result['similarity']:.2f}, Text: {result['metadata']['text']}")
```
Notice that the results are sorted in descending order of similarity, and contain results relevant to the query:

```
ID: 7, Similarity: 0.90, Text: Pizza was invented in Naples, Italy in the late 1700s. The classic Margherita pizza was created in 1889.
ID: 3, Similarity: 0.85, Text: The first chocolate bar was made in England by Fry's in 1847, marking the beginning of the modern chocolate industry.
ID: 5, Similarity: 0.80, Text: The Great Wall of China took over 2000 years to build, with construction starting in the 7th century BCE.
ID: 1, Similarity: 0.75, Text: The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after just 38 minutes.
```


!!! Note "Learn More"
    For more details, see the How-To Guide on [Searching the Index](./how_to_guides/searching.md).

## **6. Clean up**
Once you are done with the quickstart, you can delete the index.

```python
index.delete(ask_for_confirmation=False)
```
