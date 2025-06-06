from django.contrib import admin
from .models import PredictionModel

@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    """
    display of the GamePrediction model class on the admin page
    """
    list_display = ('name', 'version')
    search_fields = ('name', 'version')
