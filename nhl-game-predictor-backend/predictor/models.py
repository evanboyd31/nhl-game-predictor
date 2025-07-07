from django.db import models

class PredictionModel(models.Model):
    """
    class to represent a machine learning model used for making game predictions
    """
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)

    class Meta:
        unique_together = ("name", "version")

    def __str__(self):
        # eg: Random Forest (v.2.3)
        return f"{self.name} (Version: {self.version})"
