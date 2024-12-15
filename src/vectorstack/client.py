import functools
import warnings
import ipdb
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
# - Figure out base64 encoding if required
# - Add checks for model, languages, is_query and instruction before sending to backend


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
        model: str ,
        is_query: bool = False,
        instruction: str = "",
    ) -> EmbeddingsObject:

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