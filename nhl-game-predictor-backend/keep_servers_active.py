import httpx
import os
from dotenv import load_dotenv
load_dotenv()

URL = "https://nhl-game-predictor-backend.onrender.com/api/keep-active/"
KEEP_ACTIVE_ACCESS_TOKEN = os.getenv("KEEP_ACTIVE_ACCESS_TOKEN", "")

def keep_servers_active():
    """
    function to ping the KeepActiveView REST API endpoint to keep
    both Render and Supabase instance active
    """
    headers = {"KEEP-ACTIVE-TOKEN": KEEP_ACTIVE_ACCESS_TOKEN}
    print(KEEP_ACTIVE_ACCESS_TOKEN)

    try:
        response = httpx.get(url=URL, 
                             headers=headers) 
        if response.status_code == 200:
            print(f"Pinged {URL}, server is active.")
        else:
            print(f"Pinged {URL}, received non-200 status code: {response.status_code}")
    except httpx.RequestError as e:
        print(f"Error pinging {URL}: {e}")
    

keep_servers_active()
