import os
from django.core.management.base import BaseCommand
import sqlite3
import re
import pandas as pd

def coordinateCleaner(coordinate):
    lat = coordinate.split(",")[0].strip()
    lon = coordinate.split(",")[1].strip()
    lat = re.sub(r'\W+', ',', lat)
    lon = re.sub(r'\W+', ',', lon)
    lat = list(lat.split(","))
    lon = list(lon.split(","))
    for i in range(len(lat) - 1):
        lat[i] = int(lat[i])
    for i in range(len(lon) - 1):
        lon[i] = int(lon[i])
    return lat, lon

def toDecimal(coordinates):
    if len(coordinates) == 3:
        degrees, minutes, direction = coordinates
        seconds = 0
    else:
        degrees, minutes, seconds, direction = coordinates
    if direction == 'N' or direction == 'E':
        return degrees + minutes / 60.0 + seconds / 3600.0
    else:
        return -1 * (degrees + minutes / 60.0 + seconds / 3600.0)


def conferenceByYearBuilder(apps):
    ConferenceName = apps.get_model('conferences', 'ConferenceName')
    School = apps.get_model('conferences', 'School')
    Year = apps.get_model('conferences', 'Year')
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')

    for file in os.listdir("ConferenceByEraDB/"):
        if file.endswith(".db"):
            if file == "GeoCenters.db" or file == "ConferenceSummary.db":
                continue
            else:
                db_path = os.path.join(os.getcwd(), "ConferenceByEraDB", file)
                conn = sqlite3.connect(db_path)
                print("Processing " + file + "...")
                confName = file.split(".")[0]
                print("Conference Name: " + confName)
                ConferenceName.objects.create(name=confName)
                cursor = conn.cursor()
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                for table in tables:
                    table_name = table[0]
                    startYear = int(table_name.split("_")[1])
                    if table_name.split("_")[2] != "Present":
                        endYear = int(table_name.split("_")[2]) - 1
                    else:
                        endYear = 2024
                    for year in range(startYear, endYear + 1):
                        if not Year.objects.filter(year=year).exists():
                            Year.objects.create(year=year)
                        cursor.execute("SELECT * FROM " + table_name)
                        SportSeperatorFlag = False
                        fullMemberSchools = []
                        fballOnlySchools = []
                        bballOnlySchools = []
                        for row in cursor.fetchall():
                            schoolName = row[0]
                            City = row[1].split(",")[0].strip()
                            State = row[1].split(",")[1].strip()
                            if int(row[2]) == 1 and int(row[3]) == 1:
                                fullMemberSchools.append(schoolName)
                            elif int(row[2]) == 1:
                                SportSeperatorFlag = True
                                fballOnlySchools.append(schoolName)
                            elif int(row[3]) == 1:
                                SportSeperatorFlag = True
                                bballOnlySchools.append(schoolName)
                            Lat = row[4]
                            Lon = row[5]
                            if not School.objects.filter(name=schoolName).exists():
                               School.objects.create(name=schoolName, city=City, state=State, latitude=Lat, longitude=Lon)                            
                        if SportSeperatorFlag:
                            bBallSchools = fullMemberSchools + bballOnlySchools
                            fBallSchools = fullMemberSchools + fballOnlySchools
                            ConferenceByYear.objects.create(year=Year.objects.get(year=year), 
                                                           conference=ConferenceName.objects.get(name=confName), 
                                                           football=True, 
                                                           basketball=False,
                                                           schools=School.objects.filter(name__in=fBallSchools))
                            ConferenceByYear.objects.create(year=Year.objects.get(year=year),
                                                           conference=ConferenceName.objects.get(name=confName),
                                                           football=False,
                                                           basketball=True,
                                                           schools=School.objects.filter(name__in=bBallSchools))
                        else:
                            ConferenceByYear.objects.create(year=Year.objects.get(year=year),
                                                           conference=ConferenceName.objects.get(name=confName),
                                                           football=True,
                                                           basketball=True,
                                                           schools=School.objects.filter(name__in=fullMemberSchools))
                conn.close()



print("Starting...")

