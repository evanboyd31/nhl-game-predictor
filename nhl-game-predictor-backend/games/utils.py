from games.models import Game, Team
from django.db.models import Q, QuerySet
from predictor.ml_models.utils import GameDataFrameEntry

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

"""
given a feature name used in the machine learning training, this dictionary 
provides a function that, when given the instance of the Game, will be formatted 
into a string that is descriptive and contains relevant stats. useful for displaying
feature importances in the React frontend
"""
cleaned_feature_names_dictionary = {
    "home_team": lambda game: f"The {game.home_team.name} are the home team",
    "away_team": lambda game: f"The {game.away_team.name} are the away team",
    "game_type": lambda game: "The game is a regular season game" if game.game_json.get("gameTypeId") == 1 else "The game is a playoff game",
    "game_month": lambda game: f"The game is in {month_dictionary[game.game_date.month]}",
    "game_day_of_week": lambda game: f"The game is on a {weekday_dictionary[game.game_date.weekday()]}",

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

def get_current_season_id():
    """
    this function returns the season id of the current NHL season
    it assumes that the games stored in the database are up to date
    """

    latest_game = Game.objects.latest("game_date")
    latest_game_season = latest_game.game_json.get("season")
    return latest_game_season

def get_game_type_games_for_team_and_before_date_this_season(team_id : int, date, game_type : int):
    current_season_id = get_current_season_id()
    games = Game.objects.filter(Q(home_team__id=team_id) | Q(away_team__id=team_id),
                                game_date__lt=date,
                                game_json__season=current_season_id,
                                game_json__gameType=game_type)
    return games

def get_preseason_games_for_team_and_before_date_this_season(team_id : int, date):
    return get_game_type_games_for_team_and_before_date_this_season(team_id=team_id,
                                                                    date=date,
                                                                    game_type=Game.PRESEASON)

def get_playoff_games_for_team_and_before_date_this_season(team_id : int, date):
    return get_game_type_games_for_team_and_before_date_this_season(team_id=team_id, 
                                                                    date=date,
                                                                    game_type=Game.PLAYOFFS)


def compute_stats_over_games_queryset(games_queryset : QuerySet[Game], team : Team, is_home_team : bool):
    if not games_queryset.exists():
        win_percentage = 0
        loss_percentage = 0
        ot_loss_percentage = 0
        goals_for_per_game = 0
        goals_against_per_game = 0
        goal_differential_per_game = 0

        l10_win_percentage = 0
        l10_loss_percentage = 0
        l10_ot_losses = 0
        l10_goals_for_per_game = 0
        l10_goals_against_per_game = 0
        l10_goal_differential_per_game = 0

        if is_home_team:
            home_win_percentage = 0
            home_loss_percentage = 0
            home_ot_loss_percentage = 0
            home_goals_for_per_game = 0
            home_goals_against_per_game = 0
            home_goal_differential_per_game = 0
        else:
            away_win_percentage = 0
            away_loss_percentage = 0
            away_ot_loss_percentage = 0
            away_goals_for_per_game = 0
            away_goals_against_per_game = 0
            away_goal_differential_per_game = 0
    else:
        total_games = games_queryset.count()
        total_home_games = games_queryset.filter(home_team=team).count()
        total_away_games = games_queryset.filter(away_team=team).count()
        for game in games_queryset:
            wins += 1 if game.winning_team == team else 0
            losses += 1 if game.winning_team != team else 0
            ot_losses += 1 if game.game_json.get("gameOutcome").get("lastPeriodType") == "OT" and game.winning_team != team else 0
            goals_for += game.game_json.get("homeTeam").get("score") if game.home_team == team else game.game_json.get("awayTeam").get("score")
            goals_against += game.game_json.get("homeTeam").get("score") if game.away_team == team else game.game_json.get("awayTeam").get("score")
            goal_differential += game.game_json.get("homeTeam").get("score") - game.game_json.get("awayTeam").get("score") if game.home_team == team else game.game_json.get("awayTeam").get("score") - game.game_json.get("homeTeam").get("score")

            if is_home_team:
                home_wins += 1 if game.winning_team == team and game.home_team == team else 0
                home_losses += 1 if game.winning_team != team and game.home_team == team else 0
                home_ot_losses += 1 if game.game_json.get("gameOutcome").get("lastPeriodType") == "OT" and game.winning_team != team and game.home_team == team else 0
                home_goals_for += game.game_json.get("homeTeam").get("score") if game.home_team == team else 0
                home_goals_against += game.game_json.get("awayTeam").get("score") if game.home_team == team else 0
                home_goal_differential += game.game_json.get("homeTeam").get("score") - game.game_json.get("awayTeam").get("score") if game.home_team == team else 0
            else:
                away_wins += 1 if game.winning_team == team and game.away_team == team else 0
                away_losses += 1 if game.winning_team != team and game.away_team == team else 0
                away_ot_losses += 1 if game.game_json.get("gameOutcome").get("lastPeriodType") == "OT" and game.winning_team != team and game.away_team == team else 0
                away_goals_for += game.game_json.get("awayTeam").get("score") if game.away_team == team else 0
                away_goals_against += game.game_json.get("homeTeam").get("score") if game.away_team == team else 0
                away_goal_differential += game.game_json.get("awayTeam").get("score") - game.game_json.get("homeTeam").get("score") if game.away_team == team else 0

        last_ten_games = games_queryset.order_by("game_date")[:10]
        for game in last_ten_games:
            l10_wins += 1 if game.winning_team == team else 0
            l10_losses += 1 if game.winning_team != team else 0
            l10_ot_losses += 1 if game.game_json.get("gameOutcome").get("lastPeriodType") == "OT" and game.winning_team != team else 0
            l10_goals_for += game.game_json.get("homeTeam").get("score") if game.home_team == team else game.game_json.get("awayTeam").get("score")
            l10_goals_against += game.game_json.get("homeTeam").get("score") if game.away_team == team else game.game_json.get("awayTeam").get("score")
            l10_goal_differential += game.game_json.get("homeTeam").get("score") - game.game_json.get("awayTeam").get("score") if game.home_team == team else game.game_json.get("awayTeam").get("score") - game.game_json.get("homeTeam").get("score")

        win_percentage = wins / total_games
        loss_percentage = losses / total_games
        ot_loss_percentage = ot_losses / total_games
        goals_for_per_game = goals_for / total_games
        goals_against_per_game = goals_against / total_games
        goal_differential_per_game = goal_differential / total_games

        l10_win_percentage = l10_wins / 10
        l10_loss_percentage = l10_losses / 10
        l10_ot_losses = l10_ot_losses / 10
        l10_goals_for_per_game = l10_goals_for / 10
        l10_goals_against_per_game = l10_goals_against / 10
        l10_goal_differential_per_game = l10_goal_differential / 10

        if is_home_team:
            home_win_percentage = home_wins / total_home_games
            home_loss_percentage = home_losses / total_home_games
            home_ot_loss_percentage = home_ot_losses / total_home_games
            home_goals_for_per_game = home_goals_for / total_home_games
            home_goals_against_per_game = home_goals_against / total_home_games
            home_goal_differential_per_game = home_goal_differential / total_home_games
        else:
            away_win_percentage = away_wins / total_away_games
            away_loss_percentage = away_losses / total_away_games
            away_ot_loss_percentage = away_ot_losses / total_away_games
            away_goals_for_per_game = away_goals_for / total_away_games
            away_goals_against_per_game = away_goals_against / total_away_games
            away_goal_differential_per_game = away_goal_differential / total_away_games


    if is_home_team:
        return (win_percentage, 
                loss_percentage, 
                ot_loss_percentage, 
                goals_for_per_game,
                goals_against_per_game,
                goal_differential_per_game,
                l10_win_percentage,
                l10_loss_percentage,
                l10_ot_losses,
                l10_goals_for_per_game,
                l10_goals_against_per_game,
                l10_goal_differential_per_game,
                home_win_percentage,
                home_loss_percentage,
                home_ot_loss_percentage,
                home_goals_for_per_game,
                home_goals_against_per_game,
                home_goal_differential_per_game)
    else:
        return (win_percentage, 
                loss_percentage, 
                ot_loss_percentage, 
                goals_for_per_game,
                goals_against_per_game,
                goal_differential_per_game,
                l10_win_percentage,
                l10_loss_percentage,
                l10_ot_losses,
                l10_goals_for_per_game,
                l10_goals_against_per_game,
                l10_goal_differential_per_game,
                away_win_percentage,
                away_loss_percentage,
                away_ot_loss_percentage,
                away_goals_for_per_game,
                away_goals_against_per_game,
                away_goal_differential_per_game)