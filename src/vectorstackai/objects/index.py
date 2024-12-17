from typing import Dict, Any, List, Optional
import vectorstackai.api_resources as api_resources
from vectorstackai.objects.points import PointObject

class IndexObject:
    """
    Class which implements various vector index operations
    """
    def __init__(self, db_name: str, connection_params: Dict[str, Any]):
        self.db_name = db_name
        self.index_api = api_resources.Index(db_name, connection_params)
        
    def __str__(self) -> str:
        #TODO: Add more info via index_info()
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
        points: List[PointObject],
        **kwargs
    ) -> Dict[str, Any]:
        """Upsert vectors into the index"""
        # TODO: Put a check of max number of data points which can be uploaded
        if not all(isinstance(point, PointObject) for point in points):
            raise ValueError("All elements in points must be of type PointObject")
        
        # Unpack points dataclass into separate lists
        ids = [point.id for point in points]
        vectors = [point.vector.tolist() for point in points]
        metadata = [point.metadata for point in points]
        
        json_data = {
            "index_name": self.db_name,
            "ids": ids,
            "vectors": vectors,
            "metadata": metadata
        }
        
        return self.index_api._make_request(
            method="POST",
            json_data=json_data,
            endpoint_name="/vectors/upsert"
        )

    def search(
        self,
        vector: List[float],
        top_k: int = 10,
        return_metadata: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        json_data = {
            "index_name": self.db_name,
            "vector": vector,
            "top_k": top_k,
            "return_metadata": return_metadata
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