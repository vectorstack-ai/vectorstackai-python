import os
import requests

import vectorstackai
from vectorstackai import error

def get_api_key() -> str:
    api_key = getattr(vectorstackai, 'api_key', None) or os.environ.get("VECTORSTACKAI_API_KEY")

    if api_key is not None:
        return api_key
    else:
        raise vectorstackai.error.AuthenticationError(
            "No API key provided. You can set your API key in code using 'vectorstackai.api_key = <API-KEY>', "
            "or set the environment variable VECTORSTACKAI_API_KEY=<API-KEY>. "
            "Visit https://www.vectorstack.ai to sign up for a free API key.")
        
        
        
def raise_error_from_response(response):
    """
    Raise an appropriate exception based on the error response from the API.

    This function dynamically maps error types to their corresponding exception classes,
    extracts error information from the response, and raises the appropriate exception.

    Args:
        response (requests.Response): The API response object containing error information.

    Raises:
        VectorStackAIError: An appropriate subclass of VectorStackAIError based on the error type.

    Note:
        This function assumes that the error response is in JSON format and follows
        a specific structure with an 'error' key containing error details.
    """
    
    # Dynamically create mapping of error types to exception classes
    error_class_mapping = {
        name: getattr(error, name)
        for name in dir(error)
        if isinstance(getattr(error, name), type) and issubclass(getattr(error, name), error.VectorStackAIError)
    }
    
    # Handle server unavailable or bad gateway error
    if response.status_code in [404, 502]:
        raise error.ServiceUnavailableError(message='Server unavailable/down ..', 
                                      http_status=response.status_code, 
                                      json_body={}, 
                                      headers=response.headers)

    # Get the error data from the response
    try:
        error_data = response.json().get('error', {})
    except requests.exceptions.JSONDecodeError:
        # Handle the case where the response does not contain valid JSON
        error_data = {}
        error_data['message'] = response.content.decode('utf-8', errors='replace')
        
    message = error_data.get('message')
    http_status = error_data.get('http_status')
    code = error_data.get('code')
    http_body = error_data.get('http_body')
    json_body = error_data.get('json_body')
    headers = response.headers

    # Get the corresponding exception class based on the error type
    exception_class = error_class_mapping.get(error_data.get('type'), error.VectorStackAIError)

    # Raise the exception with the appropriate data
    raise exception_class(
        message=message,
        http_body=http_body,
        http_status=http_status,
        json_body=json_body,
        headers=headers,
        code=code,
    )
