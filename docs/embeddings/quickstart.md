# **Embeddings Quickstart**

This guide will show you how to get started with **VectorStackAI Embeddings**. 
You'll learn how to:
<br>
 ✅ Install the SDK
 <br>
 ✅ Obtain an API key
 <br>
 ✅ Generate embeddings for documents and queries
 <br>
 ✅ Perform a similarity search



!!! Note "Code for this quickstart"
    You can find and run the code for this quickstart in this [colab notebook](https://colab.research.google.com/github/vectorstack-ai/vectorstackai-python/blob/main/examples/embeddings/quickstart.ipynb)

## **1. Install the SDK**
**VectorStackAI Embeddings** is an embeddings-as-a-service product by [VectorStackAI](https://vectorstack.ai), 
designed to provide state-of-the-art domain-specific embeddings. 
Currently, we offer a Python SDK to interact with the VectorStackAI Embeddings service.
To get started, install the VectorStackAI Python SDK using pip:

```bash
pip install vectorstackai
```

## **2. Get an API key**
You will need an API key to use the SDK. 
You can get it by signing up on the [VectorStackAI website](https://vectorstack.ai).

## **3. Generating Embeddings**
This section covers generating embeddings for both **documents** and **queries**.

### **3.1 Generating Embeddings for Documents**
To generate embeddings, first import the vectorstackai package and create a client object with your API key:

```python linenums="1"
import vectorstackai

# Replace with your actual API key
api_key = "your_api_key"
client = vectorstackai.Client(api_key=api_key, timeout=30)
```

Once, the client object is created, you can use the `client.embed` method to generate embeddings for a list of documents.

The method takes the following parameters:

- `texts`: A list of text documents to embed
- `model`: The name of the embedding model to use (e.g. 'vstackai-law-1' for legal documents)
- `is_query`: A boolean flag indicating whether the texts are queries (`True`) or documents (`False`)

The method returns an `EmbeddingObject` containing the generated embeddings.
The embeddings are in numpy array format, and can be accessed using the `embeddings` attribute of the `EmbeddingObject`.

For more details on the `embed` method, checkout the API reference [here](reference.md).

```python linenums="6"
# Documents related to law domain (e.g., court cases, consumer contracts, etc.)
documents = [
    "The defendant was charged with violation of contract terms in the lease agreement signed on January 1, 2022.",
    "This contract stipulates that the consumer has 30 days to return the product in case of any manufacturing defects.",
    "In the case of Smith v. Johnson, the court ruled that the plaintiff had the right to claim damages under section 12 of the Consumer Protection Act."
]

# Get embeddings for the legal documents
doc_embeddings = client.embed(texts=documents, model='vstackai-law-1', is_query=False)
doc_embeddings = doc_embeddings.embeddings  # (3, 1536) numpy array
```


### **3.2 Generating Embeddings for Queries**
Now, let's generate embeddings for a query.

Since `vstackai-law-1` is an instruction-tuned model, it is recommended to provide an instruction when embedding queries. This helps guide the model to produce embeddings that are more relevant to the task/instruction.
You can learn more about instruction-tuned models [here](https://instructor-embedding.github.io).

```python linenums="16"
# Encode a query
query = "How many days does the consumer have to return the product?"
query_embedding = client.embed(
    texts=[query], 
    model='vstackai-law-1', 
    is_query=True, 
    instruction='Represent the query for searching legal documents'
)
query_embedding = query_embedding.embeddings  # (1, 1536) numpy array
```

## **4. Computing Similarity**
Once you have embeddings for both documents and queries, you can compute similarity scores to find the most relevant match.

Below, we compute the dot product of the document embeddings and the query embedding to get the similarity scores. You can use other similarity metrics as well (eg. cosine similarity, euclidean distance, etc.).

```python linenums="25"
# Compute similarity between query and documents
similarities = np.dot(doc_embeddings, query_embedding.T)
print(similarities)
# Example output:
# array([[0.355],
#        [0.772],
#        [0.433]])
```

The document with the highest similarity score corresponds to the most relevant match for the query.

## **5. Batch Size Limits**
For optimal performance, it is recommended to generate embeddings by batching multiple texts at once (as shown in the examples above). 
Batching helps reduce the number of API calls and improves throughput.

!!! Warning "Batch Size Limits"
    There are limits to the number of texts you can embed in a single request:

    - `vstackai-law-1`: Maximum of 64 texts per batch

## **6. Conclusion**
This concludes the quickstart guide. You can now use the VectorStackAI Embeddings service to generate embeddings for your documents and queries.