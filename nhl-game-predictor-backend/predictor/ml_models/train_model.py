import os
import django
import pandas as pd
from games.models import Team, TeamData, Game
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor_backend")
django.setup()

class GameDataFrameEntry:
    """
    class to capture game data in pandas data frame used for training.
    all data must be integers, so this is why we have a separate class
    """
    def __init__(self, game : Game):
        # inputs
        game_json = game.game_json
        home_team_data = game.home_team_data
        away_team_data = game.home_team_data
        self.home_team = game.home_team.pk
        self.away_team = game.away_team.pk
        self.game_type = game.game_type

        # home team data
        self.home_team_games_played = home_team_data.games_played
        self.home_team_wins = home_team_data.wins
        self.home_team_losses = home_team_data.losses
        self.home_team_ot_losses = home_team_data.ot_losses
        self.home_team_points = home_team_data.points
        self.home_team_goals_for = home_team_data.goals_for
        self.home_team_goals_against = home_team_data.goals_against
        self.home_team_goal_differential = home_team_data.goal_differential
        self.home_team_l10_games_played = home_team_data.l10_games_played
        self.home_team_l10_wins = home_team_data.wins
        self.home_team_l10_losses = home_team_data.losses
        self.home_team_streak_count = home_team_data.streak_count
        self.home_team_streak_code = home_team_data.streak_code

        # Away team data
        self.away_team_games_played = away_team_data.games_played
        self.away_team_wins = away_team_data.wins
        self.away_team_losses = away_team_data.losses
        self.away_team_ot_losses = away_team_data.ot_losses
        self.away_team_points = away_team_data.points
        self.away_team_goals_for = away_team_data.goals_for
        self.away_team_goals_against = away_team_data.goals_against
        self.away_team_goal_differential = away_team_data.goal_differential
        self.away_team_l10_games_played = away_team_data.l10_games_played
        self.away_team_l10_wins = away_team_data.l10_wins  # Ensure this is the wins in the last 10 games
        self.away_team_l10_losses = away_team_data.l10_losses  # Ensure this is the losses in the last 10 games
        self.away_team_streak_count = away_team_data.streak_count
        self.away_team_streak_code = away_team_data.streak_code

        # labels (winning team, goals score for each team)
        self.winning_team = game.winning_team.pk
        self.home_team_goals = game.home_team_goals
        self.away_team_goals = game.away_team_goals