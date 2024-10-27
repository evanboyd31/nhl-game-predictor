from django.contrib import admin
from .models import Team, TeamData, Game

# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')
    search_fields = ('name', 'abbreviation')

# TeamData Admin configuration
@admin.register(TeamData)
class TeamDataAdmin(admin.ModelAdmin):
    list_display = ('team', 'data_capture_date', 'games_played', 'wins', 'losses', 'points')
    list_filter = ('team', 'data_capture_date')
    search_fields = ('team__name', 'team__abbreviation')
    date_hierarchy = 'data_capture_date'


# Game Admin configuration
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'game_date', 'game_type', 'home_team_goals', 'away_team_goals', 'is_completed')
    list_filter = ('game_type', 'game_date', 'home_team', 'away_team')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'game_date'

    def is_completed(self, obj):
        return obj.is_completed()
    is_completed.boolean = True
    is_completed.short_description = 'Completed'
