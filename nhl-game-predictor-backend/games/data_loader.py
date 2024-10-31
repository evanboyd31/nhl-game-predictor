import os
import httpx
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")
django.setup()

from django.conf import settings
from games.models import Franchise, Team, Game, TeamData
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction

# mapping from API-provided strings to integer values for GameData model class
RESULT_MAP = {
    "W": TeamData.WIN,
    "L": TeamData.LOSS,
    "OT": TeamData.OVERTIME,
    "FG": TeamData.FIRST_GAME
}

# reverse results map
REVERSE_RESULT_MAP = {v: k for k, v in RESULT_MAP.items()}

@transaction.atomic
def load_franchises_and_teams_data_from_api():
    franchise_url = f"https://api.nhle.com/stats/rest/en/team"
    franchise_response = httpx.get(franchise_url)

    franchise_json = franchise_response.json()
    franchises_json = franchise_json.get("data", [])

    teams = []
    for franchise_json in franchises_json:
        franchise_id = franchise_json.get("franchiseId")
        if franchise_id is not None:
            franchise, _ = Franchise.objects.get_or_create(franchise_id=franchise_id)
            team_full_name = franchise_json.get("fullName")
            team_abbreviation = franchise_json.get("triCode")
            team = Team(name=team_full_name,
                        abbreviation=team_abbreviation,
                        franchise=franchise)
            teams.append(team)
    
    Team.objects.bulk_create(teams)


@transaction.atomic
def load_active_team_logo_urls():
    """
    using the NHL API, load each NHL team's name, abbreviation, and logo url
    into a Team model class and store in the db
    """
    # create current date string for standings_url
    current_date = timezone.localdate()
    formatted_date = current_date.strftime("%Y-%m-%d")

    # first get a list of teams from the standings to get all team abbreviations
    standings_url = f"{settings.NHL_API_BASE_URL}standings/{formatted_date}"

    team_standings_response = httpx.get(standings_url)

    # exit if API is down
    if team_standings_response.status_code != 200:
        return
    
    team_standings = team_standings_response.json().get("standings", [])
    teams = []

    for team_json in team_standings:
        # get team fields from current json
        abbreviation = team_json.get("teamAbbrev", {}).get("default", "")
        logo_url = team_json.get("teamLogo", "")

        # ensure that the team doesn't already exist in the db
        if Team.objects.filter(abbreviation=abbreviation).count() != 0:
            team = Team.objects.filter(abbreviation=abbreviation).first()
            team.logo_url = logo_url
            teams.append(team)
            
    
    # bulk create all new teams identified in above for loop
    Team.objects.bulk_update(teams, fields=['logo_url'])


@transaction.atomic
def load_team_data_for_date_from_api(team : Team, game_date):

    # get the date before a game
    previous_day = game_date - timedelta(days=1)

    # check to see if we already have the data for the given team and date
    previous_team_data = TeamData.objects.filter(team=team, data_capture_date=previous_day).first()
    if previous_team_data is not None:
        return previous_team_data


    # format the standings URL for the given date
    formatted_date = previous_day.strftime("%Y-%m-%d")
    standings_url = f"{settings.NHL_API_BASE_URL}standings/{formatted_date}"

    standings_response = httpx.get(standings_url)
    standings_json = standings_response.json().get("standings", [])

    if len(standings_json) != 0:
        for team_standings in standings_json:
            if team_standings.get("teamAbbrev", {}).get("default", "") == team.abbreviation:
                team_data = TeamData(team_data_json=team_standings,
                                     team=team,
                                     data_capture_date=previous_day)
                return team_data
    else:
        # if standings is blank, it is the first game of the season, so only supply date and team
        # all other fields will default to zero
        return None

@transaction.atomic
def load_games_for_team_from_api(team_abbreviation, seasons, get_team_data=True):
    """
    given the abbreviation of a team, load Game and GameData model instances
    into the db. 
    
    the seasons parameter is a list of season IDs that are compliant with the NHL API.
    For example, the 2024-2025 season has an ID of 20242025
    
    """

    # get the team by its abbreviation
    team = Team.objects.filter(abbreviation=team_abbreviation).first()

    if team is None:
        raise ValueError(f"No team found with abbreviation {team_abbreviation}")
    
    if len(seasons) == 0:
        raise ValueError(f"Please enter seasons to fetch game data for.")
    
    games_to_create = []
    team_data_to_create = []
    existing_team_data_keys = set()

    # used to see the completion status of a game
    current_date = timezone.localdate()

    for season in seasons:
        # get schedule and all games for this season
        season_schedule_url = f"{settings.NHL_API_BASE_URL}club-schedule-season/{team_abbreviation}/{season}"
        season_schedule_response = httpx.get(season_schedule_url)
        season_schedule_json = season_schedule_response.json()
        games_json = season_schedule_json.get("games", [])

        # iterate over all games
        for game_json in games_json:
            game_id = game_json.get("id")
            game_type = game_json.get("gameType")
            game_date = datetime.strptime(game_json.get("gameDate"), "%Y-%m-%d").date()

            home_team_json = game_json.get("homeTeam", {})
            away_team_json = game_json.get("awayTeam", {})
            home_team_goals = home_team_json.get("score", 0)
            away_team_goals = away_team_json.get("score", 0)

            # only create game data when it is not preseason game, in the past, has a winner, and doesn't already exist
            if game_type != Game.PRESEASON and Game.objects.filter(id=game_id).count() == 0:

                away_team_abbreviation = away_team_json.get("abbrev")
                away_team = Team.objects.filter(abbreviation=away_team_abbreviation).first()

                home_team_abbreviation = home_team_json.get("abbrev")
                home_team = Team.objects.filter(abbreviation=home_team_abbreviation).first()

                winning_team = None
                home_team_data = None
                away_team_data = None
                if game_date < current_date and get_team_data and not (home_team_goals == 0 and away_team_goals == 0):
                    winning_team = home_team if home_team_goals > away_team_goals else away_team
                    home_team_data = load_team_data_for_date_from_api(team=home_team,
                                                                    game_date=game_date)
                    away_team_data = load_team_data_for_date_from_api(team=away_team,
                                                                    game_date=game_date)
                    

                game = Game(id=game_id,
                            game_date=game_date,
                            game_json=game_json,
                            home_team=home_team,
                            away_team=away_team,
                            winning_team=winning_team,
                            home_team_data=home_team_data,
                            away_team_data=away_team_data)
                games_to_create.append(game)

                # check if home team data already exists in list
                if home_team_data is not None and home_team_data.pk is not None:
                    team_data_key = (home_team.id, home_team_data.data_capture_date)
                    if team_data_key not in existing_team_data_keys:
                        existing_team_data_keys.add(team_data_key)
                        team_data_to_create.append(home_team_data)

                # check if away team data already exists in list
                if away_team_data is not None and away_team_data.pk is not None:
                    team_data_key = (away_team.id, away_team_data.data_capture_date)
                    if team_data_key not in existing_team_data_keys:
                        existing_team_data_keys.add(team_data_key)
                        team_data_to_create.append(away_team_data)


    # bulk create and update the respective games
    TeamData.objects.bulk_create(team_data_to_create)
    Game.objects.bulk_create(games_to_create)

@transaction.atomic
def load_games_for_all_teams_from_api(seasons, get_team_data=True):
    teams = Team.objects.all()

    for team in teams:
        load_games_for_team_from_api(team_abbreviation=team.abbreviation,
                                     seasons=seasons,
                                     get_team_data=get_team_data)
    
@transaction.atomic
def clear_database():
    Team.objects.all().delete()
    Game.objects.all().delete()
    TeamData.objects.all().delete()

