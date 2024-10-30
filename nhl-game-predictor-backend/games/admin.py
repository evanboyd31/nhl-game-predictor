from django.contrib import admin
from .models import Franchise, Team, TeamData, Game, GamePrediction

# Register your models here.

@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ('franchise_id',)
    search_fields = ('franchise_id',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')
    search_fields = ('name', 'abbreviation')

# TeamData Admin configuration
@admin.register(TeamData)
class TeamDataAdmin(admin.ModelAdmin):
    list_display = ('team', 'data_capture_date')
    list_filter = ('team', 'data_capture_date')
    search_fields = ('team__name', 'team__abbreviation')
    date_hierarchy = 'data_capture_date'


# Game Admin configuration
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'game_date')
    list_filter = ('game_date', 'home_team', 'away_team')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'game_date'

    def is_completed(self, obj):
        return obj.is_completed()
    is_completed.boolean = True
    is_completed.short_description = 'Completed'


@admin.register(GamePrediction)
class GamePredictionAdmin(admin.ModelAdmin):
    list_display = ('game', 'predicted_home_team_win', 'confidence_score', 'display_top_features')
    list_filter = ('predicted_home_team_win',)
    search_fields = ('game__home_team__name', 'game__away_team__name')

    def display_top_features(self, obj):
        """Display top 5 features and their importance scores."""
        if obj.top_features:
            top_features = sorted(obj.top_features.items(), key=lambda x: x[1], reverse=True)[:5]
            return ", ".join([f"{k}: {v:.2f}" for k, v in top_features])
        return "No features"

    display_top_features.short_description = "Top Features (5)"

    readonly_fields = ('predicted_home_team_win', 'confidence_score', 'game', 'display_top_features')

    fieldsets = (
        (None, {
            'fields': ('game', 'predicted_home_team_win', 'confidence_score')
        }),
        ('Prediction Details', {
            'fields': ('display_top_features',),
        }),
    )