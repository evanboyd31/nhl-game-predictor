from django.db import models
from datetime import datetime

class Team(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3, unique=True)
    logo_url = models.URLField()

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class TeamData(models.Model):
  """
  Class to records the team's statistics for a provided day for model training
  """
  # associated to a team
  team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_data')

  # date for which this data was recorded
  data_capture_date = models.DateField()

  # simple team record states
  games_played = models.IntegerField(default=0)
  wins = models.IntegerField(default=0)
  losses = models.IntegerField(default=0)
  ot_losses = models.IntegerField(default=0)
  points = models.IntegerField(default=0)
  
  # team goal statistics
  goals_for = models.IntegerField(default=0)
  goals_against = models.IntegerField(default=0)
  goal_differential = models.IntegerField(default=0)

  # team record stats for the last 10 games
  l10_games_played = models.IntegerField(default=0)
  l10_wins = models.IntegerField(default=0)
  l10_losses = models.IntegerField(default=0)

  # win/loss streak stats
  streak_count = models.IntegerField(default=0)
  streak_code = models.CharField(max_length=1)

  class Meta:
      unique_together = ('team', 'data_capture_date')

  def __str__(self):
      return f"{self.team} Data ({self.data_capture_date})"
    
class Game(models.Model):
    """
    Class to represent a single NHL game
    """
    # stores game ID from the NHL API
    id = models.BigIntegerField(primary_key=True)

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
        current_date = datetime.now().date
        return current_date > self.game_date