import os
import httpx
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")

from django.conf import settings
from games.models import Team, Game
from datetime import datetime

def load_teams_data_from_api():
    """
    using the NHL API, load each NHL team's name, abbreviation, and logo url
    into a Team model class and store in the db
    """
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


def load_games_for_team_from_api(team_abbreviation, past_seasons=0):
    """
    given the abbreviation of a team, load Game and GameData model instances
    into the db. 
    
    the past_seasons parameter indicates how many seasons in the past
    we should fetch. for instance,
    
    - if the current season is 2024-2025, and past_seasons = 0, then we fetch game data for 2024-2025
    - if the current season is 2024-2025, and past_seasons = 2, we fetch game data for 2024-2025, 2023-2024, and 2022-2023.
    
    """

    # get the team by its abbreviation
    team = Team.objects.filter(abbreviation=team_abbreviation).first()

    if team is None:
        raise ValueError(f"No team found with abbreviation {team_abbreviation}")
    
    if past_seasons < 0:
        raise ValueError(f"Enter a positive past_seasons for {team_abbreviation}")
    
    def create_seasons_strings(past_seasons):
        """
        builds a list of season strings as required by the NHL API
        """
        # create current season and add to list
        current_year = datetime.now().year
        current_season = f"{current_year}{current_year + 1}"

        # build list of current season and past seasons
        seasons = [current_season]
        for i in range(1, past_seasons + 1):
            past_year = current_year - i
            past_season = f"{past_year}{past_year + 1}"
            seasons.append(past_season)
        
        return seasons
    
    # get seasons
    seasons = create_seasons_strings(past_seasons=past_seasons)
    games_to_create = []
    games_to_update = []

    # used to see the completion status of a game
    current_date = datetime.now()

    for season in seasons:
        # get schedule and all games for this season
        season_schedule_url = f"{settings.NHL_BASE_API_URL}club-schedule-season/{team_abbreviation}/{season}"
        season_schedule_json = httpx.get(season_schedule_url)
        games_json = season_schedule_json.get("games", [])

        # iterate over all games
        for game_json in games_json:
            game_id = games_json.get("id")
            game_type = games_json.get("gameType")
            game_date = datetime.strp(game_json.get("gameDate"), "%Y-%m-%d").date()

            away_team_json = game_json.get("awayTeam", {})
            away_team_abbreviation = away_team_json.get("abbrev")
            away_team = Team.objects.filter(abbreviation=away_team_abbreviation).first()

            home_team_json = game_json.get("homeTeam", {})
            home_team_abbreviation = home_team_json.get("abbrev")
            home_team = Team.objects.filter(abbreviation=home_team_abbreviation).first()

            # store info about game results if it is completed
            status = games_json.get("gameState")
            
            home_team_goals = 0
            away_team_goals = 0
            is_overtime = False
            is_shootout = False
            if game_date < current_date:
                home_team_goals = home_team_json.get("score")
                away_team_goals = away_team_json.get("score")
                is_overtime = game_json.get("gameOutcome", {}).get("lastPeriodType", "REG") == "OT"
                is_shootout = game_json.get("gameOutcome", {}).get("lastPeriodType", "REG") == "SO"
            

                winning_team = home_team if home_team_goals > away_team_goals else away_team
            
            
            game = Game(id=id,
                        home_team=home_team,
                        away_team=away_team,
                        winning_team=winning_team,
                        game_date=game_date,
                        status=status,
                        game_type=game_type,
                        home_team_goals=home_team_goals,
                        away_team_goals=away_team_goals,
                        is_overtime=is_overtime,
                        is_shootout=is_shootout)
            
            # if no game already exists, add it to the bulk_create list, otherwise add it to bulk_update list
            if Game.objects.filter(id=id).count() == 0:
                games_to_create.append(game)
            else:
                games_to_update.append(game)

    # bulk create and update the respective games
    Game.objects.bulk_create(games_to_create)
    Game.objects.bulk_update(games_to_update)

