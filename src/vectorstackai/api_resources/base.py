from typing import Optional, Dict, Any
import requests

from vectorstackai.utils import raise_error_from_response

class BaseAPIResource(object):
    """Base class for API resources"""

    DEFAULT_TIMEOUT = 300
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    @classmethod
    def _make_request(
        cls,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint
        
        Args:
            method (str): HTTP method (GET, POST, DELETE)
            params (Optional[Dict[str, Any]]): Query parameters
            json_data (Optional[Dict[str, Any]]): JSON body data
            
        Returns:
            Dict[str, Any]: Response data
        """
        response = requests.request(
            method=method,
            url=cls.CLASS_URL,
            params=params,
            json=json_data,
            headers=cls.HEADERS,
            timeout=cls.DEFAULT_TIMEOUT
        )
        
        if response.status_code != 200:
            raise_error_from_response(response)
            
        return response.json()