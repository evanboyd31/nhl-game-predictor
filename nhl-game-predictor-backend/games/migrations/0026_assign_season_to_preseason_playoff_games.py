from django.db import migrations

def assign_season_to_preseason_playoff_games(apps, schema_editor):
  Game = apps.get_model('games', 'Game')
  Season = apps.get_model('games', 'Season')

  PRESEASON = 1
  PLAYOFFS = 3

  season_map = {
      s.id: s
      for s in Season.objects.all()
  }

  games = Game.objects.filter(game_json__gameType__in=[PRESEASON, PLAYOFFS])

  games_to_update = []

  for game in games:
    game_season_id = game.game_json.get("season")
    season = season_map.get(game_season_id)
    if season:
      game.season = season
      games_to_update.append(game)

  Game.objects.bulk_update(games_to_update, fields=["season"])

def unassign_season_to_preseason_playoff_games(apps, schema_editor):
  Game = apps.get_model('games', 'Game')

  PRESEASON = 1
  PLAYOFFS = 3

  games = Game.objects.filter(game_json__gameType__in=[PRESEASON, PLAYOFFS], season__isnull=False)

  for game in games:
    game.season = None

  Game.objects.bulk_update(games, fields=["season"])

class Migration(migrations.Migration):

    dependencies = [
        ('games', '0025_load_preseason_playoff_games'),
    ]

    operations = [
        migrations.RunPython(assign_season_to_preseason_playoff_games, reverse_code=unassign_season_to_preseason_playoff_games)
    ]
