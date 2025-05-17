from rest_framework.permissions import BasePermission
from django.conf import settings

class TokenBasedPermission(BasePermission):
    """
    superclass class to ensure that only that the token
    provided in the header matches the expected token value
    """
    token_header_name = None
    expected_token_value = None

    def has_permission(self, request, view):
        token = request.headers.get(self.token_header_name)
        return token == self.expected_token_value

class PredictGamesTodayPermission(TokenBasedPermission):
    """
    custom permission class to ensure that only the predict_games_script.py script can call the
    PredictGamesTodayView API endpoint
    """

    token_header_name = "PREDICT-GAMES-TODAY-TOKEN"
    expected_token_value = settings.PREDICT_GAMES_TODAY_ACCESS_TOKEN
    
class KeepActivePermission(BasePermission):
    """
    custom permission class to ensure that only the keep_servers_active.py script
    can call the KeepActiveView API endpoint
    """

    token_header_name = "KEEP-ACTIVE-TOKEN"
    expected_token_value = settings.KEEP_ACTIVE_ACCESS_TOKEN
    
class FetchGamesFromNHLAPIByDatePermission(BasePermission):
    """
    custom permission class to ensure that only the keep_servers_active.py script
    can call the KeepActiveView API endpoint
    """

    token_header_name = "FETCH-GAMES-TOKEN"
    expected_token_value = settings.FETCH_GAMES_TOKEN
