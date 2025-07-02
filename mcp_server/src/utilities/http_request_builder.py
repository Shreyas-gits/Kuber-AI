"""Utility for building and sending HTTP requests using the requests library."""

import requests


class HTTPRequest:
    """Class for building and sending HTTP requests."""

    @classmethod
    def get(cls, url, headers=None, params=None):
        """Build and send a GET request.

        Args:
            url (str): URL for the request.
            headers (dict, optional): Dictionary of HTTP headers.
            params (dict, optional): Dictionary of URL parameters.

        Returns:
            requests.Response: Response object.
        """
        if not isinstance(url, str):
            raise ValueError("url must be a string")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("headers must be a dictionary or None")
        if params is not None and not isinstance(params, dict):
            raise ValueError("params must be a dictionary or None")
        return requests.get(url, headers=headers, params=params)

    @classmethod
    def post(cls, url, headers=None, body=None):
        """Build and send a POST request.

        Args:
            url (str): URL for the request.
            headers (dict, optional): Dictionary of HTTP headers.
            body (dict or str, optional): Request body.

        Returns:
            requests.Response: Response object.
        """
        if not isinstance(url, str):
            raise ValueError("url must be a string")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("headers must be a dictionary or None")
        if body is not None and not isinstance(body, (dict, str)):
            raise ValueError("body must be a dictionary, string, or None")
        return requests.post(
            url,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            data=body if isinstance(body, str) else None,
        )

    @classmethod
    def put(cls, url, headers=None, body=None):
        """Build and send a PUT request.

        Args:
            url (str): URL for the request.
            headers (dict, optional): Dictionary of HTTP headers.
            body (dict or str, optional): Request body.

        Returns:
            requests.Response: Response object.
        """
        return requests.put(
            url,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            data=body if isinstance(body, str) else None,
        )

    @classmethod
    def delete(cls, url, headers=None, body=None):
        """Build and send a DELETE request.

        Args:
            url (str): URL for the request.
            headers (dict, optional): Dictionary of HTTP headers.
            body (dict or str, optional): Request body.

        Returns:
            requests.Response: Response object.
        """
        return requests.delete(
            url,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            data=body if isinstance(body, str) else None,
        )
