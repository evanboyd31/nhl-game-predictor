# Generated by Django 5.1.2 on 2024-10-27 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_alter_game_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_type',
            field=models.IntegerField(choices=[(1, 'Preseason'), (2, 'Regular Season'), (3, 'Playoffs')], null=True),
        ),
    ]