from django.db import migrations

def add_utah_mammoth(apps, schema_editor):
    Team = apps.get_model('games', 'Team')
    Franchise = apps.get_model('games', 'Franchise')

    utah_mammoth = Team(name="Utah Mammoth",
                        abbreviation="UTA",
                        franchise=Franchise.objects.get(id=40))
    
    utah_mammoth.save()

def remove_utah_mammoth(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('games', '0027_alter_team_abbreviation'),
    ]

    operations = [
        migrations.RunPython(add_utah_mammoth, reverse_code=remove_utah_mammoth)
    ]