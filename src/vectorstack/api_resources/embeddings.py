import requests
import ipdb
from vectorstack.objects import EmbeddingsObject


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
    def encode(cls, input, model, languages, is_query, instruction, **kwargs):
        """
        Creates a new embedding for the provided input and parameters.

        Args:
            input (list): A list of strings to be embedded.
            model (str): The name of the model to use for embedding.
            languages (list): A list of languages corresponding to each input string.
            is_query (bool): Whether the input is a query or not.
            instruction (str): Additional instruction for the embedding process.
            **kwargs: Additional keyword arguments.

        Returns:
            EmbeddingsObject: An object containing the generated embeddings and related information.

        Raises:
            requests.RequestException: If there's an error in the API request.
        """
        
        json_data= {
            'model': model,
            'sentences': input,
            'languages': languages,
            'is_query': is_query,
            'instruction': instruction
        } 
        ipdb.set_trace()
        response = requests.post(cls.CLASS_URL, 
                                 headers=cls.HEADERS, 
                                 json=json_data, 
                                 api_key=kwargs.get("api_key"),
                                 timeout=kwargs.get("timeout", cls.DEFAULT_TIMEOUT)) 

        return EmbeddingsObject(response)