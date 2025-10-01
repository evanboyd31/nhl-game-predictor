from rest_framework import serializers
from .models import PredictionModel

class PredictionModelSerializer(serializers.ModelSerializer):
    """
    serializes all fields of a PredictionModel model instance into JSON
    """
    
    class Meta:
        model = PredictionModel
        fields = '__all__'