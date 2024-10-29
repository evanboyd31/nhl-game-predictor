from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Game
from .serializers import GameSerializer
from django.utils import timezone

class GameListByDateView(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        date_str = self.request.query_params.get('date')
        # if no date, assume the caller wants all games
        if not date_str:
            return Game.objects.all()

        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            return Game.objects.filter(game_date=date)
        except ValueError:
            raise NotFound("Invalid date format. Use 'YYYY-MM-DD'.")
