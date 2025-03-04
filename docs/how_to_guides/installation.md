# Installation and Getting Started

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)


## **Installation**
PreciseSearch is a product by [VectorStackAI](https://vectorstack.ai), designed to provide seamless vector search capabilities. 
Currently, we offer a Python SDK to interact with the PreciseSearch service.
To get started, install the VectorStackAI Python SDK using pip:

```bash
pip install vectorstackai
```

## **Getting Started**  
Once you have installed the VectorStackAI Python SDK, to use the VectorStack AI SDK, you will need an **API key**. 
You can obtain it by signing up on our [website](https://vectorstack.ai).
Once, you have the API key, you can either set it as an environment variable or pass it directly when initializing the client:

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