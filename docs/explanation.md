## Overview
VectorStack AI provides a flexible vector search solution with two main types of indexes:

### Dense Indexes
Dense indexes store and search using dense vector embeddings - fixed-length arrays of floating point numbers that represent your data in a continuous vector space. These are ideal for:
- Semantic text search
- Image similarity search 
- Recommendation systems
- Any use case where your data can be represented as fixed-length vectors

### Hybrid Indexes
Hybrid indexes combine both dense and sparse vector representations:
    - Dense vectors capture semantic meaning through continuous embeddings
    - Sparse vectors (like TF-IDF or BM25) capture exact keyword matches
    - The hybrid approach often improves search quality by combining the strengths of both representations
    - Search results blend semantic similarity with keyword matching

### Embedding Model Options

For both index types, you have two options for generating vector embeddings:

Note, when creating an index, you can specify if you want to use an integrated embedding model (i.e. embedding models managed/ provided by VectorStack AI) or non-integrated embeddings (i.e. embedding models managed by yourself) for dense embeddings. Sparse embeddings are always managed by yourself.

<details>
<summary>List of supported integrated embedding models</summary>
[`e5-small-v2`, `vstackai-law-1`]
</details>




#### Integrated Embedding Models
- VectorStack AI provides built-in models like `e5-small-v2` that automatically convert text to vectors
- Simply provide text and the model handles the embedding
- Ideal for getting started quickly with text search, no need to manage embedding models yourself

#### Non-Integrated Embedding Models (Custom)
- You provide your own pre-computed vectors
- Gives you complete control over the embedding process
- Allows use of custom models or non-text data types
- Ideal when you need specific embeddings or are working with non-text data

#### How Hybrid Similarity is Computed
The total similarity score is calculated as a weighted sum of the dense similarity and the sparse similarity:

```python
similarity_score = dense_scale * dense_similarity + sparse_scale * sparse_similarity
```
By default, both dense_scale and sparse_scale are 1.0. You can adjust these values at any time to emphasize one representation over the other:
```python
index.set_similarity_scale(dense_scale=0.2, sparse_scale=0.9)
```