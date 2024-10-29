import os
import django
import pandas as pd
from games.models import Team, TeamData, Game
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor_backend")
django.setup()

class GameDataFrameEntry:
    def __init__(self, game: Game):
        game_json = game.game_json
        home_team_data = game.home_team_data
        home_team_data_json = home_team_data.team_data_json
        away_team_data = game.away_team_data
        away_team_data_json = away_team_data.team_data_json
        
        # general game data
        self.home_team = game.home_team.franchise.pk
        self.away_team = game.away_team.franchise.pk
        self.game_type = game_json.get("gameTypeId", 1)

        self.game_month = game.game_date.month
        self.game_day_of_week = game.game_date.weekday()

        # home team data (using rates)
        home_team_games_played = home_team_data_json.get("gamesPlayed", 1) if home_team_data_json.get("gamesPlayed", 1) != 0 else 1
        self.home_team_win_percentage = home_team_data_json.get("wins", 0) / home_team_games_played
        self.home_team_loss_percentage = home_team_data_json.get("losses", 0) / home_team_games_played
        self.home_team_ot_loss_percentage = home_team_data_json.get("otLosses", 0) / home_team_games_played
        self.home_team_goals_for_per_game = home_team_data_json.get("goalFor", 0) / home_team_games_played
        self.home_team_goals_against_per_game = home_team_data_json.get("goalAgainst", 0) / home_team_games_played
        self.home_team_goal_differential_per_game = home_team_data_json.get("goalDifferential", 0) / home_team_games_played


        home_team_l10_games_played = home_team_data_json.get("l10GamesPlayed", 1) if game.home_team_data.team_data_json.get("l10GamesPlayed") != 0 else 1
        self.home_team_l10_win_percentage = home_team_data_json.get("l10Wins", 0) / home_team_l10_games_played
        self.home_team_l10_loss_percentage = home_team_data_json.get("l10Losses", 0) / home_team_l10_games_played
        self.home_team_l10_ot_losses = home_team_data_json.get("l10OtLosses", 0) / home_team_l10_games_played
        self.home_team_l10_goals_for_per_game = home_team_data_json.get("l10GoalsFor", 0) / home_team_l10_games_played
        self.home_team_l10_goals_against_per_game = home_team_data_json.get("l10GoalsAgainst", 0) / home_team_l10_games_played
        self.home_team_l10_goal_differential_per_game = home_team_data_json.get("l10GoalDifferential", 0) / home_team_l10_games_played

        # home team home data
        home_games_played = home_team_data_json.get("homeGamesPlayed", 1) if home_team_data_json.get("homeGamesPlayed", 1) != 0 else 1
        self.home_team_home_win_percentage = home_team_data_json.get("homeWins", 0) / home_games_played 
        self.home_team_home_loss_percentage = home_team_data_json.get("homeLosses", 0) / home_games_played 
        self.home_team_home_ot_loss_percentage = home_team_data_json.get("homeOtLosses", 0) / home_games_played 
        self.home_team_home_goals_for_per_game = home_team_data_json.get("homeGoalsFor", 0) / home_games_played 
        self.home_team_home_goals_against_per_game = home_team_data_json.get("homeGoalsAgainst", 0) / home_games_played 
        self.home_team_home_goal_differential_per_game = home_team_data_json.get("homeGoalDifferent", 0) / home_games_played


        # away team data (using rates)
        away_team_games_played = away_team_data_json.get("gamesPlayed", 1) if away_team_data_json.get("gamesPlayed", 1) != 0 else 1
        self.away_team_win_percentage = away_team_data_json.get("wins", 0) / away_team_games_played 
        self.away_team_loss_percentage = away_team_data_json.get("losses", 0) / away_team_games_played 
        self.away_team_ot_loss_percentage = away_team_data_json.get("otLosses", 0) / away_team_games_played 
        self.away_team_goals_for_per_game = away_team_data_json.get("goalFor", 0) / away_team_games_played 
        self.away_team_goals_against_per_game = away_team_data_json.get("goalAgainst", 0) / away_team_games_played 
        self.away_team_goal_differential_per_game = away_team_data_json.get("goalDifferential", 0) / away_team_games_played 


        away_team_l10_games_played = away_team_data_json.get("l10GamesPlayed", 1) if away_team_data_json.get("l10GamesPlayed") != 0 else 1
        self.away_team_l10_win_percentage = away_team_data_json.get("l10Wins", 0) / away_team_l10_games_played
        self.away_team_l10_loss_percentage = away_team_data_json.get("l10Losses", 0) / away_team_l10_games_played
        self.away_team_l10_ot_losses = away_team_data_json.get("l10OtLosses", 0) / away_team_l10_games_played
        self.away_team_l10_goals_for_per_game = away_team_data_json.get("l10GoalsFor", 0) / away_team_l10_games_played
        self.away_team_l10_goals_against_per_game = away_team_data_json.get("l10GoalsAgainst", 0) / away_team_l10_games_played
        self.away_team_l10_goal_differential_per_game = away_team_data_json.get("l10GoalDifferential", 0) / away_team_l10_games_played

        # away team road data
        away_games_played = away_team_data_json.get("roadGamesPlayed", 1) if away_team_data_json.get("roadGamesPlayed", 1) != 0 else 1
        self.away_team_road_win_percentage = away_team_data_json.get("roadWins", 0) / away_games_played 
        self.away_team_road_loss_percentage = away_team_data_json.get("roadLosses", 0) / away_games_played 
        self.away_team_road_ot_loss_percentage = away_team_data_json.get("roadOtLosses", 0) / away_games_played 
        self.away_team_road_goals_for_per_game = away_team_data_json.get("roadGoalsFor", 0) / away_games_played 
        self.away_team_road_goals_against_per_game = away_team_data_json.get("roadGoalsAgainst", 0) / away_games_played 
        self.away_team_road_goal_differential_per_game = away_team_data_json.get("roadGoalDifferential", 0) / away_games_played 

        # labels
        self.home_team_win = 1 if game.winning_team == game.home_team else 0


    def to_dict(self):
        """
        Convert the instance to a dictionary for easy DataFrame creation.
        """
        return {
            "home_team": self.home_team,
            "away_team": self.away_team,
            "game_type": self.game_type,
            "game_month": self.game_month,
            "game_day_of_week": self.game_day_of_week,
            # Home team overall percentage metrics
            "home_team_win_percentage": self.home_team_win_percentage,
            "home_team_loss_percentage": self.home_team_loss_percentage,
            "home_team_ot_loss_percentage": self.home_team_ot_loss_percentage,
            "home_team_goals_for_per_game": self.home_team_goals_for_per_game,
            "home_team_goals_against_per_game": self.home_team_goals_against_per_game,
            "home_team_goal_differential_per_game": self.home_team_goal_differential_per_game,
            # Home team last 10 games data
            "home_team_l10_win_percentage": self.home_team_l10_win_percentage,
            "home_team_l10_loss_percentage": self.home_team_l10_loss_percentage,
            "home_team_l10_ot_losses": self.home_team_l10_ot_losses,
            "home_team_l10_goals_for_per_game": self.home_team_l10_goals_for_per_game,
            "home_team_l10_goals_against_per_game": self.home_team_l10_goals_against_per_game,
            "home_team_l10_goal_differential_per_game": self.home_team_l10_goal_differential_per_game,

            # Home team home data
            "home_team_home_win_percentage": self.home_team_home_win_percentage,
            "home_team_home_loss_percentage": self.home_team_home_loss_percentage,
            "home_team_home_ot_loss_percentage": self.home_team_home_ot_loss_percentage,
            "home_team_home_goals_for_per_game": self.home_team_home_goals_for_per_game,
            "home_team_home_goals_against_per_game": self.home_team_home_goals_against_per_game,
            "home_team_home_goal_differential_per_game": self.home_team_home_goal_differential_per_game,

            # Away team overall percentage metrics
            "away_team_win_percentage": self.away_team_win_percentage,
            "away_team_loss_percentage": self.away_team_loss_percentage,
            "away_team_ot_loss_percentage": self.away_team_ot_loss_percentage,
            "away_team_goals_for_per_game": self.away_team_goals_for_per_game,
            "away_team_goals_against_per_game": self.away_team_goals_against_per_game,
            "away_team_goal_differential_per_game": self.away_team_goal_differential_per_game,
            "away_team_l10_win_percentage": self.away_team_l10_win_percentage,
            "away_team_l10_loss_percentage": self.away_team_l10_loss_percentage,
            "away_team_l10_ot_losses": self.away_team_l10_ot_losses,
            "away_team_l10_goals_for_per_game": self.away_team_l10_goals_for_per_game,
            "away_team_l10_goals_against_per_game": self.away_team_l10_goals_against_per_game,
            "away_team_l10_goal_differential_per_game": self.away_team_l10_goal_differential_per_game,

            # Away team road data
            "away_team_road_win_percentage": self.away_team_road_win_percentage,

            # Away team road data
            "away_team_road_win_percentage": self.away_team_road_win_percentage,
            "away_team_road_loss_percentage": self.away_team_road_loss_percentage,
            "away_team_road_ot_loss_percentage": self.away_team_road_ot_loss_percentage,
            "away_team_road_goals_for_per_game": self.away_team_road_goals_for_per_game,
            "away_team_road_goals_against_per_game": self.away_team_road_goals_against_per_game,
            "away_team_road_goal_differential_per_game": self.away_team_road_goal_differential_per_game,

            # label is a simple binary decision of did the home team win or not
            "home_team_win": self.home_team_win,
        }



def generate_past_season_ids(past_seasons):
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    if current_month >= 7:  # July or later
        current_season_start_year = current_year
    else:  # January to June
        current_season_start_year = current_year - 1

    season_ids = []
    
    for i in range(past_seasons):
        year_start = current_season_start_year - (i + 1)
        season_id = f"{year_start}{year_start + 1}"
        season_ids.append(int(season_id))
    
    return season_ids

def create_data_frame(past_seasons):
    seasons = generate_past_season_ids(past_seasons)
    # Fetch all Game records for the specified past seasons
    games = Game.objects.filter(game_json__season__in=seasons).exclude(home_team_data=None, away_team_data=None)

    # Create GameDataFrameEntry instances for each game
    game_dataframe_entries = [GameDataFrameEntry(game) for game in games]

    # Convert the list of entries to a list of dictionaries
    game_data_dicts = [entry.to_dict() for entry in game_dataframe_entries]

    # Create a DataFrame from the list of dictionaries
    game_data_df = pd.DataFrame(game_data_dicts)

    return game_data_df