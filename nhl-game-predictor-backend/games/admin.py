from django.contrib import admin
from .models import Franchise, Season, Team, TeamData, Game, GamePrediction

@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    """
    display of the Franchise model class on the admin page
    """
    list_display = ('franchise_id',)
    search_fields = ('franchise_id',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    display of the Team model class on the admin page
    """
    list_display = ('name', 'abbreviation')
    search_fields = ('name', 'abbreviation')

# TeamData Admin configuration
@admin.register(TeamData)
class TeamDataAdmin(admin.ModelAdmin):
    """
    display of the TeamData model class on the admin page
    """
    list_display = ('team', 'data_capture_date')
    list_filter = ('team', 'data_capture_date')
    search_fields = ('team__name', 'team__abbreviation')
    date_hierarchy = 'data_capture_date'

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """
    display of the Season model class on the admin page
    """
    list_display = ('id', 'regular_season_start', 'regular_season_end')
    list_filter = ('id',)
    search_fields = ('id',)

# Game Admin configuration
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    display of the Game model class on the admin page
    """
    list_display = ('home_team', 'away_team', 'game_date')
    list_filter = ('game_date', 'home_team', 'away_team')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'game_date'

    def is_completed(self, obj : Game):
        """
        displays the is_completed() return result of a Game
        as a field on the admin page
        """
        return obj.is_completed()
    
    is_completed.boolean = True
    is_completed.short_description = 'Completed'


@admin.register(GamePrediction)
class GamePredictionAdmin(admin.ModelAdmin):
    """
    display of the GamePrediction model class on the admin page
    """
    list_display = ('game', 'predicted_home_team_win', 'confidence_score', 'display_top_features')
    list_filter = ('predicted_home_team_win',)
    search_fields = ('game__home_team__name', 'game__away_team__name')

    def display_top_features(self, obj :GamePrediction):
        """
        Display top features and their importance scores. A maximum of 5 features and their 
        respective importances are stored in a GamePrediction model class
        """
        if obj.top_features:
            # sort valid entries by the importance values for displaying (if they exist)
            top_features = sorted(
                ((k, v) for k, v in obj.top_features.items() if isinstance(v, list) and len(v) == 2),
                key=lambda x: x[1][1],
                reverse=True
            )[:5]
            return ", ".join([f"{k}: {v[0]} (Importance: {v[1]:.2f})" for k, v in top_features])
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
