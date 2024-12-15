# Implement a class for the vector store API
# Should support the following operations:
# - Create index
# - Upsert vectors
# - Search for vectors
# - Delete vectors
# - Get info about the vector store
# - Delete the vector store

import requests
from typing import List, Dict, Optional, Any

from vectorstackai.api_resources.base import BaseAPIResource
from vectorstackai.utils import raise_error_from_response

class Store(BaseAPIResource):
    """Vector Store API interface for managing vector databases"""

    CLASS_URL = "https://api.vectorstack.ai/vector_store"

    def __init__(self, db_name: str, connection_params: Dict[str, Any]) -> None:
        super().__init__()
        self.db_name = db_name
        self.connection_params = connection_params

    @classmethod
    def create(
        cls,
        db_name: str,
        dimension: int,
        index_type: str = "brute_force",
        metric: str = "cosine",
        dtype: str = "float32",
        connection_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new vector store"""
        json_data = {
            "input": {
                "db_name": db_name,
                "dimension": dimension,
                "index_type": index_type,
                "metric": metric,
                "dtype": dtype
            },
            "api_key": connection_params.get("api_key")
        }
        
        return cls._make_request(
            method="POST",
            json_data=json_data,
            timeout=connection_params.get("request_timeout", cls.DEFAULT_TIMEOUT)
        )

    def upsert(
        self,
        vector_ids: List[str],
        vectors: List[List[float]],
        metadata: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upsert vectors into the store"""
        json_data = {
            "input": {
                "db_name": self.db_name,
                "vector_ids": vector_ids,
                "vectors": vectors,
                "metadata": metadata
            },
            "api_key": self.connection_params.get("api_key")
        }
        
        return self._make_request(
            method="POST",
            json_data=json_data,
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT)
        )

    def search(
        self,
        query: List[float],
        top_k: int = 10,
        return_metadata: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        json_data = {
            "input": {
                "db_name": self.db_name,
                "query": query,
                "top_k": top_k,
                "return_metadata": return_metadata
            },
            "api_key": self.connection_params.get("api_key")
        }
        
        return self._make_request(
            method="POST",
            json_data=json_data,
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT)
        )

    def delete_vectors(self, vector_ids: List[str], **kwargs) -> Dict[str, Any]:
        """Delete vectors by their IDs"""
        json_data = {
            "input": {
                "db_name": self.db_name,
                "vector_ids": vector_ids
            },
            "api_key": self.connection_params.get("api_key")
        }
        
        return self._make_request(
            method="DELETE",
            json_data=json_data,
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT)
        )

    def info(self, **kwargs) -> Dict[str, Any]:
        """Get information about the vector store"""
        json_data = {
            "input": {
                "db_name": self.db_name
            },
            "api_key": self.connection_params.get("api_key")
        }
        
        return self._make_request(
            method="GET",
            json_data=json_data,
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT)
        )

    def delete(self, **kwargs) -> Dict[str, Any]:
        """Delete the vector store"""
        json_data = {
            "input": {
                "db_name": self.db_name
            },
            "api_key": self.connection_params.get("api_key")
        }
        
        return self._make_request(
            method="DELETE",
            json_data=json_data,
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT)
        )