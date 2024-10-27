from django.db import models

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
  games_played = models.IntegerField()
  wins = models.IntegerField()
  losses = models.IntegerField()
  ot_losses = models.IntegerField()
  points = models.IntegerField()
  
  # team goal statistics
  goals_for = models.IntegerField()
  goals_against = models.IntegerField()
  goal_differential = models.IntegerField()

  # team record stats for the last 10 games
  l10_games_played = models.IntegerField()
  l10_wins = models.IntegerField()
  l10_losses = models.IntegerField()

  # win/loss streak stats
  streak_count = models.IntegerField()
  streak_code = models.CharField(max_length=1)

  class Meta:
      unique_together = ('team', 'data_capture_date')

  def __str__(self):
      return f"{self.team} Data ({self.data_capture_date})"
    
class Game(models.Model):
    """
    Class to represent a single NHL game
    """
    # home and away teams
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    
    # date of game
    game_date = models.DateField()
    
    # Game status (e.g., scheduled, completed)
    status = models.CharField(max_length=20)  # e.g., "Scheduled", "Completed", "Postponed"

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