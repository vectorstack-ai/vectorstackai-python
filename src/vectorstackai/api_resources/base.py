import json
import urllib3
from urllib.parse import urljoin
from typing import Optional, Dict, Any

from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

import vectorstackai.error as error
from vectorstackai.utils import raise_error_from_response

class BaseAPIResource(object):
    """Base class for API resources"""
    CLASS_URL = None
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    CONNECTION_PARAMS = None

    # Transient failures worth retrying; other errors (auth, bad request, ...) are raised immediately
    RETRYABLE_ERRORS = (
        error.RateLimitError,
        error.ServiceUnavailableError,
        error.InternalServerError,
        error.Timeout,
        error.APIConnectionError,
    )
    RETRY_WAIT = wait_exponential_jitter(initial=1, max=16)

    # Initialize a single persistent PoolManager. Retries are handled in _make_request_class,
    # so urllib3 only follows redirects and does not add a second retry layer.
    HTTP_CLIENT = urllib3.PoolManager(
        num_pools=10,
        maxsize=100,
        retries=urllib3.Retry(total=3, connect=0, read=0, status=0, other=0, redirect=3,
                              respect_retry_after_header=False),
    )

    @classmethod
    def _make_request_class(
        cls,
        method: str,
        json_data: Optional[Dict[str, Any]] = None,
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
        max_retries = connection_params.get("max_retries", cls.DEFAULT_MAX_RETRIES)
        retry_controller = Retrying(
            reraise=True,
            stop=stop_after_attempt(max_retries),
            wait=cls.RETRY_WAIT,
            retry=retry_if_exception_type(cls.RETRYABLE_ERRORS),
        )
        for attempt in retry_controller:
            with attempt:
                return cls._send_request(method, json_data, endpoint_name, connection_params)

    @classmethod
    def _send_request(
        cls,
        method: str,
        json_data: Optional[Dict[str, Any]],
        endpoint_name: Optional[str],
        connection_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a single HTTP request, mapping failures to VectorStackAIError subclasses."""
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
        except urllib3.exceptions.MaxRetryError as e:
            # urllib3 wraps the underlying failure once it gives up (e.g. on connection errors)
            raise cls._network_error(e.reason or e) from e
        except urllib3.exceptions.HTTPError as e:
            raise cls._network_error(e) from e

        # Check for non-200 responses
        if response.status not in [200, 202]:
            raise_error_from_response(response)

        # Ensure response has a valid JSON body
        try:
            return json.loads(response.data.decode("utf-8"))
        except ValueError:
            return {"error": "Invalid JSON response from server", "raw_response": response.data.decode("utf-8", errors="replace")}

    @staticmethod
    def _network_error(e: Exception) -> error.VectorStackAIError:
        """Map a urllib3 transport error to the matching VectorStackAIError subclass."""
        # NewConnectionError subclasses urllib3's TimeoutError, so it must be checked first
        if isinstance(e, (urllib3.exceptions.NewConnectionError,
                          urllib3.exceptions.ProtocolError,
                          urllib3.exceptions.ProxyError)):
            return error.APIConnectionError(
                message=f"Failed to connect to the VectorStackAI API. Check your network connection. ({e})")
        if isinstance(e, urllib3.exceptions.TimeoutError):
            return error.Timeout(message=f"Request to the VectorStackAI API timed out. ({e})")
        return error.VectorStackAIError(message=f"HTTP request failed: {e}")
