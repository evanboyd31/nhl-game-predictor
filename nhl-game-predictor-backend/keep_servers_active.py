from server_pinger import ServerPinger

pinger = ServerPinger(
    url="https://nhl-game-predictor-backend.onrender.com/api/keep-active/",
    token_env_var="KEEP_ACTIVE_ACCESS_TOKEN",
    header_name="KEEP-ACTIVE-TOKEN"
)

pinger.ping()