import requests
from typing import List, Dict, Optional, Any

from vectorstackai.api_resources.base import BaseAPIResource
from vectorstackai.utils import raise_error_from_response

class Index(BaseAPIResource):
    """Vector Index API interface for managing vector databases"""

    #CLASS_URL = "https://api.vectorstack.ai/vector_index"
    CLASS_URL = "http://localhost:8000/"
   
    def __init__(self, db_name: str, connection_params: Dict[str, Any]):
        self.db_name = db_name
        self.CONNECTION_PARAMS = connection_params
        self.validate_index()

    ### Vector Index high-level endpoints
    def validate_index(self):
        self._make_request(method="POST", 
                            endpoint_name="/validate_index", 
                            json_data={"index_name": self.db_name})
    
    @classmethod
    def list_indexes(cls, connection_params: Dict[str, Any]):
        ''' List all indexes'''
        return cls._make_request_class(method="POST", 
                                       endpoint_name="/list_indexes", 
                                       connection_params=connection_params)

    @classmethod
    def create_index(
        cls,
        index_name: str,
        dimension: int,
        index_type: str = "brute_force",
        metric: str = "cosine",
        dtype: str = "float32",
        connection_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new vector index"""
        json_data = {
            "index_name": index_name,
            "dimension": dimension,
            "index_type": index_type,
            "metric": metric,
            "dtype": dtype
        }
        
        return cls._make_request_class(
            method="POST",
            json_data=json_data,
            endpoint_name="/create_index",
            connection_params=connection_params
        ) 