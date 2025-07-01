from django.db import models
from django.utils import timezone


class Franchise(models.Model):
    """
    a model to represent a franchise, which can have multiple team representations
    due to relocations or rebranding
    """
    franchise_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"Franchise ID: {self.franchise_id}"


class Team(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE, related_name='teams', null=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3, unique=True)
    logo_url = models.URLField()

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class TeamData(models.Model):
    """
    class to record a team's statistics for a provided day for model training
    """
    id = models.BigAutoField(primary_key=True)
    
    # associated to a team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_data')
    # date that the data captures for
    team_data_json = models.JSONField(default=dict)

    data_capture_date = models.DateField()

    WIN = 0
    LOSS = 1
    OVERTIME = 2
    FIRST_GAME = 3

    class Meta:
        unique_together = ('team', 'data_capture_date')

    def __str__(self):
        return f"{self.team} Data ({self.data_capture_date})"
    
class Season(models.Model):
    """
    class to represent an NHL season
    """
    id = models.BigIntegerField(primary_key=True)

    # the endpoint https://api-web.nhle.com/v1/standings/<date>/ is only valid for dates between regularSeasonStart and regularSeasonEnd
    regular_season_start = models.DateField()
    regular_season_end = models.DateField()

    season_json = models.JSONField(default=dict)

class Game(models.Model):
    """
    class to represent a single NHL game
    """
    # stores game ID from the NHL API
    id = models.BigIntegerField(primary_key=True)

    game_json = models.JSONField(default=dict)

    # home and away teams
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    winning_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='won_games', null=True)

    # date of game
    game_date = models.DateField()

    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, related_name='games')

    # game type
    PRESEASON = 1
    REGULAR_SEASON = 2
    PLAYOFFS = 3

    # relationships to TeamData for pre-game analysis
    home_team_data = models.ForeignKey(TeamData, on_delete=models.SET_NULL, related_name='home_game_data', null=True)
    away_team_data = models.ForeignKey(TeamData, on_delete=models.SET_NULL, related_name='away_game_data', null=True)

    class Meta:
        unique_together = ('home_team', 'away_team', 'game_date')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.game_date.strftime('%Y-%m-%d %H:%M')}"
    
    def is_completed(self):
        """
        a game is defined as completed if the date of the game is in the past
        """
        current_date = timezone.localdate()
        return current_date > self.game_date
    

class GamePrediction(models.Model):
    """
    class to represent a Game Prediction/Choice of the machine learning model.
    used for caching purposes once the machine learning model has made predictions
    for all games on a provided day.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='predictions', null=True)
    model = models.ForeignKey('predictor.PredictionModel', on_delete=models.CASCADE, related_name='predictions', null=True)
    
    predicted_home_team_win = models.BooleanField(default=False)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    top_features = models.JSONField(null=True, blank=True)

    class Meta:
        # ensure that each PredictionModel only predicts a game once
        unique_together = ('game', 'model') 

    def __str__(self):
        return f"Prediction by {self.model} for Game {self.game} - Predicted Winner: {self.game.home_team if self.predicted_home_team_win else self.game.away_team}"