from typing import Dict, Any

from vectorstackai.objects import EmbeddingsObject
from vectorstackai.api_resources.base import BaseAPIResource

class Embedding(BaseAPIResource):
    """
    A class for creating embeddings using the VectorStack API.

    This class provides methods to encode text into embeddings using
    specified models and parameters.
    """
    CLASS_URL = "https://api.vectorstack.ai/embeddings"

    @classmethod
    def encode(cls, texts, model, is_query, instruction, connection_params: Dict[str, Any]):
        """
        Creates a new embedding for the provided input and parameters.

        Args:
            texts(list): A list of strings to be embedded.
            model (str): The name of the model to use for embedding.
            is_query (bool): Whether the input is a query or not.
            instruction (str): Additional instruction for the embedding process.
            connection_params (Dict[str, Any]): Connection parameters.
        Returns:
            EmbeddingsObject: An object containing the generated embeddings and related information.

        Raises:
            VectorStackError: An appropriate subclass of VectorStackError based on the error type.
        """
        # Post refactor, we send the API_key in the authorization header. Change embedding server to read from header.
        json_data = {
            'input': {
                'texts': texts,
                'is_query': is_query,
                'instruction': instruction,
            },
            'api_key': connection_params['api_key'], 
            'model': model,
        }

        return cls._make_request_class(
            method="POST",
            json_data=json_data,
            connection_params=connection_params
        )
    
    
