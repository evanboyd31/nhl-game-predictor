# Generated by Django 5.1.2 on 2024-10-27 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0006_game_game_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='away_team_win',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='home_team_win',
            field=models.BooleanField(default=False),
        ),
    ]
