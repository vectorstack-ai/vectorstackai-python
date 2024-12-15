import os

import vectorstack


def get_api_key() -> str:
    api_key = vectorstack.api_key or os.environ.get("VECTORSTACK_API_KEY")

    if api_key is not None:
        return api_key
    else:
        raise vectorstack.error.AuthenticationError(
            "No API key provided. You can set your API key in code using 'vectorstack.api_key = <API-KEY>', "
            "or set the environment variable VECTORSTACK_API_KEY=<API-KEY>. "
            "Visit https://www.vectorstack.ai to sign up for a free API key.")