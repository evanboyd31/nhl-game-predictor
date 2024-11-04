import httpx
import time
import os

URL = "https://nhl-game-predictor-backend.onrender.com/api/predict-games-today/"
PREDICT_GAMES_TODAY_ACCESS_TOKEN = os.getenv("PREDICT_GAMES_TODAY_ACCESS_TOKEN", "")

def predict_games(number_of_seconds=60*30):
    headers = {"PREDICT-GAMES-TODAY-TOKEN": PREDICT_GAMES_TODAY_ACCESS_TOKEN}
    while True:
        try:
            response = httpx.get(url=URL, headers=headers, timeout=number_of_seconds) 
            if response.status_code == 200:
                print(f"Games have been predicted")
            else:
                print(f"Pinged {URL}, received non-200 status code: {response.status_code}")
        except httpx.RequestError as e:
            print(f"Error pinging {URL}: {e}")
        
        time.sleep(number_of_seconds)

predict_games()
