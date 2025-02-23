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
        
    def __str__(self):
        info = self.info()
        return f"Index(Name: {info['index_name']}, Status: {info['status']})"
    
    def upsert(self, 
               batch_ids: List[str], 
               batch_metadata: Optional[List[Dict[str, Any]]] = None, 
               batch_vectors: Optional[List[List[float]]] = None, 
               batch_sparse_values: Optional[List[List[float]]] = None, 
               batch_sparse_indices: Optional[List[List[int]]] = None) -> None:
        """Upsert a batch of vectors and associated metadata to the index.

        This method constructs a JSON payload from the provided vector IDs, metadata, and optionally,
        dense and sparse vector representations, then sends an upsert request to the configured index.

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
               return_metadata: bool = False,
               query_sparse_values: List[float] = None,
               query_sparse_indices: List[int] = None) -> Dict[str, Any]:
        """
        Search for similar vectors in the index.

        This method allows you to search for vectors in the index based on different parameters.
        
        Args:
            top_k (int): Number of top-k results to return (should be >= 1).
            query_text (str): Query text (required for integrated embedding models).
            return_metadata (bool): Whether to return metadata for each result (optional, defaults to False).
            query_vector (List[float]): Query vector (required for non-integrated embedding models).
            query_sparse_values (List[float]): Query sparse values (required for hybrid indexes).
            query_sparse_indices (List[int]): Query sparse indices (required for hybrid indexes).
        
        Returns:
            Search results are returned as a list of dictionaries. The list is sorted in descending order of similarity scores.  
            Each element of the list contains:
            - vector_id (str): ID of the retrieved vector.
            - similarity (float): Similarity score between the query and the retrieved vector.
            - metadata (Dict, optional): Metadata associated with the vector (present if `return_metadata=True`, otherwise defaults to an empty dict).
        """
        self._validate_search_input(top_k, query_text, query_vector, query_sparse_values, query_sparse_indices)
        json_data = {
            "top_k": top_k,
            "query_text": query_text,
            "return_metadata": return_metadata,
            "query_vector": query_vector,
            "query_sparse_values": query_sparse_values,
            "query_sparse_indices": query_sparse_indices,
        }
        return api_resources.Index.search(self.index_name, json_data, self.connection_params)

    def info(self) -> Dict[str, Any]:
        """
        Retrieve detailed information about the index.

        If the index is still being created (i.e., not yet ready), the returned dictionary will only
        include the `index_name` and a `status` set to "initializing". Once the index is fully set up
        (i.e., `status` is "ready"), the dictionary will include additional details.
        
        Returns:
        Dict[str, Any]: A dictionary containing information about the index with the following keys:
            - index_name (str): The name of the index.
            - status (str): The current status of the index.
            - num_records (int): The number of records in the index.
            - dimension (int): The dimensionality of the vectors.
            - metric (str): The distance metric used for similarity search.
            - features_type (str): The type of features (e.g., "dense" or "hybrid").
            - embedding_model_name (str): The name of the embedding model used.
        """
        return api_resources.Index.info(self.index_name, self.connection_params)

    def delete(self, ask_for_confirmation: bool = True) -> None:
        """
        Delete the vector index.

        Permanently deletes the index and all its contents. The deletion is asynchronous, and the deleted index cannot be recovered. 

        Args:
            ask_for_confirmation (bool): Whether to ask for confirmation before deleting the index.
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
       
    def delete_vectors(self, ids: List[str]) -> None:
        """
        Delete vectors from the index by their IDs.

        This method removes the specified vectors from the index. The IDs of the vectors to be deleted
        are provided in the `ids` list.
        
        Args:
            ids (List[str]): A list of IDs of the vectors to be deleted.
        """
        assert isinstance(ids, list), "ids must be a list"
        assert len(ids) > 0, "ids must be a non-empty list"
        assert [isinstance(id, str) for id in ids], "each element of ids must be a string"
        
        json_data = {
            "delete_vector_ids": ids,
        }
        api_resources.Index.delete_vectors(self.index_name, json_data, self.connection_params)
        print(f"Successfully deleted {len(ids)} vectors from index {self.index_name}")
           
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