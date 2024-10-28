import os
import httpx
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")

from django.conf import settings
from games.models import Franchise, Team, Game, TeamData
from datetime import datetime, timedelta
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
    print(franchise_url)
    franchise_response = httpx.get(franchise_url)
    print(franchise_response)

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
    current_date = datetime.now()
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
def create_or_update_team_data(team_standings, team, date):
    # get all remaining statistics from the json response
    season = team_standings.get("seasonId")
    games_played = team_standings.get("gamesPlayed")
    wins = team_standings.get("wins")
    losses = team_standings.get("losses")
    ot_losses = team_standings.get("otLosses")
    points = team_standings.get("points")
    goals_for = team_standings.get("goalFor")
    goals_against = team_standings.get("goalAgainst")
    goal_differential = team_standings.get("goalDifferential")
    l10_games_played = team_standings.get("l10GamesPlayed")
    l10_wins = team_standings.get("l10Wins")
    l10_losses = team_standings.get("l10Losses")
    streak_count = team_standings.get("streakCount", 0)
    streak_code = RESULT_MAP.get(team_standings.get("streakCode", "FG"))
    team_data = TeamData(team=team,
                        data_capture_date=date,
                        season=season,
                        games_played=games_played,
                        wins=wins,
                        losses=losses,
                        ot_losses=ot_losses,
                        points=points,
                        goals_for=goals_for,
                        goals_against=goals_against,
                        goal_differential=goal_differential,
                        l10_games_played=l10_games_played,
                        l10_wins=l10_wins,
                        l10_losses=l10_losses,
                        streak_count=streak_count,
                        streak_code=streak_code,
                        team_data_json=team_standings)
    
    team_data, _ = TeamData.objects.update_or_create(
        team=team,
        data_capture_date=date,
        defaults={
            'season': season,
            'team_data_json': team_standings,
            'games_played': games_played,
            'wins': wins,
            'losses': losses,
            'ot_losses': ot_losses,
            'points': points,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_differential': goal_differential,
            'l10_games_played': l10_games_played,
            'l10_wins': l10_wins,
            'l10_losses': l10_losses,
            'streak_count': streak_count,
            'streak_code': streak_code,
        }
    )

    return team_data

@transaction.atomic
def load_team_data_for_date_from_api(team_abbreviation, game_date):

    # ensure team exists
    team = Team.objects.filter(abbreviation=team_abbreviation).first()
    if team is None:
        return

    # get the date before a game
    previous_day = game_date - timedelta(days=1)

    # check to see if we already have the data for the given team and date
    previous_team_data = TeamData.objects.filter(team__abbreviation=team_abbreviation, data_capture_date=previous_day).first()


    # format the standings URL for the given date
    formatted_date = previous_day.strftime("%Y-%m-%d")
    standings_url = f"{settings.NHL_API_BASE_URL}standings/{formatted_date}"

    standings_response = httpx.get(standings_url)
    standings_json = standings_response.json().get("standings", [])

    if len(standings_json) != 0:
        for team_standings in standings_json:
            if team_standings.get("teamAbbrev", {}).get("default", "") == team_abbreviation:
                team_data = create_or_update_team_data(team_standings=team_standings,
                                                       team=team,
                                                       date=previous_day)
                return team_data
    else:
        # if standings is blank, it is the first game of the season, so only supply date and team
        # all other fields will default to zero
        if not TeamData.objects.filter(team=team, data_capture_date=previous_day).exists():
            team_data = TeamData(team=team,
                                data_capture_date=previous_day)
            team_data.save()

            return team_data
        else:
            return TeamData.objects.filter(team=team, data_capture_date=previous_day).first()

@transaction.atomic
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
    current_date = datetime.now().date()

    for season in seasons:
        # get schedule and all games for this season
        season_schedule_url = f"{settings.NHL_API_BASE_URL}club-schedule-season/{team_abbreviation}/{season}"
        season_schedule_response = httpx.get(season_schedule_url)
        season_schedule_json = season_schedule_response.json()
        games_json = season_schedule_json.get("games", [])

        # iterate over all games
        for game_json in games_json:
            game_id = game_json.get("id")
            game_season = game_json.get("season")
            game_type = game_json.get("gameType")

            # only create game data when it is not preseason game
            if game_type != Game.PRESEASON:
                game_date = datetime.strptime(game_json.get("gameDate"), "%Y-%m-%d").date()

                away_team_json = game_json.get("awayTeam", {})
                away_team_abbreviation = away_team_json.get("abbrev")
                away_team = Team.objects.filter(abbreviation=away_team_abbreviation).first()

                home_team_json = game_json.get("homeTeam", {})
                home_team_abbreviation = home_team_json.get("abbrev")
                home_team = Team.objects.filter(abbreviation=home_team_abbreviation).first()

                # fields for when the game has been completed
                home_team_goals = 0
                away_team_goals = 0
                is_overtime = False
                is_shootout = False
                winning_team = None
                home_team_data = None
                away_team_data = None
                if game_date < current_date:
                    home_team_goals = home_team_json.get("score", 0)
                    away_team_goals = away_team_json.get("score", 0)

                    if not (home_team_goals == 0 and away_team_goals ==0):
                        is_overtime = game_json.get("gameOutcome", {}).get("lastPeriodType", "REG") == "OT"
                        is_shootout = game_json.get("gameOutcome", {}).get("lastPeriodType", "REG") == "SO"

                        winning_team = home_team if home_team_goals > away_team_goals else away_team
                        home_team_data = load_team_data_for_date_from_api(team_abbreviation=home_team_abbreviation,
                                                                        game_date=game_date)
                        away_team_data = load_team_data_for_date_from_api(team_abbreviation=away_team_abbreviation,
                                                                        game_date=game_date)
                game = Game(id=game_id,
                            season=game_season,
                            home_team=home_team,
                            away_team=away_team,
                            winning_team=winning_team,
                            game_date=game_date,
                            game_type=game_type,
                            home_team_goals=home_team_goals,
                            away_team_goals=away_team_goals,
                            is_overtime=is_overtime,
                            is_shootout=is_shootout,
                            home_team_data=home_team_data,
                            away_team_data=away_team_data,
                            game_json=game_json)
                
                # if no game already exists, add it to the bulk_create list, otherwise add it to bulk_update list
                if Game.objects.filter(id=game_id).count() == 0:
                    games_to_create.append(game)
                else:
                    games_to_update.append(game)

    # bulk create and update the respective games
    Game.objects.bulk_create(games_to_create)
    Game.objects.bulk_update(games_to_update, fields=[
        'winning_team',
        'home_team_goals',
        'away_team_goals',
        'is_overtime',
        'is_shootout',
        'game_type',
        'game_date',
        'home_team_data',
        'away_team_data'
    ])

@transaction.atomic
def load_games_for_all_teams_from_api(past_seasons=0):
    teams = Team.objects.all()

    for team in teams:
        load_games_for_team_from_api(team_abbreviation=team.abbreviation,
                                     past_seasons=past_seasons)
    
@transaction.atomic
def clear_database():
    Team.objects.all().delete()
    Game.objects.all().delete()
    TeamData.objects.all().delete()

