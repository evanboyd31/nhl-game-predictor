from server_pinger import ServerPinger
from datetime import date

# Get today's date in YYYY-MM-DD format
today = date.today().isoformat()

pinger = ServerPinger(
    url="https://nhl-game-predictor-backend.onrender.com/api/games/fetch-from-nhl-api/",
    token_env_var="FETCH_GAMES_TOKEN",
    header_name="FETCH-GAMES-TOKEN",
    params={"date": today}
)

pinger.ping()