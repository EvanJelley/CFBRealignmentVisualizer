# Generated by Django 5.0.7 on 2024-07-20 23:59

from django.db import migrations
from DatabaseCreation.DistanceCalculator.distanceCalc import AACBuilder


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0013_conferencename_colors'),
    ]

    operations = [
        migrations.RunPython(AACBuilder)
    ]
