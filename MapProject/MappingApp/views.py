from django.shortcuts import render
import sqlite3
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'MapProject.settings'
from django.conf import settings
from django.http import JsonResponse


def coordinates(request, conference, year):
    db_path = settings.DATA_DIR / f'{conference}.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    



