from rest_framework.permissions import BasePermission
from django.conf import settings

class PredictGamesTodayPermission(BasePermission):
    """
    custom permission class to ensure that only the predict_games_script.py script can call the
    PredictGamesTodayView API endpoint
    """
    def has_permission(self, request, view):
        token = request.headers.get('PREDICT-GAMES-TODAY-TOKEN')
        return token == settings.PREDICT_GAMES_TODAY_ACCESS_TOKEN
