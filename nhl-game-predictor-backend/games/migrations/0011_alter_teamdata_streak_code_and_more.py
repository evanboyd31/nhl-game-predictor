# Generated by Django 5.1.2 on 2024-10-27 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_alter_teamdata_streak_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamdata',
            name='streak_code',
            field=models.IntegerField(choices=[(0, 'Win'), (1, 'LOSS'), (2, 'Overtime'), (3, 'First Game')], default=3),
        ),
        migrations.AlterField(
            model_name='teamdata',
            name='streak_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
