import json
import urllib3
from urllib.parse import urljoin
from typing import Optional, Dict, Any

from vectorstackai.utils import raise_error_from_response
from vectorstackai.error import VectorStackAIError

class BaseAPIResource(object):
    """Base class for API resources"""
    CLASS_URL = None
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    DEFAULT_TIMEOUT = 30
    CONNECTION_PARAMS = None
    
    # Initialize a single persistent PoolManager
    HTTP_CLIENT = urllib3.PoolManager(num_pools=10, maxsize=100, retries=3)

    @classmethod
    def _make_request_class(
        cls,
        method: str,
        json_data: Optional[Dict[str, Any]] = {},
        endpoint_name: Optional[str] = None,
        connection_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint via class method.
        
        Args:
            method (str): HTTP method (GET, POST, DELETE)
            json_data (Optional[Dict[str, Any]]): JSON body data
            endpoint_name (Optional[str]): Endpoint name to append to the base URL
            connection_params (Optional[Dict[str, Any]]): Connection parameters

        Returns:
            Dict[str, Any]: Response data
        """
        url = urljoin(cls.CLASS_URL, endpoint_name) if endpoint_name else cls.CLASS_URL

        # Fetch API key from connection params and add to headers
        headers = cls.HEADERS.copy()
        headers["Authorization"] = f"{connection_params['api_key']}"

        # Prepare JSON data
        encoded_data = json.dumps(json_data).encode("utf-8") if json_data else None

        try:
            response = cls.HTTP_CLIENT.request(
                method=method.upper(),
                url=url,
                body=encoded_data,
                headers=headers,
                timeout=connection_params.get("request_timeout", cls.DEFAULT_TIMEOUT),
            )

            # Check for non-200 responses
            if response.status not in [200, 202]:
                raise_error_from_response(response)
                
            # Ensure response has a valid JSON body
            try:
                return json.loads(response.data.decode("utf-8"))
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response from server", "raw_response": response.data.decode("utf-8", errors="replace")}
            
        except urllib3.exceptions.MaxRetryError:
            raise Exception("Server not found or unreachable. Check the URL or network connection.")

        except urllib3.exceptions.NewConnectionError:
            raise Exception("Failed to establish a new connection. Server might be down.")

        except urllib3.exceptions.HTTPError as e:
            raise Exception(f"HTTP request failed: {e}")

        except VectorStackAIError as e:
            raise e
        
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")