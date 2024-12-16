from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class PointObject:
    """Data class representing a data point with its metadata.
    
    A PointObject represents a single data point in the vector database, containing:
    - id: A unique identifier string
    - vector: The vector embedding as a list of floats 
    - metadata: Optional metadata dictionary that can store additional information about the point
    
    This class is used for inserting and retrieving points from vector indexes.
    """
    id: str
    vector: List[float]
    metadata: Optional[Dict] = None
