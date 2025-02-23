
class VectorStackAIError(Exception):
    """
    Custom exception class for VectorStack-related errors.

    Args:
        message (str, optional): The error message.
        http_body (str, optional): The HTTP response body.
        http_status (int, optional): The HTTP status code.
        json_body (dict, optional): The JSON response body.
        headers (dict, optional): The HTTP response headers.
        code (str, optional): The error code.
   """

    def __init__(
        self,
        message=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None,
    ):
        super(VectorStackAIError, self).__init__(message)

        if http_body and hasattr(http_body, "decode"):
            try:
                http_body = http_body.decode("utf-8")
            except BaseException:
                http_body = "<Could not decode body as utf-8.>"

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body
        self.headers = headers or {}
        self.code = code
        self.request_id = self.headers.get("request-id", None)
        self.error = self.construct_error_object()

    def __str__(self):
        msg = self._message or "<empty message>"
        if self.request_id is not None:
            return "Request {0}: {1}".format(self.request_id, msg)
        else:
            return msg

    # Returns the underlying `Exception` (base class) message, which is usually
    # the raw message returned by an API. This was previously available
    # in python2 via `error.message`. Unlike `str(error)`, it omits "Request
    # req_..." from the beginning of the string.
    @property
    def user_message(self):
        return self._message

    def __repr__(self):
        return "%s(message=%r, http_status=%r, request_id=%r)" % (
            self.__class__.__name__,
            self._message,
            self.http_status,
            self.request_id,
        )

    def construct_error_object(self):
        """Constructs and returns an error object with relevant information."""
        error_obj = {
            "type": self.__class__.__name__,
            "message": self._message,
        }

        for attr in ["http_status", "code", "request_id", "http_body", "json_body"]:
            if getattr(self, attr) is not None:
                error_obj[attr] = getattr(self, attr)

        return error_obj
    
    
    
class AuthenticationError(VectorStackAIError):
    """
    Exception raised when there is an authentication error.

    This error occurs when the API key is invalid, missing, or there are other
    authentication-related issues when trying to access the VectorStack AI API.
    """
    pass

class InternalServerError(VectorStackAIError):
    """
    Exception raised when there is an internal server error.
    """
    pass
    
class RateLimitError(VectorStackAIError):
    """
    Exception raised when there is a rate limit error.

    This error occurs when the rate limit is exceeded.
    """
    pass

class ServiceUnavailableError(VectorStackAIError):
    """
    Exception raised when the service is unavailable.
    """
    pass

class MethodNotAllowedError(VectorStackAIError):
    """
    Exception raised when the GET/POSTmethod is not allowed.
    """
    pass

class Timeout(VectorStackAIError):
    """
    Exception raised when the request times out.
    """
    pass


class BadRequestError(VectorStackAIError):
    """
    Exception raised when the request is bad.
    """
    pass

class NotFoundError(VectorStackAIError):
    """
    Exception raised when the resource is not found.
    """
    pass

class ResourceBusyError(VectorStackAIError):
    """
    Exception raised when the resource is busy, and hence the request cannot be processed.
    """
    pass