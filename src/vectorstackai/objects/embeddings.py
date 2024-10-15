import requests

class BaseObject:
    response: requests.Response = None

class EmbeddingsObject(BaseObject):
    """
    Object returned by the Embedding API

    Attributes:
        embeddings (List[List[float]]): The list of embeddings returned by the API
    """
    def __init__(self, response):
        self.response = response
        self.embeddings = None
        if response.status_code == 200:
            self.embeddings = response.json()['output']['embeddings']
        
    def __str__(self) -> str:
        if self.embeddings:
            num_embeddings = len(self.embeddings)
            embedding_dims = len(self.embeddings[0])
            return f"EmbeddingsObject(num_embeddings={num_embeddings}, embedding_dims={embedding_dims})"
        else:
            return "Error: EmbeddingsObject(no embeddings returned)"
        
    def __repr__(self) -> str:
        return self.__str__()   