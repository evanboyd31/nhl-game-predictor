import httpx
import time

URL = "http://nhl-game-predictor-backend.onrender.com/api/predict-games-today/"

def predict_games(number_of_seconds=60*30):
    while True:
        try:
            response = httpx.get(url=URL, timeout=number_of_seconds) 
            if response.status_code == 200:
                print(f"Games have been predicted")
            else:
                print(f"Pinged {URL}, received non-200 status code: {response.status_code}")
        except httpx.RequestError as e:
            print(f"Error pinging {URL}: {e}")
        
        time.sleep(number_of_seconds)

predict_games()
