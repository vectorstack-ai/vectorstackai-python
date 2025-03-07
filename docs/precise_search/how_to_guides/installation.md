# Installation and Getting Started

## **Installation**
PreciseSearch is a search-as-a-service product by [VectorStackAI](https://vectorstack.ai), designed to provide seamless vector search capabilities. 
Currently, we offer a Python SDK to interact with the PreciseSearch service.
To get started, install the VectorStackAI Python SDK using pip:

```bash title="Installing the VectorStackAI Python SDK" linenums="1"
pip install vectorstackai
```

## **Getting Started**  
Once you have installed the VectorStackAI Python SDK, to use the VectorStack AI SDK, you will need an **API key**. 
You can obtain it by signing up on our [website](https://vectorstack.ai).
Once, you have the API key, you can either set it as an environment variable or pass it directly when initializing the client:

### Option 1: Pass API Key Directly  
```python title="Initializing the client with an API key" linenums="1"
from vectorstackai import PreciseSearch

# Initialize the client with your API key
client = PreciseSearch(api_key="your_api_key_here")
```

### Option 2: Set API Key as Environment Variable  
If you've set the `VECTORSTACK_API_KEY` environment variable, you can initialize the client without explicitly passing the API key:
```python title="Initializing the client using an environment variable" linenums="1"
from vectorstackai import PreciseSearch

# Initialize the client using the API key from environment variables
client = PreciseSearch()
```
This allows for better security and flexibility when managing API credentials. 