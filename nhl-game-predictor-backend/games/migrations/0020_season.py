# Generated by Django 5.1.2 on 2025-06-19 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0019_alter_game_away_team_data_alter_game_home_team_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('regularSeasonStart', models.DateField()),
                ('regularSeasonEnd', models.DateField()),
                ('season_json', models.JSONField(default=dict)),
            ],
        ),
    ]
