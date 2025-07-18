"""
URL configuration for nhl_game_predictor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from games.views import FetchGamesFromNHLAPIByDateView, GameDetailView, GameListByDateView, GamePredictionByGameIdView, GamePredictionListByDateView, KeepActiveView, PredictGamesTodayView, UpdateCompletedGamesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/games/<int:id>/', GameDetailView.as_view(), name='game-detail'),
    path('api/games/date/', GameListByDateView.as_view(), name='game-list-by-date'),
    path('api/game-predictions/date/', GamePredictionListByDateView.as_view(), name='game-prediction-list-by-date'),
    path('api/game-predictions/by-game/<int:game_id>/', GamePredictionByGameIdView.as_view(), name='game-prediction-by-game-id'),
    path('api/predict-games-today/', PredictGamesTodayView.as_view(), name='predict-games-today'),
    path('api/keep-active/', KeepActiveView.as_view(), name='keep-active'),
    path('api/games/fetch-from-nhl-api/', FetchGamesFromNHLAPIByDateView.as_view(), name='fetch-games-from-nhl-api-by-date'),
    path('api/update-completed-games/', UpdateCompletedGamesView.as_view(), name='update-completed-games')
]
