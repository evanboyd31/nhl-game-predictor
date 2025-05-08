import httpx
import time

URL = "https://nhl-game-predictor-backend.onrender.com/api/keep-active/"

def keep_server_active():
    """
    function to ping the KeepActiveView REST API endpoint
    """
    try:
        response = httpx.get(url=URL) 
        if response.status_code == 200:
            print(f"Pinged {URL}, server is active.")
        else:
            print(f"Pinged {URL}, received non-200 status code: {response.status_code}")
    except httpx.RequestError as e:
        print(f"Error pinging {URL}: {e}")
    

keep_server_active()
