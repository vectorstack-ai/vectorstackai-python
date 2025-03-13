import warnings
from typing import Any, Dict, List, Optional
import vectorstackai.api_resources as api_resources

class IndexObject:
    """
    Represents a vector store index. Provides methods to interact with the index.
    """
    def __init__(self, index_name: str, connection_params: Dict[str, Any]):
        self.index_name = index_name
        self.connection_params = connection_params
        
        # Get core attributes of the index, used for validation
        _info = self.info()
        self.dimension = _info['dimension']
        self.embedding_model_name = _info['embedding_model_name']
        self.features_type = _info['features_type']
        
        # Scale values for dense and sparse features
        self.dense_similarity_scale = 1.0
        self.sparse_similarity_scale = 1.0
        
    def __repr__(self):
        info = self.info()
        return (f"IndexObject(index_name='{self.index_name}', "
                f"dimension={self.dimension}, "
                f"features_type='{self.features_type}', "
                f"embedding_model_name='{self.embedding_model_name}', "
                f"dense_similarity_scale={self.dense_similarity_scale}, "
                f"sparse_similarity_scale={self.sparse_similarity_scale})")
        
    def __str__(self):
        info = self.info()
        return f"Index(Name: {info['index_name']}, Status: {info['status']})"
   
    def set_similarity_scale(self, 
                            dense_scale: float = 1.0, 
                            sparse_scale: float = 1.0) -> None:
        """Set the scale values for dense and sparse similarity scores in hybrid search.
        
        The similarity in a hybrid index is computed as a weighted sum of the dense and 
        sparse similarity scores:
        
            similarity = dense_similarity * dense_scale + 
                         sparse_similarity * sparse_scale
                         
        This method allows you to set the scale values for the dense and sparse similarity 
        scores. The scale values must be between 0 and 1.
        
        Note:
            In a dense index, the scale values are ignored. The similarity is computed as:
            
                similarity = dense_similarity.
        
        Args:
            dense_scale: The scale value for the dense similarity score.
                Defaults to 1.0.
            sparse_scale: The scale value for the sparse similarity score.
                Defaults to 1.0.
        """
        if self.features_type == 'dense':
            warnings.warn("Setting scale values for dense and sparse features is redundant for dense indexes, since index is dense only; they will not be used for search..")
        
        # Validate scale values
        if dense_scale == 0.0 and sparse_scale == 0.0:
            raise ValueError("At least one of the scale values must be set to a non-zero value.")
        if dense_scale < 0.0 or dense_scale > 1.0:
            raise ValueError("dense_scale must be between 0.0 and 1.0")
        if sparse_scale < 0.0 or sparse_scale > 1.0:
            raise ValueError("sparse_scale must be between 0.0 and 1.0")
        
        self.dense_similarity_scale = dense_scale
        self.sparse_similarity_scale = sparse_scale
        
        if sparse_scale == 0.0:
            warnings.warn("Sparse similarity scale is set to 0.0; sparse features will not be used for search..")
        if dense_scale == 0.0:
            warnings.warn("Dense similarity scale is set to 0.0; dense features will not be used for search..")
             
    def upsert(self, 
               batch_ids: List[str], 
               batch_metadata: Optional[List[Dict[str, Any]]] = None, 
               batch_vectors: Optional[List[List[float]]] = None, 
               batch_sparse_values: Optional[List[List[float]]] = None, 
               batch_sparse_indices: Optional[List[List[int]]] = None) -> None:
        """Upsert a batch of vectors and associated metadata to the index.

        This method upserts a batch of dense or sparse vectors, along with their associated metadata in the index. Note, if a datapoint with the same ID already exists, its metadata, vector, and sparse vector will be updated with the new values.
        
        Args:
            batch_ids: List of unique identifiers for each vector.
            batch_metadata: List of dictionaries containing metadata for each vector. For indexes configured 
                with an integrated embedding model, each dictionary should include a 'text' key whose 
                value is used to compute the embeddings.
            batch_vectors: List of dense vectors (each represented as a list of floats) corresponding to 
                each ID. This field is required for indexes configured with a non-integrated embedding 
                model and should be omitted for indexes configured with an integrated embedding model.
            batch_sparse_values: List of values in the sparse vector (each as a list of floats) 
                corresponding to each ID. Required for upserting in a hybrid index.
            batch_sparse_indices: List of indices in the sparse vector (each as a list of ints) 
                corresponding to each ID. Required for upserting in a hybrid index.
        """
        # Validate input types
        self._validate_upsert_input(batch_ids, batch_metadata, batch_vectors, batch_sparse_values, batch_sparse_indices) 
        
        json_data = {
            "ids": batch_ids,
            "metadata": batch_metadata,
            "vectors": batch_vectors,
            "sparse_values": batch_sparse_values,
            "sparse_indices": batch_sparse_indices,
        }
        response = api_resources.Index.upsert(self.index_name, json_data, self.connection_params)

    def search(self, 
               top_k: int = 10, 
               query_text: str = None, 
               query_vector: List[float] = None, 
               query_sparse_values: List[float] = None,
               query_sparse_indices: List[int] = None,
               return_metadata: bool = True) -> Dict[str, Any]:
        """Search the index for entries similar to the query.
        
        Finds entries in the index that are most similar to the provided query. Query can be a text (if using an integrated embedding model) or a dense vector (if using a non-integrated embedding model), along with a sparse vector (if using a hybrid index).
        
        Args:
            top_k: Number of top-k results to return (should be >= 1).
            query_text: Query text (required for integrated embedding models).
            query_vector: Query vector (required for non-integrated embedding models).
            query_sparse_values: Query sparse values (required for hybrid indexes).
            query_sparse_indices: Query sparse indices (required for hybrid indexes).
            return_metadata: Whether to return metadata for each result (optional, defaults to True).
        
        Returns:
            search_results: List of dictionaries containing search results, sorted in descending order of similarity scores. Each dictionary contains:
            
                - id (str): ID of the retrieved vector.
                - similarity (float): Similarity score between the query and the retrieved vector.
                - metadata (dict): Metadata associated with the vector (present if return_metadata=True, otherwise defaults to an empty dict).
        """
        self._validate_search_input(top_k, query_text, query_vector, query_sparse_values, query_sparse_indices)
        json_data = {
            "top_k": top_k,
            "query_text": query_text,
            "return_metadata": return_metadata,
            "query_vector": query_vector,
            "query_sparse_values": query_sparse_values,
            "query_sparse_indices": query_sparse_indices,
            "dense_similarity_scale": self.dense_similarity_scale,
            "sparse_similarity_scale": self.sparse_similarity_scale
        }
        response = api_resources.Index.search(self.index_name, json_data, self.connection_params)
        return response['search_results']

    def info(self) -> Dict[str, Any]:
        """Get information about the index.

        If the index is still being created (i.e., not yet ready), the returned dictionary 
        includes only `"index_name"` and a `"status"` (which is `"initializing"`). Once the index is configured, the status is set to`"ready"`, the returned dictionary includes additional information.

        Returns:
            index_info: A dictionary containing information about the index with the following keys:
            
                - index_name (str): The name of the index.
                - status (str): The current status of the index ("initializing" or "ready").
                - num_records (int): The number of records stored in the index.
                - dimension (int): The dimensionality of the vectors in the index.
                - metric (str): The distance metric used for similarity search ("cosine" or "dotproduct").
                - features_type (str): The type of features stored ("dense" or "hybrid").
                - embedding_model_name (str): The name of the embedding model used (if applicable).
                - optimized_for_latency (bool): Indicates whether the index is optimized for low-latency queries.
        """
        return api_resources.Index.info(self.index_name, self.connection_params)

    def delete(self, ask_for_confirmation: bool = True) -> None:
        """Deletes the vector index.

        Permanently deletes the index and all its contents. The deletion is asynchronous, 
        and the deleted index cannot be recovered. 

        Args:
            ask_for_confirmation (bool): Whether to ask for confirmation before deleting the index. Defaults to True. When True, the user will be prompted to type 'yes' to confirm deletion.

        Returns:
            None

        Raises:
            ValueError: If the index doesn't exist or cannot be deleted.
        """
        # Ask the user to confirm the deletion
        #########################################################
        if ask_for_confirmation:
            print(f"Are you sure you want to delete index '{self.index_name}'? "
                  f"This action is irreversible.")
            confirm = input("Type 'yes' to confirm: ")
            if confirm != 'yes':
                print("Deletion cancelled.")
                return 
        
        api_resources.Index.delete_index(self.index_name, 
                                         self.connection_params)
        print(f"Request accepted: Index '{self.index_name}' deletion scheduled.")
       
    def delete_vectors(self, ids: List[str]) -> None:
        """Deletes vectors from the index by their IDs.
        
        Permanently removes the specified vectors from the index based on their unique identifiers. The deletion operation cannot be undone. This operation is performed synchronously. Even if one of the IDs does not exist, the operation will raise an error, and the index state will remain unchanged (i.e., no vectors will be deleted).
        
        Args:
            ids: A list of string IDs identifying the vectors to delete from the index.
                Each ID must correspond to a vector previously added to the index.
        """
        assert isinstance(ids, list), "ids must be a list"
        assert len(ids) > 0, "ids must be a non-empty list"
        assert [isinstance(id, str) for id in ids], "each element of ids must be a string"
        
        json_data = {
            "delete_vector_ids": ids,
        }
        api_resources.Index.delete_vectors(self.index_name, json_data, self.connection_params)
        print(f"Successfully deleted {len(ids)} vectors from index {self.index_name}")
    
    def optimize_for_latency(self) -> None:
        """
        Optimizes the index for better latency and throughput.
        
        This method triggers an optimization process in the background to improve the latency and throughput of the index for search operations.
        """
        api_resources.Index.optimize_for_latency(self.index_name, self.connection_params)
        print(f"Request accepted: Index '{self.index_name}' optimization scheduled.")
        
    def _validate_upsert_input(self, 
                               batch_ids: List[str], 
                               batch_metadata: List[Dict[str, Any]], 
                               batch_vectors: List[List[float]], 
                               batch_sparse_values: List[List[float]], 
                               batch_sparse_indices: List[List[int]]) -> None:
        """
        Validate the input for the upsert method.
        
        Args:
            batch_ids: List of unique identifiers for each vector.
            batch_metadata: List of dictionaries containing metadata for each vector. For indexes configured 
                with an integrated embedding model, each dictionary should include a 'text' key whose 
                value is used to compute the embeddings.
            batch_vectors: List of dense vectors (each represented as a list of floats) corresponding to 
                each ID. This field is required for indexes configured with a non-integrated embedding 
                model and should be omitted for indexes configured with an integrated embedding model.
            batch_sparse_values: List of values in the sparse vector (each as a list of floats) 
                corresponding to each ID. Required for upserting in a hybrid index.
            batch_sparse_indices: List of indices in the sparse vector (each as a list of ints) 
                corresponding to each ID. Required for upserting in a hybrid index.
        """
        
        # Validate batch_ids
        num_ids = len(batch_ids)
        assert isinstance(batch_ids, list), "batch_ids must be a list"
      
        # Validate dense vectors 
        #########################################################
        if self.embedding_model_name != 'none':
            # Index is configured with an integrated embedding model
            
            assert batch_metadata is not None, "batch_metadata must be provided for upserting in indexes configured with integrated embedding models."
            if batch_vectors is not None:
                warnings.warn("batch_vectors are not required for upserting in indexes configured with integrated embedding models; "
                             "batch_vectors will be computed directly from the 'text' key in batch_metadata.")
        else:
            # Index is configured with a non-integrated embedding model
            assert batch_vectors is not None, (
                "batch_vectors must be provided for upserting in indexes configured with non-integrated embedding models"
            )
            assert len(batch_vectors) == num_ids, (
                f"length mismatch: batch_vectors length = {len(batch_vectors)} != batch_ids length = {num_ids}"
            )
      
        # Validate batch_metadata
        #########################################################
        if batch_metadata is not None:
            assert isinstance(batch_metadata, list), "batch_metadata must be a list"
            assert [isinstance(x, dict) for x in batch_metadata], "each element of batch_metadata must be a dictionary"
            assert len(batch_metadata) == num_ids, (
                f"length mismatch: batch_metadata length = {len(batch_metadata)} != batch_ids length = {num_ids}"
            )
            
            if self.embedding_model_name != 'none':
                assert ['text' in item.keys() for item in batch_metadata], (
                    "each element of batch_metadata must contain a 'text' key for indexes with "
                    "integrated embedding models. This text will be used to compute the embeddings."
                )
        # Validate sparse vectors and indices
        #########################################################
        if self.features_type == 'hybrid':
            assert batch_sparse_values is not None, "batch_sparse_values must be provided for hybrid indexes"
            assert batch_sparse_indices is not None, "batch_sparse_indices must be provided for hybrid indexes"
            assert isinstance(batch_sparse_values, list), "batch_sparse_values must be a list"
            assert isinstance(batch_sparse_indices, list), "batch_sparse_indices must be a list"
            assert len(batch_sparse_values) == num_ids, (
                f"length mismatch: batch_sparse_values length = {len(batch_sparse_values)} != batch_ids length = {num_ids}"
            )
            assert len(batch_sparse_indices) == num_ids, (
                f"length mismatch: batch_sparse_indices length = {len(batch_sparse_indices)} != batch_ids length = {num_ids}"
            )
            
            for sparse_values, sparse_indices in zip(batch_sparse_values, batch_sparse_indices):
                assert isinstance(sparse_values, list), "each element of batch_sparse_values must be a list"
                assert isinstance(sparse_indices, list), "each element of batch_sparse_indices must be a list"
                assert [isinstance(x, float) for x in sparse_values], "values in batch_sparse_values must be floats"
                assert [isinstance(x, int) for x in sparse_indices], "values in batch_sparse_indices must be ints"
        else:
            # Dense index
            assert batch_sparse_values is None, "batch_sparse_values must be None for dense indexes"
            assert batch_sparse_indices is None, "batch_sparse_indices must be None for dense indexes"
            
    def _validate_search_input(self, 
                              top_k: int, 
                              query_text: str, 
                              query_vector: List[float], 
                              query_sparse_values: List[float], 
                              query_sparse_indices: List[int]) -> None:
        """
        Validate the input for the search method.
        """
        # Validate top_k
        #########################################################
        assert isinstance(top_k, int), "top_k must be an integer"
        assert top_k > 0, "top_k must be greater than 0"
        
        # Validate query_text and query_vector
        #########################################################
        if self.embedding_model_name != 'none':
            # Index is configured with an integrated embedding model
            assert query_text is not None, (
                "query_text must be provided for search in indexes "
                "configured with integrated embedding models"
            )
            if query_vector is not None:
                warnings.warn("query_vector is not required for search in indexes configured "
                              "with integrated embedding model; will not be used for search..")
        else:
            # Index is configured with a non-integrated embedding model
            assert query_vector is not None, "query_vector must be provided for search in indexes configured with non-integrated embedding models"
            if query_text is not None:
                warnings.warn("query_text is not required for search in indexes configured with non-integrated embedding model; "
                              "will not be used for search..")
            
        # Validate query_sparse_values and query_sparse_indices
        #########################################################
        if self.features_type == 'hybrid':
            assert query_sparse_values is not None, "query_sparse_values must be provided for search in hybrid indexes"
            assert query_sparse_indices is not None, "query_sparse_indices must be provided for search in hybrid indexes"
        else:
            # Dense index
            if query_sparse_values is not None or query_sparse_indices is not None:
                warnings.warn("query_sparse_values and query_sparse_indices are not required for search in dense indexes; "
                             "will not be used for search..")