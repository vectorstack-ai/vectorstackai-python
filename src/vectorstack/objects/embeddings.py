
class EmbeddingsObject:
    """
    Object returned by the Embedding API

    Attributes:
        embeddings (List[List[float]]): The list of embeddings returned by the API
    """
    def __init__(self, response):
        self.embeddings = response.json()['embeddings']