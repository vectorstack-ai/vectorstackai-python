from typing import Optional, Dict, Any
import requests
from urllib.parse import urljoin
from vectorstackai.utils import raise_error_from_response

class BaseAPIResource(object):
    """Base class for API resources"""
    CLASS_URL = None
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    DEFAULT_TIMEOUT = 30
    CONNECTION_PARAMS = None

    @classmethod
    def _make_request_class(
        cls,
        method: str,
        json_data: Optional[Dict[str, Any]] = {},
        endpoint_name: Optional[str] = None,
        connection_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint via class method. 
        This is used for class methods that do not require an instance of the class.
        Args:
            method (str): HTTP method (GET, POST, DELETE)
            json_data (Optional[Dict[str, Any]]): JSON body data
            endpoint_name (Optional[str]): Endpoint name to append to the base URL
            connection_params (Optional[Dict[str, Any]]): Connection parameters
        Returns:
            Dict[str, Any]: Response data
        """
        url = urljoin(cls.CLASS_URL, endpoint_name) if endpoint_name else cls.CLASS_URL
        
        # Fetch api key from connection params and add to headers
        headers = cls.HEADERS.copy()
        headers["Authorization"] = f"{connection_params['api_key']}"
        
        response = requests.request(
            method=method,
            url=url,
            json=json_data,
            headers=headers,
            timeout=connection_params.get("request_timeout", cls.DEFAULT_TIMEOUT)
        )
        if response.status_code not in [200, 202]:
            raise_error_from_response(response)
            
        return response.json()