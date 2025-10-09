from django.db import models
from games.models import Season

class PredictionModel(models.Model):
    """
    class to represent a machine learning model used for making game predictions
    """
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    trained_seasons = models.ManyToManyField(Season, related_name="prediction_models")
    feature_importances = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = ("name", "version")

    def __str__(self):
        # eg: Random Forest (v.2.3)
        return f"{self.name} (Version: {self.version})"
