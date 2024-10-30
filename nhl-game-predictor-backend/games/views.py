from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Game, GamePrediction
from .serializers import GameSerializer, GamePredictionSerializer
from django.utils import timezone

class GameDetailView(generics.RetrieveAPIView):
    """
    Retrieve a Game by its ID.
    """
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'id'

class GameListByDateView(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        date_str = self.request.query_params.get('date')
        # caller must provide a date to find games
        if not date_str:
            raise NotFound("A date must be provided in the format 'YYYY-MM-DD'.")

        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            return Game.objects.filter(game_date=date)
        except ValueError:
            raise NotFound("Invalid date format. Use 'YYYY-MM-DD'.")
        

class GamePredictionByGameIdView(APIView):
    """
    Get a game prediction for a provided Game's id. When only 1 PredictionModel is in use,
    any Game associated to a GamePrediction will be associated to exactly 1 GamePrediction
    """
    def get(self, request, game_id, *args, **kwargs):
        try:
            prediction = GamePrediction.objects.get(game__id=game_id)
        except GamePrediction.DoesNotExist:
            raise NotFound(f"Prediction for the specified game ID {game_id} does not exist.")
        
        serializer = GamePredictionSerializer(prediction)
        return Response(serializer.data)

class GamePredictionListByDateView(generics.ListAPIView):
    serializer_class = GamePredictionSerializer

    def get_queryset(self):

        date_str = self.request.query_params.get('date')
        
        # caller must provide a date to find game predictions
        if not date_str:
            raise NotFound("A date must be provided in the format 'YYYY-MM-DD'.")

        # ensure date is in correct format
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            return GamePrediction.objects.filter(game__game_date=date)
        except ValueError:
            raise NotFound("Invalid date format. Use 'YYYY-MM-DD'.")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)