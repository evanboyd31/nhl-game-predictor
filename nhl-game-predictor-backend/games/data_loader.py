import os
import httpx
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")
django.setup()

from django.conf import settings
from games.models import Franchise, Team, Game, TeamData, Season
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

def convert_game_json_to_game_data_objects(game_json : dict, date_string : str, get_team_data : bool = False):
    """
    converts a single game's JSON from the NHL API into Game and TeamData
    Django model instances. Optionally, TeamData instances are created as well.
    """

    game_id = game_json.get("id")
    game_date = datetime.strptime(date_string, "%Y-%m-%d").date()
    current_date = timezone.localdate()

    home_team_json = game_json.get("homeTeam", {})
    away_team_json = game_json.get("awayTeam", {})
    home_team_goals = home_team_json.get("score", 0)
    away_team_goals = away_team_json.get("score", 0)

    # only create game data when it doesn't already exist
    game = None
    home_team_data = None
    away_team_data = None
    if Game.objects.filter(id=game_id).count() == 0:

        away_team_abbreviation = away_team_json.get("abbrev")
        away_team = Team.objects.filter(abbreviation=away_team_abbreviation).first()

        home_team_abbreviation = home_team_json.get("abbrev")
        home_team = Team.objects.filter(abbreviation=home_team_abbreviation).first()

        # handle case where games are between an NHL team and non-NHL team (e.g., 2022010107, NSH vs SC Bern)
        if home_team is None or away_team is None:
            return None, None, None

        winning_team = None
        if home_team_goals != away_team_goals:
            winning_team = home_team if home_team_goals > away_team_goals else away_team

        if get_team_data and current_date <= game_date:
            home_team_data = load_team_data_for_date_from_api(team=home_team,
                                                              game_date=game_date)
            away_team_data = load_team_data_for_date_from_api(team=away_team,
                                                              game_date=game_date)
            
        
        # assign game to season model
        season_id = game_json.get("season")
        season = Season.objects.filter(id=season_id).first()
        
        game = Game(id=game_id,
                    season=season,
                    game_date=game_date,
                    game_json=game_json,
                    home_team=home_team,
                    away_team=away_team,
                    winning_team=winning_team,
                    home_team_data=home_team_data,
                    away_team_data=away_team_data)
    
    return game, home_team_data, away_team_data

@transaction.atomic
def fetch_games_for_date(date : datetime, get_team_data : bool = True):
    """
    fetches game JSONs from the NHL api and create Game
    Django objects. Optionally, TeamData objects are recorded as well.
    Returns True in the case that there are games on the given date,
    False otherwise.
    """

    # first check to see if the games already exist before calling API
    games_for_date_in_db = Game.objects.filter(game_date=date)
    if games_for_date_in_db.exists():
        return games_for_date_in_db
    
    date_string = date.strftime("%Y-%m-%d")
    schedule_url = f"https://api-web.nhle.com/v1/schedule/{date_string}"
    schedule_response = httpx.get(schedule_url)
    response_json = schedule_response.json()
    games_for_date_json = response_json.get("gameWeek")[0].get("games", [])
    games_to_create = []
    team_data_to_create = []

    # iterate over all games
    for game_json in games_for_date_json:
        game, home_team_data, away_team_data = convert_game_json_to_game_data_objects(game_json=game_json,
                                                                                      date_string=date_string,
                                                                                      get_team_data=True)
        if game is not None:
            games_to_create.append(game)
        if home_team_data is not None:
            team_data_to_create.append(home_team_data)
        if away_team_data is not None:
            team_data_to_create.append(away_team_data)

    TeamData.objects.bulk_create(team_data_to_create)
    Game.objects.bulk_create(games_to_create)

    return Game.objects.filter(game_date=date)

