import httpx
import time

URL = "https://nhl-game-predictor-backend.onrender.com/api/keep-active/"

def keep_servers_active(number_of_seconds=60*15):
    while True:
        try:
            response = httpx.get(url=URL, timeout=number_of_seconds) 
            if response.status_code == 200:
                print(f"Pinged {URL}, server is active.")
            else:
                print(f"Pinged {URL}, received non-200 status code: {response.status_code}")
        except httpx.RequestError as e:
            print(f"Error pinging {URL}: {e}")
        
        time.sleep(number_of_seconds)

keep_servers_active()
