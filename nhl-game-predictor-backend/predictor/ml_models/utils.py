from games.models import Game, Franchise
import os
import django
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor_backend")
django.setup()

CATEGORICAL_FEATURE_NAMES = [
        "home_team",
        "away_team",
        "game_type",
        "game_day_of_week",
        "game_month"
    ]

# we only consider franchises that have participated in a game that is stored in the DB, not all franchises
# otherwise, a lot of the data columns would go unused
POSSIBLE_GAME_FRANCHISE_IDS = Franchise.objects.filter(
    teams__in=Game.objects.values_list("home_team", flat=True).union(
        Game.objects.values_list("away_team", flat=True)
        )
).distinct().order_by("id").values_list("id", flat=True)

GAME_TYPES = [
    Game.PRESEASON,
    Game.REGULAR_SEASON,
    Game.PLAYOFFS
]

GAME_DAYS_OF_WEEK = list(range(7))

GAME_MONTHS = list(range(1, 13))

def categorical_feature_column_name_prefix(categorical_feature_name, categorical_feature_value):
    """
    creates a name for a categorical feature column based on the name of the feature
    and the value is takes on
    """
    return f"{categorical_feature_name}_{categorical_feature_value}"

def one_hot_encode_game_df(game_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode known categorical columns of the input DataFrame,
    ensuring all expected dummy columns exist, even if missing from input.
    """

    game_data_df = pd.get_dummies(game_data_df, 
                                  columns=CATEGORICAL_FEATURE_NAMES, 
                                  dtype=int)

    # ensure all expected one-hot columns are present (even if not in this row)
    expected_columns = []

    for categorical_feature_name, categorical_feature_values in {
        "home_team": POSSIBLE_GAME_FRANCHISE_IDS,
        "away_team": POSSIBLE_GAME_FRANCHISE_IDS,
        "game_type": GAME_TYPES,
        "game_day_of_week": GAME_DAYS_OF_WEEK,
        "game_month": GAME_MONTHS,
    }.items():
        expected_columns += [f"{categorical_feature_name}_{categorical_feature_value}" for categorical_feature_value in categorical_feature_values]

    # add any missing one-hot columns with 0s
    for column in expected_columns:
        if column not in game_data_df.columns:
            game_data_df[column] = 0

    # sort to ensure consistent column order
    return game_data_df.reindex(sorted(game_data_df.columns), axis=1)

class GameDataFrameEntry:
    """
    class to represent a Game model instance
    as an entry in a pandas dataframe used for training
    a Random Forest model
    """

    def __init__(self, game: Game):
        self.game = game
        game_json = game.game_json
        home_team_data = game.home_team_data
        home_team_data_json = {} if home_team_data is None else home_team_data.team_data_json
        away_team_data = game.away_team_data
        away_team_data_json = {} if away_team_data is None else away_team_data.team_data_json
        
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


        home_team_l10_games_played = home_team_data_json.get("l10GamesPlayed", 1) if home_team_data_json.get("l10GamesPlayed") != 0 else 1
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
        convert the GameDataFrameEntry instance to a dictionary for easy DataFrame creation
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