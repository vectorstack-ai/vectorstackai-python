from typing import Any, List, Optional, Dict

from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

import vectorstackai
import vectorstackai.error as error
from vectorstackai.utils import get_api_key
from vectorstackai.objects import EmbeddingsObject, IndexObject
import vectorstackai.api_resources as api_resources


class Client:
    """VectorStack AI Client for interacting with the VectorStack API.
    
    This client provides methods to:
    - Generate embeddings from text using various models
    - Manage and search vector search indexes
    
    Args:
        api_key (str): Your API key.
        max_retries (int): Maximum number of retries if API call fails.
        timeout (float): Timeout in seconds.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[float] = 30,
    ) -> None:

        self.api_key = api_key or get_api_key()

        self.connection_params = {
            "api_key": self.api_key,
            "request_timeout": timeout,
        }
        self.retry_controller = Retrying(
            reraise=True,
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential_jitter(initial=1, max=16),
            retry=(
                retry_if_exception_type(error.RateLimitError)
                | retry_if_exception_type(error.ServiceUnavailableError)
                | retry_if_exception_type(error.Timeout)
            ),
        )

    def embed(
        self,
        texts: List[str],
        model: str,
        is_query: bool = False,
        instruction: str = "",
    ) -> EmbeddingsObject:
        # Validate input arguments
        if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
            raise ValueError("'texts' must be a list of strings")
        if not isinstance(model, str):
            raise ValueError("'model' must be a string")
        if not isinstance(is_query, bool):
            raise ValueError("'is_query' must be a boolean")
        if not isinstance(instruction, str):
            raise ValueError("'instruction' must be a string")

        for attempt in self.retry_controller:
            with attempt:
                response_json = api_resources.Embedding.encode(
                    texts=texts,
                    model=model,
                    is_query=is_query,
                    instruction=instruction,
                    connection_params=self.connection_params
                )
        return EmbeddingsObject(response_json, batch_size=len(texts))
    
    # High-level endpoints for VectorSearch API
    #########################################################
    def list_indexes(self) -> List[Dict[str, Any]]:
        """
        List info of all the indexes
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing info of all the indexes.
        """
        return api_resources.Index.list_indexes(connection_params=self.connection_params)
  
    def create_index(self, 
                     index_name: str, 
                     embedding_model_name: str, 
                     dimension: Optional[int] = None, 
                     metric: Optional[str] = 'dotproduct', 
                     features_type: Optional[str] = 'hybrid') -> None:
        """
        Create a new vector index
        
        Args:
            index_name (str): Name of the index to create.
            embedding_model_name (str): Name of the embedding model to use. There are two kinds of embedding models:  
                - Integrated models: These are pre-trained models hosted on the vector2search platform.  
                - Non-integrated models: These are custom models hosted on your platform/ application.  
                - Set "embedding_model_name" to None for using your own embedding model (i.e. non-integrated model).
            dimension (int): Vector dimension (required for non-integrated models).
            metric (str): Distance metric for comparing dense and sparse vectors. Must be one of "cosine" or "dotproduct".
            features_type (str): Type of features used in the index. Must be one of "dense" or "hybrid" (sparse + dense).
        """
        json_data = {
            "index_name": index_name,
            "embedding_model_name": embedding_model_name,
            "dimension": dimension,
            "metric": metric,
            "features_type": features_type,
        }
        response_json = api_resources.Index.create_index(json_data=json_data, 
                                                         connection_params=self.connection_params)
        print(f"{response_json['detail']}")
 
    def delete_index(self, index_name: str, ask_for_confirmation: bool = True) -> None:
        """
        Delete a vector index by its name.

        Permanently deletes the specified index and all its contents. The deletion is asynchronous, and the deleted index cannot be recovered.

        Args:
            index_name (str): Name of the index to delete.
            ask_for_confirmation (bool): Whether to ask for confirmation before deleting the index.
        """
        
        # Ask the user to confirm the deletion
        #########################################################
        if ask_for_confirmation:
            print(f"Are you sure you want to delete index '{index_name}'? "
                  f"This action is irreversible.")
            confirm = input("Type 'yes' to confirm: ")
            if confirm != 'yes':
                print("Deletion cancelled.")
                return
        
        response_json = api_resources.Index.delete_index(index_name=index_name, 
                                         connection_params=self.connection_params)
        print(f"{response_json['detail']}")
       
    def get_index_info(self, index_name: str) -> Dict[str, Any]:
        """
        Get info of an index by its name.

        Args:
            index_name (str): Name of the index to get info of.

        Returns:
            Dict[str, Any]: Dictionary containing info of the index.
        """
        info_all_indexes = self.list_indexes()
        for info_index in info_all_indexes:
            if info_index['index_name'] == index_name:
                return info_index
            
        raise ValueError(f"Index {index_name} not found in the list of existing indexes")
    
    def connect_to_index(self, index_name: str) -> IndexObject:
        """
        Connect to an existing vector index and return an IndexObject for further operations.

        This method searches for the index specified by `index_name` within the list of available indexes. If the index exists, it returns an `IndexObject` configured with the current connection parameters, which can be used to perform operations such as upsert, search, and more on the index.

        Args:
            index_name (str): The name of the index to connect to.

        Returns:
            IndexObject: An object that provides methods to interact with the specified vector index.
        """ 
        
        info_all_indexes = self.list_indexes()
        for index in info_all_indexes:
            if index['index_name'] == index_name:
                return IndexObject(index_name=index_name, connection_params=self.connection_params)
            
        raise ValueError(f"Index {index_name} not found in the list of existing indexes")