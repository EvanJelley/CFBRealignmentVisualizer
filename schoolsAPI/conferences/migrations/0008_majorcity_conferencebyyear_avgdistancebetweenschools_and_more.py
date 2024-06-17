# Generated by Django 5.0.6 on 2024-06-17 19:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0007_rename_conf_conferencebyyear_conference'),
    ]

    operations = [
        migrations.CreateModel(
            name='MajorCity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=2)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='avgDistanceBetweenSchools',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='avgDistanceFromCenter',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='basketball',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='centerLat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='centerLon',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='football',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='conferencebyyear',
            name='capital',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='conferences.majorcity'),
        ),
    ]
