import os
import httpx
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")

from django.conf import settings
from games.models import Team
from datetime import datetime

def load_teams_data_from_api():

    # create current date string for standings_url
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")

    # first get a list of teams from the standings to get all team abbreviations
    standings_url = f"{settings.NHL_API_BASE_URL}standings/{formatted_date}"

    team_standings_response = httpx.get(standings_url)
    print(team_standings_response)

    # exit if API is down
    if team_standings_response.status_code != 200:
        return
    
    team_standings = team_standings_response.json().get("standings", [])
    print(team_standings)
    teams = []

    for team_json in team_standings:
        # get team fields from current json
        name = team_json.get("teamCommonName", {}).get("default", "")
        abbreviation = team_json.get("teamAbbrev", {}).get("default", "")
        logo_url = team_json.get("teamLogo", "")

        # ensure that the team doesn't already exist in the db
        if Team.objects.filter(name=name).count() == 0:
            team = Team(name=name,
                        abbreviation=abbreviation,
                        logo_url=logo_url)
            teams.append(team)
    
    # bulk create all new teams identified in above for loop
    Team.objects.bulk_create(teams)