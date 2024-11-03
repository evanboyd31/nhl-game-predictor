from rest_framework import serializers
from .models import Franchise, Team, TeamData, Game, GamePrediction

from rest_framework import serializers
from .models import Game, Team, GamePrediction
from predictor.serializers import PredictionModelSerializer
from .utils import cleaned_feature_names_dictionary

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
    
    top_features_descriptions = serializers.SerializerMethodField()

    def get_top_features_descriptions(self, obj):
        """
        Maps the original feature name to its corresponding descriptive feature.
        """
        top_features = obj.top_features or {}
        game = obj.game

        descriptions = {}
        for feature_key, feature_value in top_features.items():
            if feature_key in cleaned_feature_names_dictionary:
                description = cleaned_feature_names_dictionary[feature_key](game)
                descriptions[description] = feature_value
        return descriptions

    class Meta:
        model = GamePrediction
        fields = [
            'id',
            'game', 
            'model', 
            'predicted_home_team_win', 
            'confidence_score', 
            'top_features', 
            'top_features_descriptions'  # Explicitly add the additional field here
        ]


