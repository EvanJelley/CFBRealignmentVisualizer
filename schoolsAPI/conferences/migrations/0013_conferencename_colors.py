# Generated by Django 5.0.6 on 2024-07-12 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0012_school_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferencename',
            name='colors',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
