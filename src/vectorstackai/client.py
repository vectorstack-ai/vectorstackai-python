from typing import Any, List, Optional

from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

import vectorstackai
import vectorstackai.error as error
from vectorstackai.utils import get_api_key
from vectorstackai.objects import EmbeddingsObject
import vectorstackai.api_resources as api_resources
#TODO:
# - Base64 encoding

class Client:
    """VectorStack AI Client

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
                response_json = api_resources.Embedding(
                    connection_params=self.connection_params
                ).encode(
                    texts=texts,
                    model=model,
                    is_query=is_query,
                    instruction=instruction,
                )
        return EmbeddingsObject(response_json, batch_size=len(texts))
    
    def create_index(
        self,
        db_name: str,
        dimension: int,
        index_type: str = "brute_force",
        metric: str = "cosine",
        dtype: str = "float32",
    ) -> Store:
        """Create a new vector store index.
        
        Args:
            db_name (str): Name of the database to create
            dimension (int): Dimension of vectors to be stored
            index_type (str, optional): Type of index. Defaults to "brute_force"
            metric (str, optional): Distance metric to use. Defaults to "cosine"
            dtype (str, optional): Data type of vectors. Defaults to "float32"
        
        Returns:
            Store: A Store instance connected to the newly created index
        """
        Store.create(
            db_name=db_name,
            dimension=dimension,
            index_type=index_type,
            metric=metric,
            dtype=dtype,
            connection_params=self.connection_params
        )
        return self.connect_to_index(db_name)

    def connect_to_index(self, db_name: str) -> Store:
        """Connect to an existing vector store index.
        
        Args:
            db_name (str): Name of the database to connect to
        
        Returns:
            Store: A Store instance connected to the specified index
        """
        return Store(db_name, connection_params=self.connection_params)