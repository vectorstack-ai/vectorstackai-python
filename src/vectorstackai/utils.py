import os
import json
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
        response (urllib3.response.HTTPResponse): The API response object containing error information in bytes.

    Raises:
        VectorStackAIError: An appropriate subclass of VectorStackAIError based on the error type.

    Note:
        This function assumes that the error response is in JSON format and follows
        a specific structure with an 'error' key containing error details. If the 
        response is not in JSON format or does not contain an 'error' key, the function
        will raise a VectorStackAIError with the response content as the message.
    """
            
    # Parse the error_data from the response as JSON
    #########################################################
    try:
        response_json = response.json()
        error_data = response_json['error']
        ERROR_RAISED_BY_VECTORSTACKAI = True
    except (json.JSONDecodeError, KeyError, ValueError):
        # Case where the response does not contain valid JSON or 'error' key
        ERROR_RAISED_BY_VECTORSTACKAI = False
        error_data = {}
        error_data['message'] = response.data.decode('utf-8', errors='replace')
    
    # The error can originate from either server due to unexpected event or raise by our API containing error data
    # Below, we will handle both cases.
    #########################################################
    if ERROR_RAISED_BY_VECTORSTACKAI:
        message = error_data.get('message')
        http_status = error_data.get('http_status')
        code = error_data.get('code')
        http_body = error_data.get('http_body')
        json_body = error_data.get('json_body')
        headers = response.headers
        
        # Dynamically create mapping of error types to exception classes
        error_class_mapping = {
            name: getattr(error, name)
            for name in dir(error)
            if isinstance(getattr(error, name), type) and issubclass(getattr(error, name), error.VectorStackAIError)
        }

        # Get the corresponding exception class based on the error type
        exception_class = error_class_mapping.get(error_data.get('type'),
                                                  error.VectorStackAIError)

        # Raise the exception with the appropriate data
        raise exception_class(
            message=message,
            http_body=http_body,
            http_status=http_status,
            json_body=json_body,
            headers=headers,
            code=code,
        )
    else:
        # Map the error (raised by server) to the appropriate exception class of VectorStackAIError
        #########################################################
        if response.status == 405:
            # Handle 405 method not allowed error
            raise error.MethodNotAllowedError(message=f'{error_data["message"]}', 
                                          http_status=response.status, 
                                          json_body={}, 
                                          headers=response.headers)
        elif response.status == 402:
            raise error.BadRequestError(message=f'{error_data["message"]}', 
                                       http_status=response.status, 
                                       json_body={}, 
                                       headers=response.headers)
        elif response.status in [404, 502]:
            # Handle server unavailable or bad gateway error
            raise error.ServiceUnavailableError(message=f'{error_data["message"]}', 
                                          http_status=response.status, 
                                          json_body={}, 
                                          headers=response.headers)
        else:
            # Raise a general VectorStackAIError with the response content as the message
            raise error.VectorStackAIError(message=f'Unexpected error: {error_data["message"]}', 
                                          http_status=response.status, 
                                          json_body={}, 
                                          headers=response.headers)