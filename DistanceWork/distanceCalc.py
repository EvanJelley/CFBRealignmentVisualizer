import math
import sqlite3
import os
import re

class school(object):

    def __init__(self, name, location, football, basketball, latitude, longitude):
        self.name = name
        self.location = location
        self.football = football
        self.basketball = basketball
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return self.name
    
class conference(object):

    def __init__(self, name, year):
        self.name = name
        self.year = year
        self.schools = []
    
    def addSchool(self, school):
        self.schools.append(school)

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

def convertDegreesMinutesSecondsToDecimal(degrees, minutes, seconds, direction):
    if direction == 'N' or direction == 'E':
        return degrees + minutes / 60.0 + seconds / 3600.0
    else:
        return -1 * (degrees + minutes / 60.0 + seconds / 3600.0)

lat = (42, 16, 53,"N")
lon = (83, 44, 54, "W")

latDecimal = convertDegreesMinutesSecondsToDecimal(lat[0], lat[1], lat[2], lat[3])
lonDecimal = convertDegreesMinutesSecondsToDecimal(lon[0], lon[1], lon[2], lon[3])

def convertDecimalToDegreesMinutesSeconds (decimal):
    degrees = int(decimal)
    minutes = int((decimal - degrees) * 60)
    seconds = int((decimal - degrees - minutes / 60.0) * 3600)
    return degrees, minutes, seconds

def great_circle_distance (latitudeA, longitudeA, latitudeB, longitudeB):
    # Degrees to radians
    phi1    = math.radians(latitudeA)
    lambda1 = math.radians(longitudeA)

    phi2    = math.radians(latitudeB)
    lambda2 = math.radians(longitudeB)

    delta_lambda = math.fabs(lambda2 - lambda1)

    central_angle = \
        math.atan2 \
        (
            # Numerator
            math.sqrt
            (
                # First
                math.pow
                (
                    math.cos(phi2) * math.sin(delta_lambda)
                    , 2.0
                )
                +
                # Second
                math.pow
                (
                    math.cos(phi1) * math.sin(phi2) -
                    math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
                    , 2.0
                )
            ),
            # Denominator
            (
                math.sin (phi1) * math.sin(phi2) +
                math.cos (phi1) * math.cos(phi2) * math.cos(delta_lambda)
            )
        )

    R = 3958.7564 # miles
    return R * central_angle





def readInSchools(conf):
    eras = []

    # Find all the files in the directory
    for file in os.listdir("ConferenceByEra/" + conf):
        if file.endswith(".db"):
            print("Processing " + file + "...")

            # Make conference object
            confEra = conference(conf  + file[:-3], int(file[:-3]))

            # Connect to the database
            conn = sqlite3.connect("ConferenceByEra/" + conf + "/" + file)
            cursor = conn.cursor()

            # Get all the schools
            cursor.execute("SELECT * FROM Conference")
            rows = cursor.fetchall()

            # Add the schools to the conference object
            for row in rows:
                name = row[0]
                location = row[1]
                if row[2] == "1":
                    football = True
                else:
                    football = False
                if row[3] == "1":
                    basketball = True
                else:
                    basketball = False
                coordinates = row[4]
                latitude, longitude = coordinateCleaner(coordinates)
                schoolObj = school(name, location, football, basketball, latitude, longitude)
                confEra.addSchool(schoolObj)
            conn.close()

            # Add the conference to the list of conferences
            eras.append(confEra)
    return eras

con = "BigTen"
eras = readInSchools(con)
for era in eras:
    print(era.name)
    for school in era.schools:
        print(school.name)
        print(school.location)
        print(school.football)
        print(school.basketball)
        print(school.latitude)
        print(school.longitude)
        print("\n")




