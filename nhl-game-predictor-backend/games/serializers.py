from rest_framework import serializers
from .models import Franchise, Team, TeamData, Game, GamePrediction

from rest_framework import serializers
from .models import Game, Team, GamePrediction
from predictor.serializers import PredictionModelSerializer

class FranchiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    franchise = FranchiseSerializer(serializers.ModelSerializer)
    class Meta:
        model = Team
        fields = '__all__'

class TeamDataSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TeamData
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer() 
    away_team = TeamSerializer()

    class Meta:
        model = Game
        fields = '__all__'


class GamePredictionSerializer(serializers.ModelSerializer):
    game = GameSerializer()
    model = PredictionModelSerializer()

    class Meta:
        model = GamePrediction
        fields = '__all__'
