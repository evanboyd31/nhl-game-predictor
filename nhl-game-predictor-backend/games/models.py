from django.db import models
from datetime import datetime


class Franchise(models.Model):
    """
    A model to represent a franchise, which can have multiple team representations
    due to relocations or rebranding.
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
    Class to record a team's statistics for a provided day for model training
    """

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
    
class Game(models.Model):
    """
    Class to represent a single NHL game
    """

    game_json = models.JSONField(default=dict)
    # stores game ID from the NHL API
    id = models.BigIntegerField(primary_key=True)
    season = models.BigIntegerField(null=True)

    # home and away teams
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    winning_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='won_games', null=True)

    # date of game
    game_date = models.DateField()

    # game type
    PRESEASON = 1
    REGULAR_SEASON = 2
    PLAYOFFS = 3
    GAME_TYPE_CHOICES = [
        (PRESEASON, "Preseason"),
        (REGULAR_SEASON, "Regular Season"),
        (PLAYOFFS, "Playoffs")
    ]

    game_type = models.IntegerField(choices=GAME_TYPE_CHOICES, null=True)

    # goals
    home_team_goals = models.IntegerField(default=0)
    away_team_goals = models.IntegerField(default=0)

    # shootout and overtime finishes
    is_overtime = models.BooleanField(default=False)
    is_shootout = models.BooleanField(default=False)

    # relationships to TeamData for pre-game analysis
    home_team_data = models.ForeignKey(TeamData, on_delete=models.CASCADE, related_name='home_game_data', null=True)
    away_team_data = models.ForeignKey(TeamData, on_delete=models.CASCADE, related_name='away_game_data', null=True)

    class Meta:
        unique_together = ('home_team', 'away_team', 'game_date')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.game_date.strftime('%Y-%m-%d %H:%M')}"
    
    def is_completed(self):
        current_date = datetime.now().date()
        return current_date > self.game_date