import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SERVICE_ACCOUNT_FILE = '/home/cspl/Company_work/Project1/MyProject/MyApp/firebase_key.json'
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
projectId = "drf-project-4e879"

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes = SCOPES
    )
    credentials.refresh(Request())
    return credentials.token

def send_firebase_notification(fcm_token):
    access_token = get_access_token()

    url = f"https://fcm.googleapis.com/v1/projects/{projectId}/messages:send"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    payload = {
        "message": {
            "token": fcm_token,
            "notification": {
                "title": 'Notification',
                "body": 'Notification From Firebase'
            }
        }
    }

    response = requests.post(url, headers = headers, json = payload)

    if response.status_code == 200:
        print("Notification Send Successfully", response.json())
    else:
        print("Failed to send Notification", response.json())