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
    """VectorStackAI's Client for interacting with proprietary models provided by VectorStackAI.
    
    Currently, the client provides methods to:
    - Generate embeddings from text using domain-specific models (eg. vstackai-law-1)
    
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
        """
        Generates embeddings for a batch of text inputs using the specified model.

        This method encodes a batch of text documents or queries into dense vector 
        representations using the selected embedding model. It supports both 
        document and query embeddings, with an optional instruction for 
        instruction-tuned models.

        Args:
            texts (List[str]): 
                Batch of text strings to be embedded as a list of strings. 
                Each string represents either a document or a query.
            model (str): 
                The name of the embedding model to use (e.g., `"vstackai-law-1"` 
                for legal documents).
            is_query (bool, optional): 
                A flag indicating whether the input texts are queries (`True`) 
                or documents (`False`). Defaults to `False`.
            instruction (str, optional): 
                An optional instruction to guide the model when embedding queries. 
                Recommended for instruction-tuned models. Defaults to an empty string.

        Returns:
            EmbeddingsObject: 
                An object that holds embeddings for the batch of texts. 
                The embeddings are stored as a NumPy array of shape
                `(num_texts, embedding_dimension)`, accesible via the 
                `embeddings` attribute.

        Raises:
            ValueError: 
                If `texts` is not a list of strings.
                If `model` is not a string.
                If `is_query` is not a boolean.
                If `instruction` is not a string.

        Example:
            ```python
            client = vectorstackai.Client(api_key="your_api_key")

            texts = [
                "The defendant was charged with violation of contract terms.",
                "Consumers have 30 days to return a defective product."
            ]
            
            embeddings = client.embed(texts=texts, model="vstackai-law-1", is_query=False)
            
            print(embeddings.embeddings.shape)  # (2, 1536)
            ```
        """ 
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
    
class PreciseSearch:
    """Client for managing PreciseSearch indexes.
    
    PreciseSearch is a vertically integrated search offering, which allows you to search your data in a more efficient way.
    
    Currently, this client provides methods to:
    - List indexes: List all indexes associated with the current API key.
    - Create indexes: Create a new vector index with the specified parameters.
    - Delete indexes: Delete a vector index by its name.
    - Connect to an index: Connect to an existing vector index and return an IndexObject for further operations.
    - Get index information: Retrieve information about a specific vector index.
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
        
    def list_indexes(self) -> List[Dict[str, Any]]:
        """Lists information about all available indexes.
        
        Retrieves metadata for all indexes associated with the current API key.
        
        Returns:
            list_info: A list of dictionaries, where each dictionary contains information about an index with the following keys:
            
                - index_name (str): The name of the index.
                - status (str): The current status of the index ("initializing" or "ready").
                - num_records (int): The number of records stored in the index.
                - dimension (int): The dimensionality of the vectors in the index.
                - metric (str): The distance metric used for similarity search ("cosine" or "dotproduct").
                - features_type (str): The type of features stored ("dense" or "hybrid").
                - embedding_model_name (str): The name of the embedding model used (if applicable).
                - optimized_for_latency (bool): Indicates whether the index is optimized for low-latency queries.
        """
        return api_resources.Index.list_indexes(connection_params=self.connection_params)
  
    def create_index(self, 
                     index_name: str, 
                     embedding_model_name: str = 'none', 
                     dimension: Optional[int] = None, 
                     metric: Optional[str] = 'dotproduct', 
                     features_type: Optional[str] = 'dense') -> None:
        """Creates a new vector index with the specified parameters.
        
        Args:
            index_name: Name of the index to create.
            embedding_model_name: Name of the embedding model to use. There are two kinds of embedding models:
                - Integrated models: These are pre-trained models hosted on the vector2search platform.
                - Non-integrated models: These are custom models hosted on your platform/application.
                - Set "embedding_model_name" to "none" for using your own embedding model (i.e. non-integrated model).
            dimension: Vector dimension (required for non-integrated models).
            metric: Distance metric for comparing dense and sparse vectors. Must be one of "cosine" or "dotproduct".
            features_type: Type of features used in the index. Must be one of "dense" or "hybrid" (sparse + dense).
        """
        # Convert "None" to "none"
        if embedding_model_name == 'None':
            embedding_model_name = 'none'
            
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
        """Deletes a vector index by its name.

        Permanently deletes the specified index and all its contents. 
        The deletion is asynchronous, and the deleted index cannot be recovered. 
        Note, this method is useful for deleting an index without having to connect to it.

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
        
    def index_status(self, index_name: str) -> Dict[str, Any]:
        """Retrieves the status of a specific vector index.
        
        This method retrieves the status of the index specified by `index_name`.
        Here are the possible statuses:
        
        - "initializing": The index is being initialized.
        - "ready": The index is ready for use.
        - "failed": The index failed to initialize.
        - "deleting": The index is being deleted.
        - "undergoing_optimization_for_latency": The index is undergoing optimization for better latency and throughput.
        
        Args:
            index_name: Name of the index to retrieve status for.
            
        Returns:
            index_status (str): The current status of the index.
        """
        return self.index_info(index_name)['status']
       
    def index_info(self, index_name: str) -> Dict[str, Any]:
        """Retrieves information about a specific vector index.
        
        This method searches for the index specified by `index_name` within the list of available indexes. 
        If the index exists, it returns a dictionary containing information about the index. This method 
        is useful to get information about the index without having to connect to it.
        
        Args:
            index_name: Name of the index to retrieve information for.

        Returns:
            index_info: A dictionary containing information about the index with the following keys:
            
                - index_name (str): The name of the index.
                - status (str): The current status of the index ("initializing" or "ready").
                - num_records (int): The number of records stored in the index.
                - dimension (int): The dimensionality of the vectors in the index.
                - metric (str): The distance metric used for similarity search.
                - features_type (str): The type of features stored.
                - embedding_model_name (str): The name of the embedding model used (if applicable).
                - optimized_for_latency (bool): Whether the index is optimized for low-latency queries.
        """
        info_all_indexes = self.list_indexes()
        for info_index in info_all_indexes:
            if info_index['index_name'] == index_name:
                return info_index
            
        raise ValueError(f"Index {index_name} not found in the list of existing indexes")
    
    def connect_to_index(self, index_name: str) -> IndexObject:
        """Connects to an existing vector index and returns an IndexObject for further operations.

        This method searches for the index specified by `index_name` within the list of available indexes. 
        If the index exists, it returns an `IndexObject` configured with the current connection parameters, 
        which can be used to perform operations such as upsert, search, and more on the index.

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
    
 
