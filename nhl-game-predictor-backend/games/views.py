from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from .models import Game, GamePrediction
from .serializers import GameSerializer, GamePredictionSerializer
from django.utils import timezone
from rest_framework.permissions import AllowAny
from predictor.ml_models.predict_model import predict_games
from .permissions import PredictGamesTodayPermission

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

    def get_date(self):
        date_str = self.request.query_params.get('date')
        # caller must provide a date to find game predictions
        if not date_str:
            raise ParseError("A date must be provided in the format 'YYYY-MM-DD'.")
        # ensure date is in correct format
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            return date
        except ValueError:
            raise ParseError("Invalid date format. Use 'YYYY-MM-DD'.")

    def get_predictions(self):
        """
        function to get the game predictions on the specified date
        """
        date = self.get_date()
        predictions = GamePrediction.objects.filter(game__game_date=date)
        return predictions

    def get_games(self):
        """
        function to get the games on the specified date. useful for checking
        if predictions have been made yet, or if there are any games scheduled today
        """
        date = self.get_date()
        games = Game.objects.filter(game_date=date)
        return games

    def get(self, request, *args, **kwargs):
        # get GamePredictions and Games for specified date
        predictions = self.get_predictions()
        games = self.get_games()

        # there are no games scheduled on the date, so raise an error saying so
        if games.count() == 0:
            raise NotFound("There are no NHL games scheduled today.")

        # there are games scheduled today, but the corresponding GamePredictions have not yet been made
        if games.count() != predictions.count():
            raise NotFound("Our predictions have not yet been created for the NHL games scheduled today. Check back soon!")

        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
class PredictGamesTodayView(APIView):
    """
    API endpoint that is called every night at midnight to generate today's game predicitions
    since you can't make chron jobs on render unless you pay :(
    """

    permission_classes = [PredictGamesTodayPermission]
    
    def get(self, request):
        today = timezone.localdate()
        games_today = Game.objects.filter(game_date=today)

        # check to see if we've already made predictions for today
        # if we have, then we return them all
        if all(GamePrediction.objects.filter(game=game).exists() for game in games_today):
            todays_predictions = GamePrediction.objects.filter(game__in=games_today)
            serializer = GamePredictionSerializer(todays_predictions, many=True)
            return Response(serializer.data)
        
        # otherwise, predictions haven't been made yet for the games today, 
        todays_predictions = predict_games(games_today)
        serializer = GamePredictionSerializer(todays_predictions, many=True)
        return Response(serializer.data)
    
class KeepActiveView(APIView):
    """
    called every 15 minutes so the free render service does not spin down
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "Server is active"}, status=200)