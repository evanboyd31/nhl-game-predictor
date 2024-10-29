from django.db import models

class PredictionModel(models.Model):
    """
    class to represent a machine learning model used for making game predictions
    """
    name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=50, blank=True)

    def __str__(self):
        # eg: Random Forest (v.2.3)
        return f"{self.name} (Version: {self.version})"
