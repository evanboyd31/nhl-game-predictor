from predictor.ml_models.utils import POSSIBLE_GAME_FRANCHISE_IDS

"""
provided an integer in the range [1, 12], this dictionary
maps the integer to the corresponding month name
"""
month_dictionary = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

month_feature_descriptions = {
    f"game_month_{month_num}": lambda game: f"The game is in {month_name}"
    for month_num, month_name in month_dictionary.items()
}


"""
provided an integer in the range [0, 6], this dictionary
maps the integer to the corresponding day of week name
"""
weekday_dictionary = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

weekday_feature_descriptions = {
    f"game_day_of_week_{weekday_num}": lambda game: f"The game is on a {weekday_name}"
    for weekday_num, weekday_name in weekday_dictionary.items()
}

"""
provided an integer in the range [1, 3], this dictionary
maps the integer to the corresponding game type description
"""
game_type_dictionary = {
  1: "The game is a preseason game",
  2: "The game is a regular season game",
  3: "The game is a playoff game"
}

game_type_feature_descriptions = {
    f"game_type_{game_type_num}": lambda game: description
    for game_type_num, description in game_type_dictionary.items()
}

"""
given a feature name used in the machine learning training, this dictionary 
provides a function that, when given the instance of the Game, will be formatted 
into a string that is descriptive and contains relevant stats. useful for displaying
feature importances in the React frontend
"""
cleaned_feature_names_dictionary = {
    "home_team": lambda game: f"The {game.home_team.name} are the home team",
    "away_team": lambda game: f"The {game.away_team.name} are the away team",

    # Home team overall metrics
    "home_team_win_percentage": lambda game: f"The {game.home_team.name} have a win percentage of {(game.home_team_data.team_data_json.get('wins', 0) / max(1, game.home_team_data.team_data_json.get('gamesPlayed', 1))) * 100:.2f}%",
    "home_team_loss_percentage": lambda game: f"The {game.home_team.name} have a regulation loss percentage of {(game.home_team_data.team_data_json.get('losses', 0) / max(1, game.home_team_data.team_data_json.get('gamesPlayed', 1))) * 100:.2f}%",
    "home_team_ot_loss_percentage": lambda game: f"The {game.home_team.name} have an overtime loss percentage of {(game.home_team_data.team_data_json.get('otLosses', 0) / max(1, game.home_team_data.team_data_json.get('gamesPlayed', 1))) * 100:.2f}%",
    "home_team_goals_for_per_game": lambda game: f"The {game.home_team.name} score an average of {(game.home_team_data.team_data_json.get('goalFor', 0) / max(1, game.home_team_data.team_data_json.get('gamesPlayed', 1))):.2f} goals per game",
    "home_team_goals_against_per_game": lambda game: f"The {game.home_team.name} allow an average of {(game.home_team_data.team_data_json.get('goalAgainst', 0) / max(1, game.home_team_data.team_data_json.get('gamesPlayed', 1))):.2f} goals against per game",
    "home_team_goal_differential_per_game": lambda game: f"The {game.home_team.name} have a goal differential of {(game.home_team_data.team_data_json.get('goalDifferential', 0) / max(1, game.home_team_data.team_data_json.get('gamesPlayed', 1))):.2f} per game",

    # Home team last 10 games data
    "home_team_l10_win_percentage": lambda game: f"In the last 10 games, the {game.home_team.name} have a win percentage of {(game.home_team_data.team_data_json.get('l10Wins', 0) / max(1, game.home_team_data.team_data_json.get('l10GamesPlayed', 1))) * 100:.2f}%",
    "home_team_l10_loss_percentage": lambda game: f"In the last 10 games, the {game.home_team.name} have a regulation loss percentage of {(game.home_team_data.team_data_json.get('l10Losses', 0) / max(1, game.home_team_data.team_data_json.get('l10GamesPlayed', 1))) * 100:.2f}%",
    "home_team_l10_ot_losses": lambda game: f"The {game.home_team.name} have an overtime loss percentage of {(game.home_team_data.team_data_json.get('l10OtLosses', 0) / max(1, game.home_team_data.team_data_json.get('l10GamesPlayed', 1))) * 100:.2f}% in the last 10 games",
    "home_team_l10_goals_for_per_game": lambda game: f"The {game.home_team.name} scored an average of {(game.home_team_data.team_data_json.get('l10GoalsFor', 0) / max(1, game.home_team_data.team_data_json.get('l10GamesPlayed', 1))):.2f} goals per game in the last 10 games",
    "home_team_l10_goals_against_per_game": lambda game: f"The {game.home_team.name} allowed an average of {(game.home_team_data.team_data_json.get('l10GoalsAgainst', 0) / max(1, game.home_team_data.team_data_json.get('l10GamesPlayed', 1))):.2f} goals against per game in the last 10 games",
    "home_team_l10_goal_differential_per_game": lambda game: f"The {game.home_team.name} have a goal differential of {(game.home_team_data.team_data_json.get('l10GoalDifferential', 0) / max(1, game.home_team_data.team_data_json.get('l10GamesPlayed', 1))):.2f} per game in the last 10 games",

    # Home team home data
    "home_team_home_win_percentage": lambda game: f"At home, the {game.home_team.name} have a win percentage of {(game.home_team_data.team_data_json.get('homeWins', 0) / max(1, game.home_team_data.team_data_json.get('homeGamesPlayed', 1))) * 100:.2f}%",
    "home_team_home_loss_percentage": lambda game: f"At home, the {game.home_team.name} have a regulation loss percentage of {(game.home_team_data.team_data_json.get('homeLosses', 0) / max(1, game.home_team_data.team_data_json.get('homeGamesPlayed', 1))) * 100:.2f}%",
    "home_team_home_ot_loss_percentage": lambda game: f"At home, the {game.home_team.name} have an overtime loss percentage of {(game.home_team_data.team_data_json.get('homeOtLosses', 0) / max(1, game.home_team_data.team_data_json.get('homeGamesPlayed', 1))) * 100:.2f}%",

    # Away team overall metrics
    "away_team_win_percentage": lambda game: f"The {game.away_team.name} have a win percentage of {(game.away_team_data.team_data_json.get('wins', 0) / max(1, game.away_team_data.team_data_json.get('gamesPlayed', 1))) * 100:.2f}%",
    "away_team_loss_percentage": lambda game: f"The {game.away_team.name} have a regulation loss percentage of {(game.away_team_data.team_data_json.get('losses', 0) / max(1, game.away_team_data.team_data_json.get('gamesPlayed', 1))) * 100:.2f}%",
    "away_team_ot_loss_percentage": lambda game: f"The {game.away_team.name} have an overtime loss percentage of {(game.away_team_data.team_data_json.get('otLosses', 0) / max(1, game.away_team_data.team_data_json.get('gamesPlayed', 1))) * 100:.2f}%",
    "away_team_goals_for_per_game": lambda game: f"The {game.away_team.name} score an average of {(game.away_team_data.team_data_json.get('goalFor', 0) / max(1, game.away_team_data.team_data_json.get('gamesPlayed', 1))):.2f} goals per game",
    "away_team_goals_against_per_game": lambda game: f"The {game.away_team.name} allow an average of {(game.away_team_data.team_data_json.get('goalAgainst', 0) / max(1, game.away_team_data.team_data_json.get('gamesPlayed', 1))):.2f} goals against per game",
    "away_team_goal_differential_per_game": lambda game: f"The {game.away_team.name} have a goal differential of {(game.away_team_data.team_data_json.get('goalDifferential', 0) / max(1, game.away_team_data.team_data_json.get('gamesPlayed', 1))):.2f} per game",

    # Away team last 10 games data
    "away_team_l10_win_percentage": lambda game: f"In the last 10 games, the {game.away_team.name} have a win percentage of {(game.away_team_data.team_data_json.get('l10Wins', 0) / max(1, game.away_team_data.team_data_json.get('l10GamesPlayed', 1))) * 100:.2f}%",
    "away_team_l10_loss_percentage": lambda game: f"In the last 10 games, the {game.away_team.name} have a regulation loss percentage of {(game.away_team_data.team_data_json.get('l10Losses', 0) / max(1, game.away_team_data.team_data_json.get('l10GamesPlayed', 1))) * 100:.2f}%",
    "away_team_l10_ot_losses": lambda game: f"In the last 10 games, the {game.away_team.name} have an overtime loss percentage of {(game.away_team_data.team_data_json.get('l10OtLosses', 0) / max(1, game.away_team_data.team_data_json.get('l10GamesPlayed', 1))) * 100:.2f}%",
    "away_team_l10_goals_for_per_game": lambda game: f"In the last 10 games, the {game.away_team.name} score an average of {(game.away_team_data.team_data_json.get('l10GoalsFor', 0) / max(1, game.away_team_data.team_data_json.get('l10GamesPlayed', 1))):.2f} goals per game",
    "away_team_l10_goals_against_per_game": lambda game: f"In the last 10 games, the {game.away_team.name} allow an average of {(game.away_team_data.team_data_json.get('l10GoalsAgainst', 0) / max(1, game.away_team_data.team_data_json.get('l10GamesPlayed', 1))):.2f} goals against per game",
    "away_team_l10_goal_differential_per_game": lambda game: f"In the last 10 games, the {game.away_team.name} have a goal differential of {(game.away_team_data.team_data_json.get('l10GoalDifferential', 0) / max(1, game.away_team_data.team_data_json.get('l10GamesPlayed', 1))):.2f} per game",

    # Away team road data
    "away_team_road_win_percentage": lambda game: f"On the road, the {game.away_team.name} have a win percentage of {(game.away_team_data.team_data_json.get('roadWins', 0) / max(1, game.away_team_data.team_data_json.get('roadGamesPlayed', 1))) * 100:.2f}%",
    "away_team_road_loss_percentage": lambda game: f"On the road, the {game.away_team.name} have a regulation loss percentage of {(game.away_team_data.team_data_json.get('roadLosses', 0) / max(1, game.away_team_data.team_data_json.get('roadGamesPlayed', 1))) * 100:.2f}%",
    "away_team_road_ot_loss_percentage": lambda game: f"On the road, the {game.away_team.name} have an overtime loss percentage of {(game.away_team_data.team_data_json.get('roadOtLosses', 0) / max(1, game.away_team_data.team_data_json.get('roadGamesPlayed', 1))) * 100:.2f}%",
    "away_team_road_goals_for_per_game": lambda game: f"On the road, the {game.away_team.name} score an average of {(game.away_team_data.team_data_json.get('roadGoalsFor', 0) / max(1, game.away_team_data.team_data_json.get('roadGamesPlayed', 1))):.2f} goals per game",
    "away_team_road_goals_against_per_game": lambda game: f"On the road, the {game.away_team.name} allow an average of {(game.away_team_data.team_data_json.get('roadGoalsAgainst', 0) / max(1, game.away_team_data.team_data_json.get('roadGamesPlayed', 1))):.2f} goals against per game",
    "away_team_road_goal_differential_per_game": lambda game: f"On the road, the {game.away_team.name} have a goal differential of {(game.away_team_data.team_data_json.get('roadGoalDifferential', 0) / max(1, game.away_team_data.team_data_json.get('roadGamesPlayed', 1))):.2f} per game",

    # Label for outcome
    "home_team_win": lambda game: "The home team won" if game.home_team_win else "The home team lost",
}

cleaned_feature_names_dictionary.update(month_feature_descriptions)
cleaned_feature_names_dictionary.update(weekday_feature_descriptions)
cleaned_feature_names_dictionary.update(game_type_feature_descriptions)

