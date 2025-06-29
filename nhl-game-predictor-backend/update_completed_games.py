from server_pinger import ServerPinger

pinger = ServerPinger(
    url="http://localhost:8001/api/update-completed-games/",
    token_env_var="UPDATE_COMPLETED_GAMES_TOKEN",
    header_name="UPDATE-COMPLETED-GAMES-TOKEN"
)

pinger.ping()