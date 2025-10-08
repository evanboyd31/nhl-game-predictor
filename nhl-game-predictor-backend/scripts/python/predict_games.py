from server_pinger import ServerPinger

pinger = ServerPinger(
    url="http://localhost:8003/api/predict-games-today/",
    token_env_var="PREDICT_GAMES_TODAY_ACCESS_TOKEN",
    header_name="PREDICT-GAMES-TODAY-TOKEN"
)

pinger.ping()