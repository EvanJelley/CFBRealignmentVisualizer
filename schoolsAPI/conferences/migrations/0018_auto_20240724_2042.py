# Generated by Django 5.0.7 on 2024-07-24 20:42

from django.db import migrations
from DatabaseCreation.DistanceCalculator.distanceCalc import buildHistoricConferences


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0017_conferencename_historical'),
    ]

    operations = [
        migrations.RunPython(buildHistoricConferences),
    ]
