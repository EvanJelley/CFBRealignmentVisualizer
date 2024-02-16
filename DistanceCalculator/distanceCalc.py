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
            # print(school.getLatitude(), school.getLongitude())
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

        # Iterate to find better center
        currentPoint = (centralLatitude, centralLongitude)
        totDistance = distanceCalc(currentPoint, schoolLocations)

        # Test school locations
        for school in schoolLocations:
            schoolDistance = distanceCalc(school, schoolLocations)
            # print("Current distance: " + str(distance))
            # print("Test distance: " + str(testDistance))
            if schoolDistance < totDistance:
                currentPoint = school
                totDistance = schoolDistance
                # print("New center: " + str(currentPoint) + " with distance: " + str(distance) + "\n")
        
        testDistance = 10018 / 6371.0
        while testDistance > 0.000000002:
            # print(currentPoint[0], currentPoint[1])
            testPoints = generate_test_points(currentPoint[0], currentPoint[1], testDistance)
            newPointFlag = False
            for point in testPoints:
                testPointDistance = distanceCalc(point, schoolLocations)
                if testPointDistance < totDistance:
                    currentPoint = point
                    totDistance = testPointDistance
                    newPointFlag = True
                    # print("New center from Narrowing method: " + str(currentPoint) + " with distance: " + str(distance) + "\n")
            if not newPointFlag:
                testDistance = testDistance / 2
        currentPoint = (math.degrees(currentPoint[0]), math.degrees(currentPoint[1]))
        return currentPoint


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
    if abs(lat1 - lat2) < .000000000000001 and abs(lon1 - lon2) < .000000000000001:
        return 0
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

def generate_test_points(lat, lon, distance):
    # Constants
    R = 6371.0  # Earth's radius in kilometers
    bearings = [0, 45, 90, 135, 180, 225, 270, 315]  # Bearings in degrees
    
    test_points = []
    for bearing in bearings:
        # Convert bearing to radians
        brng_rad = math.radians(bearing)
        
        # Calculate the new latitude
        new_lat = math.asin(math.sin(lat) * math.cos(distance / R) +
                                math.cos(lat) * math.sin(distance / R) * math.cos(brng_rad))
        
        # Calculate the new longitude
        new_lon = lon + math.atan2(math.sin(brng_rad) * math.sin(distance / R) * math.cos(lat),
                                           math.cos(distance / R) - math.sin(lat) * math.sin(new_lat))
                
        # Append new point to the list
        test_points.append((new_lat, new_lon))
    
    return test_points

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

con = "BigTen"
eras = readInSchools(con)
for era in eras:
    print(era.name)
    print(era.calculateGeoCenter())

# lat = 33.7550
# lon = -84.3900
# lat = 0.5795656669455838
# lon = -1.5277691125964252
# distance = math.radians(10018)

# testPoints = generate_test_points(lat, lon, distance)
# for point in testPoints:
#     print(math.degrees(point[0]), math.degrees(point[1]))

