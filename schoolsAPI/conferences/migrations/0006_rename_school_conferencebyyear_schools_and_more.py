# Generated by Django 5.0.6 on 2024-06-14 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0005_conferencename_conferencecomplete_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conferencebyyear',
            old_name='school',
            new_name='schools',
        ),
        migrations.DeleteModel(
            name='ConferenceComplete',
        ),
    ]
