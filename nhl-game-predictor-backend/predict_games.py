import httpx
import os

URL = "https://nhl-game-predictor-backend.onrender.com/api/predict-games-today/"
PREDICT_GAMES_TODAY_ACCESS_TOKEN = os.getenv("PREDICT_GAMES_TODAY_ACCESS_TOKEN", "")

def predict_games():
    """
    function to ping the PredictGamesTodayView REST API endpoint every
    number_of_seconds seconds
    """

    # the PredictGamesTodayView endpoint must be provided the correct token to predict games for today
    headers = {"PREDICT-GAMES-TODAY-TOKEN": PREDICT_GAMES_TODAY_ACCESS_TOKEN}
    try:
        response = httpx.get(url=URL, headers=headers) 
        if response.status_code == 200:
            print(f"Games have been predicted")
        else:
            print(f"Pinged {URL}, received non-200 status code: {response.status_code}")
    except httpx.RequestError as e:
        print(f"Error pinging {URL}: {e}")
        

predict_games()
