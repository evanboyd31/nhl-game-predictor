from rest_framework import serializers
from .models import Franchise, Team, TeamData, Game, GamePrediction

class FranchiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise
        fields = ['franchise_id']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'franchise', 'name', 'abbreviation', 'logo_url']


class TeamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamData
        fields = ['id', 'team', 'team_data_json', 'data_capture_date']


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id',
            'game_json',
            'home_team',
            'away_team',
            'winning_team',
            'game_date',
            'home_team_data',
            'away_team_data'
        ]


class GamePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePrediction
        fields = [
            'id',
            'game',
            'model',
            'predicted_home_team_win',
            'confidence_score',
            'top_features'
        ]