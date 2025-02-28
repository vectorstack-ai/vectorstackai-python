In addition to the documentation, we also have a series of tutorials that cover the basics of the library. In contras to how-to guides, these tutorials will give you a broader overview of the library and its capabilities.

The tutorials will guide you through a set of complete examples/workflows. These practical examples will show you how to use the library, and also provide a template to start building your own applications.

The tutorials assume you have already installed the library and have a valid API key. If you haven't done so yet, you can find the instructions in the [installation guide](installation.md)


## Examples
Below is a list of the available tutorials along with a short description of what they cover.

- [Semantic search on a collection of documents](tutorials/semantic_search_on_documents.ipynb)
    - Workflow to setup semantic search on a collection of documents.
    - Setting up the index with: integrated embedding Model or a non-integrated model (i.e. your own custom model) for generating dense embeddings.
    - Optimizing the index for latency.

- [Hybrid search on a collection of documents](tutorials/hybrid_search_on_documents.ipynb)
    - Workflow to setup hybrid search on a collection of documents, with a focus on the importance of sparse and dense embeddings for hybrid search.
    - Optimizing the hybrid index for latency.
    - Tuning the weights for dense and sparse embeddings in hybrid search, to improve the results.
