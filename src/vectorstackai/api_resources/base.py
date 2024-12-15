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
    CONNECTION_PARAMS = None

    def _make_request(
        self,
        method: str,
        json_data: Optional[Dict[str, Any]] = None,
        endpoint_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint
        
        Args:
            method (str): HTTP method (GET, POST, DELETE)
            json_data (Optional[Dict[str, Any]]): JSON body data
            endpoint_name (Optional[str]): Endpoint name to append to the base URL
            
        Returns:
            Dict[str, Any]: Response data
        """
        url = self.CLASS_URL + endpoint_name if endpoint_name else self.CLASS_URL
        
        # Fetch api key from connection params
        json_data['api_key'] = self.CONNECTION_PARAMS['api_key']
            
        response = requests.request(
            method=method,
            url=url,
            json=json_data,
            headers=self.HEADERS,
            timeout=self.CONNECTION_PARAMS.get("request_timeout", self.DEFAULT_TIMEOUT)
        )
        if response.status_code != 200:
            raise_error_from_response(response)
            
        return response.json()