# utils.py
import httpx
from fastapi import HTTPException
from typing import Any, Dict

async def api_fetch(url: str, headers: Dict[str, str]):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error fetching data: {exc.response.text}")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")


async def api_post(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Any:
    """
    Sends an asynchronous POST request to the specified URL with headers and a JSON payload.

    Args:
        url (str): The endpoint URL.
        headers (Dict[str, str]): HTTP headers to include in the request.
        payload (Dict[str, Any]): The data to include in the body of the POST request.

    Returns:
        Any: The JSON-decoded response from the server.

    Raises:
        HTTPException: If the HTTP request fails or an unexpected error occurs.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error posting data: {exc.response.text}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {str(exc)}"
            )


async def api_delete(url: str, headers: Dict[str, str]) -> Any:
    """
    Sends an asynchronous DELETE request to the specified URL with headers.

    Args:
        url (str): The endpoint URL.
        headers (Dict[str, str]): HTTP headers to include in the request.

    Returns:
        Any: The JSON-decoded response from the server.

    Raises:
        HTTPException: If the HTTP request fails or an unexpected error occurs.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            print(f"response utils: {response}")
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses
            return response  # Return the JSON-decoded response
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error deleting data: {exc.response.text}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {str(exc)}"
            )


async def api_put(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Any:
    """
    Sends an asynchronous PUT request to the specified URL with headers and a JSON payload.

    Args:
        url (str): The endpoint URL.
        headers (Dict[str, str]): HTTP headers to include in the request.
        payload (Dict[str, Any]): The data to include in the body of the PUT request.

    Returns:
        Any: The JSON-decoded response from the server.

    Raises:
        HTTPException: If the HTTP request fails or an unexpected error occurs.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise error for bad status
            return response
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error updating data: {exc.response.text}")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")


def setLoadingAndError(set, is_loading: bool):
    set({'isLoading': is_loading})

def handleError(set, error: Exception):
    set({'error': error})
    setLoadingAndError(set, False)