@transaction.atomic
def load_franchises_and_teams_data_from_api():
    """
    using the official NHL API, this function gets a list of all franchises
    that have ever existed in the NHL, and creates new Franchise model instances
    to represent them
    """

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
    into a Team model instance and store in the database
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
def load_team_data_for_date_from_api(team : Team, game_date : datetime):
    """
    creates a TeamData instance for a particular game. a TeamData
    instance is the team's statistics on the day prior to the game, as provided
    by the official NHL API
    """

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
        return TeamData(team_data_json={},
                        team=team,
                        data_capture_date=previous_day)

@transaction.atomic
def load_games_for_team_from_api(team_abbreviation : str, seasons : list, get_team_data : bool = True):
    """
    given the abbreviation of a team, load Game and TeamData model instances
    into the database. 
    
    the seasons parameter is a list of season IDs that are compliant with the NHL API.
    For example, the 2024-2025 season has an ID of 20242025

    TeamData instances are the team's statistics a day prior to a Game
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
def load_games_for_all_teams_from_api(seasons : list, get_team_data : bool = True):
    """
    given a list of season ids (such as [20202021, 20212022]), get all
    NHL games for each of the seasons. optionally, create TeamData instances,
    which are each team's statistics the day prior to a game
    """
    teams = Team.objects.all()

    for team in teams:
        load_games_for_team_from_api(team_abbreviation=team.abbreviation,
                                     seasons=seasons,
                                     get_team_data=get_team_data)
    
@transaction.atomic
def clear_database():
    """
    function used to manually clear all instances in the database from
    the Django shell
    """
    Team.objects.all().delete()
    Game.objects.all().delete()
    TeamData.objects.all().delete()

@transaction.atomic
def update_completed_games() -> list:
    """
    for all games in the database that have been completed but do not yet
    have a winning team recorded, fetch the latest game JSON from the NHL API,
    update the game_json field, and store the winning team. also fetch
    TeamData for each team if it has not yet been created.
    returns a list of all updated Game instances.
    """

    today = timezone.localdate()
    completed_games_dates = Game.objects.filter(winning_team__isnull=True, game_date__lt=today).values_list("game_date", flat=True).distinct()
    games_to_update = []
    team_datas_to_create = []

    for game_date in completed_games_dates:
        date_string = game_date.strftime("%Y-%m-%d")
        schedule_url = f"https://api-web.nhle.com/v1/schedule/{date_string}"
        schedule_response = httpx.get(schedule_url)
        response_json = schedule_response.json()
        games_for_date_json = response_json.get("gameWeek")[0].get("games", [])

        for game_json in games_for_date_json:
            game = Game.objects.filter(id=game_json.get("id")).first()
            if game is not None:
                # update the game_json field
                game.game_json = game_json

                # find the winning team and store
                home_team_json = game_json.get("homeTeam", {})
                away_team_json = game_json.get("awayTeam", {})
                home_team_goals = home_team_json.get("score", 0)
                away_team_goals = away_team_json.get("score", 0)

                away_team_abbreviation = away_team_json.get("abbrev")
                away_team = Team.objects.filter(abbreviation=away_team_abbreviation).first()

                home_team_abbreviation = home_team_json.get("abbrev")
                home_team = Team.objects.filter(abbreviation=home_team_abbreviation).first()

                winning_team = home_team if home_team_goals > away_team_goals else away_team
                game.winning_team = winning_team

                # fetch team data if it has not yet been created
                if game.home_team_data is None:
                    home_team_data = load_team_data_for_date_from_api(team=home_team,
                                                                    game_date=game_date)
                    if home_team_data is not None:
                        team_datas_to_create.append(home_team_data)
                    
                if game.away_team_data is None:
                    away_team_data = load_team_data_for_date_from_api(team=away_team,
                                                                    game_date=game_date)
                    if away_team_data is not None:
                        team_datas_to_create.append(away_team_data)

                games_to_update.append(game)

    if team_datas_to_create:
        TeamData.objects.bulk_create(team_datas_to_create)
    
    if games_to_update:
        Game.objects.bulk_update(games_to_update,
                                 ["game_json", "winning_team", "home_team_data", "away_team_data"])
        
    return games_to_update