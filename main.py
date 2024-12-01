import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import AUTH_HEADER, EXTERNAL_BASE_URL
from utils import api_fetch ,api_post, api_delete, api_put
import httpx
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint: Fetch client details and lists
@app.get("/clients/{id}")
async def get_clients(id: str) -> Dict[str, Any]:
    """
    Fetch client details and list details from two external API calls and merge them into one response.
    """
    try:
        # Fetch client details
        client_url = f"{EXTERNAL_BASE_URL}/clients/{id}.json"
        client_data = await api_fetch(client_url, {"Authorization": AUTH_HEADER})

        # Fetch lists associated with the client
        lists_url = f"{EXTERNAL_BASE_URL}/clients/{id}/lists.json"
        lists_data = await api_fetch(lists_url, {"Authorization": AUTH_HEADER})

        # Combine the data
        combined_response = {
            "basic_details": client_data.get("BasicDetails", {}),
            "billing_details": client_data.get("BillingDetails", {}),
            "lists": lists_data,
        }

        return combined_response

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error fetching data: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")


# Endpoint: Fetch list details and active subscribers
@app.get("/lists/{id}")
async def get_list_details(id: str) -> Dict[str, Any]:
    """
    Fetch list details and active subscribers from two external API calls
    and combine them into one response.
    """
    try:
        # Fetch list details
        list_url = f"{EXTERNAL_BASE_URL}/lists/{id}.json"
        list_data = await api_fetch(list_url, {"Authorization": AUTH_HEADER})

        # Fetch active subscribers
        subscribers_url = f"{EXTERNAL_BASE_URL}/lists/{id}/active.json?&includetrackingpreference=true&includesmspreference=true"
        subscribers_data = await api_fetch(subscribers_url, {"Authorization": AUTH_HEADER})

        # Combine the data into a response
        combined_response = {
            "details": list_data,
            "active_subscribers": subscribers_data,
        }

        return combined_response

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error fetching data: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(exc)}"
        )


class CustomField(BaseModel):
    Key: str
    Value: str

class Subscriber(BaseModel):
    EmailAddress: str
    Name: Optional[str] = None
    MobileNumber: Optional[str] = None
    CustomFields: Optional[List[CustomField]] = []
    Resubscribe: Optional[bool] = False
    RestartSubscriptionBasedAutoresponders: Optional[bool] = False
    ConsentToTrack: str
    ConsentToSendSms: Optional[str] = "No"
    
@app.post("/subscribers/{id}")
async def add_active_subscriber(id: str, subscriber: Subscriber):
    """
    Add a new subscriber to the given list using Campaign Monitor's API,
    and respond with the updated list of active subscribers.
    """
    try:
        # Endpoint URL for adding a subscriber
        url = f"{EXTERNAL_BASE_URL}/subscribers/{id}.json"
        print(f"url: {url}")

        # Convert the Pydantic model to a dictionary
        payload = subscriber.dict()

        # Perform API call to add a subscriber
        res = await api_post(
            url,
            headers={"Authorization": AUTH_HEADER, "Content-Type": "application/json"},
            payload=payload,
        )
        # Return success response with the updated list of active subscribers
        return res

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(exc)}"
        )


@app.delete("/subscribers/{emailList}/{email}")
async def remove_active_subscriber(emailList: str, email: str):
    print(f"emailList: {emailList}")
    print(f"email: {email}")
    
    # Decode the email (optional, FastAPI decodes by default)
    decoded_email_list = unquote(emailList)
    decoded_email = unquote(email)
    """
    Remove an active subscriber from the list using Campaign Monitor's API.
    """
    try:
        # Endpoint URL
        url = f"{EXTERNAL_BASE_URL}/subscribers/{decoded_email_list}.json?email={decoded_email}"
        await api_delete(url, headers={"Authorization": AUTH_HEADER})
        
        return {"message":"Subscriber removed successfully", "status": 200}
       

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error removing subscriber: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(exc)}"
        )



@app.put("/subscribers/{emailList}/{email}")
async def update_active_subscriber(emailList: str, email: str, subscriber: Subscriber):
    try:
        # Decode the email and email list (FastAPI decodes by default, but we are decoding explicitly here as well)
        decoded_email_list = unquote(emailList)
        decoded_email = unquote(email)

        # Endpoint URL for updating a subscriber
        url = f"{EXTERNAL_BASE_URL}subscribers/{decoded_email_list}.json?email={decoded_email}"
        print(f'url: {url}')
        # Convert the Pydantic model to a dictionary
        payload = subscriber.dict()

        # Use the api_put function to send a PUT request to update the subscriber
        res = await api_put(
            url,
            headers={"Authorization": AUTH_HEADER, "Content-Type": "application/json"},
            payload=payload,
        )
        print(f'res: {res}')
        
        return {"message":"Subscriber removed successfully", "status": 200}

    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"Error updating subscriber: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")




if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variables or use 4000 as the default
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, port=port)