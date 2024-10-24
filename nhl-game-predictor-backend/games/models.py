from django.db import models

class Team(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    city = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3, unique=True)
    logo_url = models.URLField()

    def __str__(self):
        return f"{self.city} ({self.abbreviation})"

