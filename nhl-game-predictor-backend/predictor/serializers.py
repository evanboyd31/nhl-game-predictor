from rest_framework import serializers
from .models import PredictionModel

class PredictionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionModel
        fields = ['id', 'name', 'version']