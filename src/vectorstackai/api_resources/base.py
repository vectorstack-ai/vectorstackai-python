from typing import Optional, Dict, Any
import requests

from vectorstackai.utils import raise_error_from_response

class BaseAPIResource(object):
    """Base class for API resources"""
    CLASS_URL = None
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    DEFAULT_TIMEOUT = 30

    @classmethod
    def _make_request(
        cls,
        method: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        endpoint_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint
        
        Args:
            method (str): HTTP method (GET, POST, DELETE)
            json_data (Optional[Dict[str, Any]]): JSON body data
            timeout (Optional[float]): Request timeout
            endpoint_name (Optional[str]): Endpoint name to append to the base URL
            
        Returns:
            Dict[str, Any]: Response data
        """
        
        url = cls.CLASS_URL + endpoint_name if endpoint_name else cls.CLASS_URL
        
        response = requests.request(
            method=method,
            url=url,
            json=json_data,
            headers=cls.HEADERS,
            timeout=timeout
        )
        
        if response.status_code != 200:
            raise_error_from_response(response)
            
        return response.json()