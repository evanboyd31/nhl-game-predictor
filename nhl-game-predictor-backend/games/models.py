from django.db import models

class Team(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    city = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3, unique=True)
    logo_url = models.URLField()

    def __str__(self):
        return f"{self.city} ({self.abbreviation})"

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
  streak_code = models.CharField(max_length=1)  # e.g., W for Win, L for Loss

  class Meta:
      unique_together = ('team', 'data_capture_date')  # Prevent duplicates for the same team on the same day

  def __str__(self):
      return f"{self.team} Data ({self.data_capture_date})"