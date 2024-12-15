import requests
from vectorstackai.objects import EmbeddingsObject
from vectorstackai import error
from vectorstackai.utils import raise_error_from_response

class BaseAPIResource(object):
    DEFAULT_TIMEOUT = 300
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json"
    }

class Embedding(BaseAPIResource):
    """
    A class for creating embeddings using the VectorStack API.

    This class provides methods to encode text into embeddings using
    specified models and parameters.
    """

    CLASS_URL = "https://api.vectorstack.ai/embeddings"

    @classmethod
    def encode(cls, texts, model, is_query, instruction, **kwargs):
        """
        Creates a new embedding for the provided input and parameters.

        Args:
            texts(list): A list of strings to be embedded.
            model (str): The name of the model to use for embedding.
            is_query (bool): Whether the input is a query or not.
            instruction (str): Additional instruction for the embedding process.
            **kwargs: Additional keyword arguments.

        Returns:
            EmbeddingsObject: An object containing the generated embeddings and related information.

        Raises:
            VectorStackError: An appropriate subclass of VectorStackError based on the error type.
        """
        
        json_data= {
            'input': {
                'texts': texts,
                'is_query': is_query,
                'instruction': instruction,
            },
            'api_key': kwargs.get("api_key"),
            'model': model,
        } 
        response = requests.post(cls.CLASS_URL, 
                                 headers=cls.HEADERS, 
                                 json=json_data, 
                                 timeout=kwargs.get("request_timeout", cls.DEFAULT_TIMEOUT)) 
       
        if response.status_code != 200:
            raise_error_from_response(response)
            
        return response
    
    
