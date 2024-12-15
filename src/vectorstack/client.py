from typing import Any, List, Optional

from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

import vectorstack
import vectorstack.error as error
from vectorstack.utils import get_api_key
from vectorstack.objects import EmbeddingsObject

#TODO:
# - Base64 encoding

class Client:
    """VectorStack AI Client

    Args:
        api_key (str): Your API key.
        max_retries (int): Maximum number of retries if API call fails.
        timeout (float): Timeout in seconds.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 0,
        timeout: Optional[float] = None,
    ) -> None:

        self.api_key = api_key or get_api_key()

        self._params = {
            "api_key": self.api_key,
            "request_timeout": timeout,
        }
        self.retry_controller = Retrying(
            reraise=True,
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential_jitter(initial=1, max=16),
            retry=(
                retry_if_exception_type(error.RateLimitError)
                | retry_if_exception_type(error.ServiceUnavailableError)
                | retry_if_exception_type(error.Timeout)
            ),
        )

    def embed(
        self,
        texts: List[str],
        languages: List[str],
        model: str,
        is_query: bool = False,
        instruction: str = "",
    ) -> EmbeddingsObject:
        
        
        # Validate input arguments
        if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
            raise ValueError("'texts' must be a list of strings")
        if not isinstance(languages, list) or not all(isinstance(lang, str) for lang in languages):
            raise ValueError("'languages' must be a list of strings")
        if len(texts) != len(languages):
            raise ValueError("'texts' and 'languages' must have the same length")
        if not isinstance(model, str):
            raise ValueError("'model' must be a string")
        if not isinstance(is_query, bool):
            raise ValueError("'is_query' must be a boolean")
        if not isinstance(instruction, str):
            raise ValueError("'instruction' must be a string")

        for attempt in self.retry_controller:
            with attempt:
                response = vectorstack.Embedding.encode(
                    texts=texts,
                    model=model,
                    languages=languages,
                    is_query=is_query,
                    instruction=instruction,
                    **self._params,
                )
        return EmbeddingsObject(response)