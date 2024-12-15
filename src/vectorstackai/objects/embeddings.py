import base64
import numpy as np

class EmbeddingsObject:
    """
    Object returned by the Embedding API

    Attributes:
        embeddings (List[List[float]]): The list of embeddings returned by the API
    """
    def __init__(self, response_json, batch_size):
        self.embeddings = None
        # Get the base64 encoded embeddings string
        embeddings_base64 = response_json['output']['embeddings']
        # Decode the base64 string back into bytes
        embeddings_bytes = base64.b64decode(embeddings_base64)
        
        # Convert the byte string back into a NumPy array
        self.embeddings = np.frombuffer(embeddings_bytes, dtype=np.float16).reshape(batch_size, -1)
        
    def __str__(self) -> str:
        if self.embeddings is not None:
            num_embeddings = len(self.embeddings)
            embedding_dims = len(self.embeddings[0])
            return f"EmbeddingsObject(num_embeddings={num_embeddings}, embedding_dims={embedding_dims})"
        else:
            return "Error: EmbeddingsObject(no embeddings returned)"
        
    def __repr__(self) -> str:
        return self.__str__()   