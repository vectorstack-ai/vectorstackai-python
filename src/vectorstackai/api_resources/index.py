import re
import requests
from typing import List, Dict, Optional, Any

from vectorstackai.api_resources.base import BaseAPIResource
from vectorstackai.utils import raise_error_from_response

class Index(BaseAPIResource):
    """API Resource for vector store (index) operations."""
    CLASS_URL = "https://api.vectorstack.ai/precise_search/"
    
    @classmethod
    def create_index(cls, json_data: Dict[str, Any], connection_params: Dict[str, Any]):
        """Create a new vector index"""
        return cls._make_request_class(
            method="POST",
            json_data=json_data,
            connection_params=connection_params,
            endpoint_name="create_index"
        )

    @classmethod
    def upsert(cls, index_name: str, json_data: Dict[str, Any], connection_params: Dict[str, Any]):
        """Upsert vectors into the index."""
        return cls._make_request_class(
            method="POST",
            json_data=json_data,
            connection_params=connection_params,
            endpoint_name=f"upsert/{index_name}"
        )

    @classmethod 
    def search(cls, index_name: str, json_data: Dict[str, Any], connection_params: Dict[str, Any]):
        """Search for similar vectors in index specified by index_name"""
        return cls._make_request_class(
            method="POST",
            json_data=json_data,
            connection_params=connection_params,
            endpoint_name=f"search/{index_name}"
        )
    
    @classmethod 
    def delete_vectors(cls, index_name: str, json_data: Dict[str, Any], connection_params: Dict[str, Any]):
        """Delete vectors from the index."""
        return cls._make_request_class(
            method="DELETE",
            json_data=json_data,
            connection_params=connection_params,
            endpoint_name=f"delete_vectors/{index_name}"
        )
    
    @classmethod 
    def list_indexes(cls, connection_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries containing info of all the indexes"""
        return cls._make_request_class(
            method="GET",
            connection_params=connection_params,
            endpoint_name="list_indexes"
        )
    
    @classmethod 
    def info(cls, index_name: str, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about the index."""
        return cls._make_request_class(
            method="GET",
            connection_params=connection_params,
            endpoint_name=f"info/{index_name}"
        )
    
    @classmethod 
    def delete_index(cls, index_name: str, connection_params: Dict[str, Any]):
        """Delete the index."""
        return cls._make_request_class(
            method="DELETE",
            connection_params=connection_params,
            endpoint_name=f"delete_index/{index_name}"
        )
    
    @classmethod
    def optimize_for_latency(cls, index_name: str, connection_params: Dict[str, Any]):
        """Optimize the index for better latency and throughput."""
        return cls._make_request_class(
            method="POST",
            connection_params=connection_params,
            endpoint_name=f"optimize_for_latency/{index_name}"
        )
