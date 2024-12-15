from typing import Dict, Any, List, Optional
import vectorstackai.api_resources as api_resources

class StoreObject:
    """
    Class which implements various vector store operations

    """
    def __init__(self, db_name: str, connection_params: Dict[str, Any]):
        self.db_name = db_name
        self.store_api = api_resources.Store(db_name, connection_params)
        
    def __str__(self) -> str:
        #TODO: Add more info
        return f"VstackAI Vector Store (name={self.db_name})"
        
    def __repr__(self) -> str:
        return self.__str__()   

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
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT),
            endpoint_name="/vectors/upsert"
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
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT),
            endpoint_name="/vectors/search"
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
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT),
            endpoint_name="/vectors/delete"
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
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT),
            endpoint_name="/info_store"
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
            timeout=self.connection_params.get("request_timeout", self.DEFAULT_TIMEOUT),
            endpoint_name="/delete_store"
        )