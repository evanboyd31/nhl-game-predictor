import httpx
import time

URL = "https://nhl-game-predictor.onrender.com"

def keep_servers_active(number_of_seconds=60):

    while True:
        response = httpx.get(url=URL)
        print(f"Pinged {URL}, response code {response.status_code}")
        time.sleep(number_of_seconds)

keep_servers_active()