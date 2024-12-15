from typing import Dict, Any, List, Optional
import vectorstackai.api_resources as api_resources

class IndexObject:
    """
    Class which implements various vector index operations
    """
    def __init__(self, db_name: str, connection_params: Dict[str, Any]):
        self.db_name = db_name
        self.index_api = api_resources.Index(db_name, connection_params)
        
    def __str__(self) -> str:
        #TODO: Add more info
        return f"VstackAI Vector Index (name={self.db_name})"
        
    def __repr__(self) -> str:
        return self.__str__()   
    
    def index_info(self, **kwargs) -> Dict[str, Any]:
        """Get information about the vector index"""
        return self.index_api._make_request(
            method="POST",
            endpoint_name="/index_info",
            json_data={"index_name": self.db_name}
        )
 
    def upsert(
        self,
        vector_ids: List[str],
        vectors: List[List[float]],
        metadata: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upsert vectors into the index"""
        json_data = {
            "input": {
                "db_name": self.db_name,
                "vector_ids": vector_ids,
                "vectors": vectors,
                "metadata": metadata
            }
        }
        
        return self.index_api._make_request(
            method="POST",
            json_data=json_data,
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
            }
        }
        
        return self.index_api._make_request(
            method="POST",
            json_data=json_data,
            endpoint_name="/vectors/search"
        )

    def delete_vectors(self, vector_ids: List[str], **kwargs) -> Dict[str, Any]:
        """Delete vectors by their IDs"""
        json_data = {
            "input": {
                "db_name": self.db_name,
                "vector_ids": vector_ids
            }
        }
        
        return self.index_api._make_request(
            method="DELETE",
            json_data=json_data,
            endpoint_name="/vectors/delete"
        )
   
    def delete(self, **kwargs) -> Dict[str, Any]:
        """Delete the vector index"""
        json_data = {
            "input": {
                "db_name": self.db_name
            }
        }
        
        return self.index_api._make_request(
            method="DELETE",
            json_data=json_data,
            endpoint_name="/delete_index"
        )