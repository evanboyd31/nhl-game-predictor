from django.db import migrations

def assign_season_to_preseason_playoff_games(apps, schema_editor):
  Game = apps.get_model('games', 'Game')
  Season = apps.get_model('games', 'Season')

  games_to_update = []

  PRESEASON = 1
  PLAYOFFS = 3

  preseason_playoff_games = Game.objects.filter(game_json__gameType__in=[PRESEASON, PLAYOFFS])

  for game in preseason_playoff_games:
     game_season_id = game.game_json.get("season")
     game.season = Season.objects.filter(season_id=game_season_id).first()
     
     if game.season is not None:
        games_to_update.append(game)

  Game.objects.bulk_update(games_to_update, fields=['season'])

def unassign_season_to_preseason_playoff_games(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('games', '0025_load_preseason_playoff_games'),
    ]

    operations = [
        migrations.RunPython(assign_season_to_preseason_playoff_games, reverse_code=unassign_season_to_preseason_playoff_games)
    ]