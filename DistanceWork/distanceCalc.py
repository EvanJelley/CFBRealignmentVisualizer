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

    def getLatitude(self):
        return self.latitude
    
    def getLongitude(self):
        return self.longitude

    def __str__(self):
        return self.name
    
class conference(object):

    def __init__(self, name, year):
        self.name = name
        self.year = year
        self.schools = []
        self.geoCenter = None
    
    def addSchool(self, school):
        self.schools.append(school)
    
    def calculateGeoCenter(self):

        # Calculate initial center
        x = []
        y = []
        z = []
        schoolLocations = []
        for school in self.schools:
            latitude = math.radians(school.getLatitude())
            longitude = math.radians(school.getLongitude())
            schoolLocations.append((latitude, longitude))
            x.append(math.cos(latitude) * math.cos(longitude))
            y.append(math.cos(latitude) * math.sin(longitude))
            z.append(math.sin(latitude))
        x = sum(x) / len(x)
        y = sum(y) / len(y)
        z = sum(z) / len(z)
        centralLongitude = math.atan2(y, x)
        centralSquareRoot = math.sqrt(x * x + y * y)
        centralLatitude = math.atan2(z, centralSquareRoot)
        centralLatitude = math.degrees(centralLatitude)
        centralLongitude = math.degrees(centralLongitude)

        # Iterate to find better center
        currentPoint = (centralLatitude, centralLongitude)
        distance = distanceCalc(currentPoint, schoolLocations)

        # Test school locations
        for school in schoolLocations:
            testDistance = distanceCalc(school, schoolLocations)
            if testDistance < distance:
                currentPoint = school
                distance = testDistance
        
        testDistance = math.pi/2

        #### LEFT OFF HERE (step 5 of the method) ####


            
                   

        ##### Use Method A & B from this site: http://www.geomidpoint.com/calculation.html to calculate the center of the conference from #####

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

def convertDegreesMinutesSecondsToDecimal(coordinates):
    if len(coordinates) == 3:
        degrees, minutes, direction = coordinates
        seconds = 0
    else:
        degrees, minutes, seconds, direction = coordinates
    if direction == 'N' or direction == 'E':
        return degrees + minutes / 60.0 + seconds / 3600.0
    else:
        return -1 * (degrees + minutes / 60.0 + seconds / 3600.0)

def convertDecimalToDegreesMinutesSeconds (decimal):
    degrees = int(decimal)
    minutes = int((decimal - degrees) * 60)
    seconds = int((decimal - degrees - minutes / 60.0) * 3600)
    return degrees, minutes, seconds

def pointToPointCalc(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the earth's surface
    :params lat1, lat2, lon1, lon2: latitude and longitude of the two points (should be in radians)
    :return: distance between the two points (in radians)
    """
    R = 6371.009 # radius of the earth in kilometers
    distance = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)) * R
    return distance

def distanceCalc(main, points):
    """
    Calculate the distance between a point and a set of points
    :params main: a tuple with the latitude and longitude of the main point
    :params points: a list of tuples with the latitude and longitude of the set of points
    :return: the total distance between the main point and the set of points
    """
    distance = 0
    for point in points:
        distance += pointToPointCalc(main[0], main[1], point[0], point[1])
    return distance

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
                print(name)
                latitude = convertDegreesMinutesSecondsToDecimal(latitude)
                longitude = convertDegreesMinutesSecondsToDecimal(longitude)
                schoolObj = school(name, location, football, basketball, latitude, longitude)
                confEra.addSchool(schoolObj)
            conn.close()

            # Add the conference to the list of conferences
            eras.append(confEra)
    return eras

con = "SEC"
eras = readInSchools(con)
for era in eras:
    print(era.name)
    print(era.calculateGeoCenter())



