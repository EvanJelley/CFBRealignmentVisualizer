import math
import sqlite3
import os
import re
import requests
import pandas as pd
import io
from bs4 import BeautifulSoup

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

    def __init__(self, name, startYear, endYear):
        self.name = name
        self.startYear = startYear
        self.endYear = endYear
        self.schools = []
        self.bBallSchools = None
        self.fBallSchools = None
        self.geoCenter = None
        self.bBallGeoCenter = None
        self.fBallGeoCenter = None
        self.capital = None
        self.bBallCapital = None
        self.fBallCapital = None
        self.avgDistanceFromGeoCenter = None
        self.bBallAvgDistanceFromGeoCenter = None
        self.fBallAvgDistanceFromGeoCenter = None
        self.avgDistanceFromOtherSchools = None
        self.bBallAvgDistanceFromOtherSchools = None
        self.fBallAvgDistanceFromOtherSchools = None
    
    def addSchool(self, school):
        self.schools.append(school)

    def findSportSpecificSchools(self):
        bBallSchools = []
        fBallSchools = []
        for school in self.schools:
            if school.football:
                    fBallSchools.append(school)
            if school.basketball:
                bBallSchools.append(school)
            self.bBallSchools = bBallSchools
            self.fBallSchools = fBallSchools

    def findGeoCenter(self):
        if self.bBallSchools == self.fBallSchools:
            schoolLocations = []
            for s in self.schools:
                latitude = s.getLatitude()
                longitude = s.getLongitude()
                schoolLocations.append((latitude, longitude))
            self.geoCenter = calculateGeoCenter(schoolLocations)
        else:
            bBallLocations = []
            fBallLocations = []
            for s in self.bBallSchools:
                latitude = s.getLatitude()
                longitude = s.getLongitude()
                bBallLocations.append((latitude, longitude))
            for s in self.fBallSchools:
                latitude = s.getLatitude()
                longitude = s.getLongitude()
                fBallLocations.append((latitude, longitude))
            self.bBallGeoCenter = calculateGeoCenter(bBallLocations)
            self.fBallGeoCenter = calculateGeoCenter(fBallLocations)

    def findCapital(self, cities):
        if self.bBallSchools == self.fBallSchools:
            capital = None
            currentDistance = None
            for city in cities:
                cityLat = math.radians(city.getLatitude())
                cityLon = math.radians(city.getLongitude())
                if capital == None:
                    capital = city
                    distance = pointToPointCalc(math.radians(self.geoCenter[0]), math.radians(self.geoCenter[1]), cityLat, cityLon)
                    currentDistance = distance
                else:
                    distance = pointToPointCalc(math.radians(self.geoCenter[0]), math.radians(self.geoCenter[1]), cityLat, cityLon)
                    if distance < currentDistance:
                        capital = city
                        currentDistance = distance
            self.capital = capital
        else:
            bBallCapital = None
            fBallCapital = None
            currentDistance = None
            for city in cities:
                cityLat = math.radians(city.getLatitude())
                cityLon = math.radians(city.getLongitude())
                if bBallCapital == None:
                    bBallCapital = city
                    distance = pointToPointCalc(math.radians(self.bBallGeoCenter[0]), math.radians(self.bBallGeoCenter[1]), cityLat, cityLon)
                    currentDistance = distance
                else:
                    distance = pointToPointCalc(math.radians(self.bBallGeoCenter[0]), math.radians(self.bBallGeoCenter[1]), cityLat, cityLon)
                    if distance < currentDistance:
                        bBallCapital = city
                        currentDistance = distance
            self.bBallCapital = bBallCapital
            currentDistance = None
            for city in cities:
                cityLat = math.radians(city.getLatitude())
                cityLon = math.radians(city.getLongitude())
                if fBallCapital == None:
                    fBallCapital = city
                    distance = pointToPointCalc(math.radians(self.fBallGeoCenter[0]), math.radians(self.fBallGeoCenter[1]), cityLat, cityLon)
                    currentDistance = distance
                else:
                    distance = pointToPointCalc(math.radians(self.fBallGeoCenter[0]), math.radians(self.fBallGeoCenter[1]), cityLat, cityLon)
                    if distance < currentDistance:
                        fBallCapital = city
                        currentDistance = distance
            self.fBallCapital = fBallCapital
    
    def findAvgDistanceFromGeoCenter(self):
        if self.bBallSchools == self.fBallSchools:
            distance = 0
            for school in self.schools:
                distance += pointToPointCalc(math.radians(self.geoCenter[0]), math.radians(self.geoCenter[1]), math.radians(school.getLatitude()), math.radians(school.getLongitude()))
            self.avgDistanceFromGeoCenter = round(distance / len(self.schools), 2)
        else:
            distance = 0
            for school in self.bBallSchools:
                distance += pointToPointCalc(math.radians(self.bBallGeoCenter[0]), math.radians(self.bBallGeoCenter[1]), math.radians(school.getLatitude()), math.radians(school.getLongitude()))
            self.bBallAvgDistanceFromGeoCenter = round(distance / len(self.bBallSchools), 2)
            distance = 0
            for school in self.fBallSchools:
                distance += pointToPointCalc(math.radians(self.fBallGeoCenter[0]), math.radians(self.fBallGeoCenter[1]), math.radians(school.getLatitude()), math.radians(school.getLongitude()))
            self.fBallAvgDistanceFromGeoCenter = round(distance / len(self.fBallSchools), 2)
    
    def findAvgDistanceFromOtherSchools(self):
        if self.bBallSchools == self.fBallSchools:
            distance = 0
            for school in self.schools:
                for school2 in self.schools:
                    distance += pointToPointCalc(math.radians(school.getLatitude()), math.radians(school.getLongitude()), math.radians(school2.getLatitude()), math.radians(school2.getLongitude()))
            self.avgDistanceFromOtherSchools = round(distance / (len(self.schools) * len(self.schools)), 2)
        else:
            distance = 0
            for school in self.bBallSchools:
                for school2 in self.bBallSchools:
                    distance += pointToPointCalc(math.radians(school.getLatitude()), math.radians(school.getLongitude()), math.radians(school2.getLatitude()), math.radians(school2.getLongitude()))
            self.bBallAvgDistanceFromOtherSchools = round(distance / (len(self.bBallSchools) * len(self.bBallSchools)), 2)
            distance = 0
            for school in self.fBallSchools:
                for school2 in self.fBallSchools:
                    distance += pointToPointCalc(math.radians(school.getLatitude()), math.radians(school.getLongitude()), math.radians(school2.getLatitude()), math.radians(school2.getLongitude()))
            self.fBallAvgDistanceFromOtherSchools = round(distance / (len(self.fBallSchools) * len(self.fBallSchools)), 2)

    def __str__(self):
        return self.name + " " + self.startYear + "-" + self.endYear
    
class majorCity(object):

    def __init__(self, city, state, latitude, longitude):
        self.city = city
        self.state = state
        self.latitude = latitude
        self.longitude = longitude
    
    def getLatitude(self):
        return self.latitude
    
    def getLongitude(self):
        return self.longitude
    
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
    R = 3958.8 # radius of the earth in miles
    if abs(lat1 - lat2) < .00000001 and abs(lon1 - lon2) < .00000001:
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

def readInSchools():
    conferencesByEraObjects = []
    cities = createMajorCitiesList()

    # Find all the files in the directory
    for file in os.listdir("ConferenceByEraDB"):
        if file.endswith(".db") and file != "GeoCenters.db" and file != "ConferenceSummary.db":

            conf = file[:-3] 

            print("Processing " + file + "...")

            # Connect to the database
            conn = sqlite3.connect("ConferenceByEraDB/" + file)
            cursor = conn.cursor()

            # Select table names from database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

            tables = cursor.fetchall()

            # Itereate tables
            for table in tables:
                # Connect to table
                # print(f"Processing {table[0]}")
                cursor.execute(f"SELECT * FROM {table[0]}")
                
                # Make conference era object
                confEra = conference(conf, table[0][6:10], table[0][11:])
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
                    latitude = convertDegreesMinutesSecondsToDecimal(latitude)
                    longitude = convertDegreesMinutesSecondsToDecimal(longitude)
                    schoolObj = school(name, location, football, basketball, latitude, longitude)
                    confEra.addSchool(schoolObj)
                
                # Find the schools that play basketball and football
                confEra.findSportSpecificSchools()

                # Calculate the center of the conference
                confEra.findGeoCenter()

                # Find the capital of the conference
                confEra.findCapital(cities)

                # Find the average distance between the schools
                confEra.findAvgDistanceFromOtherSchools()

                # Find the average distance from the center of the conference
                confEra.findAvgDistanceFromGeoCenter()

                # Add the conference era object to the list of conference era objects
                conferencesByEraObjects.append(confEra)
            conn.close()

    return conferencesByEraObjects   

def conferenceSummaryDBBuilder():

    conferences = readInSchools()

    # Create a new database
    conn = sqlite3.connect("ConferenceByEraDB/ConferenceSummary.db")
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS ConferenceSummaries")
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS ConferenceSummaries
                    (Conference text, Era text, Sports text, Latitude real, Longitude real, Captial text, CapitalLatitude real, CapitalLongitude real, AvgDistanceFromCenter_miles real, AvgDistanceBetweenSchools_miles real)''')
    for conference in conferences:
        if conference.bBallSchools == conference.fBallSchools:
            c.execute(f"INSERT INTO ConferenceSummaries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (conference.name, conference.startYear + "-" + conference.endYear, 
                   "All", conference.geoCenter[0], conference.geoCenter[1], conference.capital.city + ", " + conference.capital.state,
                   conference.capital.latitude, conference.capital.longitude, conference.avgDistanceFromGeoCenter, conference.avgDistanceFromOtherSchools))
        else:
            c.execute(f"INSERT INTO ConferenceSummaries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (conference.name, conference.startYear + "-" + conference.endYear, 
                   "Football", conference.fBallGeoCenter[0], conference.fBallGeoCenter[1], conference.fBallCapital.city + ", " + conference.fBallCapital.state,
                   conference.fBallCapital.latitude, conference.fBallCapital.longitude, conference.fBallAvgDistanceFromGeoCenter, conference.fBallAvgDistanceFromOtherSchools))
            c.execute(f"INSERT INTO ConferenceSummaries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (conference.name, conference.startYear + "-" + conference.endYear, 
                   "Basketball", conference.bBallGeoCenter[0], conference.bBallGeoCenter[1], conference.bBallCapital.city + ", " + conference.bBallCapital.state,
                   conference.bBallCapital.latitude, conference.bBallCapital.longitude, conference.bBallAvgDistanceFromGeoCenter, conference.bBallAvgDistanceFromOtherSchools))
    conn.commit()
    conn.close()

def createMajorCitiesList():
    URL = "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population"

    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table', {'class': 'wikitable'})[1:2]
    tableString = str(table)
    df = pd.read_html(io.StringIO(tableString))
    df = pd.DataFrame(df[0])

    # Flatten MultiIndex columns
    df.columns = ['_'.join(col).strip() if col[0] != col[1] else col[0] for col in df.columns.values]
    df = df.drop(0)

    majorCities = []
    for row in df.iterrows():
        city = row[1]["City"]
        city = re.sub(r'\[.*?\]', '', city)
        state = row[1]["ST"]
        state = re.sub(r'\[.*?\]', '', state)
        coord = str(row[1]["Location"])
        index = coord.rfind("\ufeff")
        coord = coord[index + 1:]
        coord = coord.strip()
        lat, lon = coord.split(" ")
        lon = -float(lon[:-2])
        lat = float(lat[:-2])
        cityobj = majorCity(city, state, lat, lon)
        majorCities.append(cityobj)
    return majorCities

def buildCitiesCSV(cities):
    df = pd.DataFrame(columns=["City", "State", "Latitude", "Longitude"])
    for city in cities:
        df = df._append({"City": city.city, "State": city.state, "Latitude": city.latitude, "Longitude": city.longitude}, ignore_index=True)
    df.to_csv("DistanceCalculator/majorCities.csv", index=False)

def calculateGeoCenter(points):
    ##### Used Method A & B from this site: http://www.geomidpoint.com/calculation.html#####
    """
    Calculate the geographic center of a set of points
    :params points: a list of tuples with the latitude and longitude of the set of points
    """

    # Calculate initial center
    x = []
    y = []
    z = []
    radianPoints = []
    for point in points:
        latitude = math.radians(point[0])
        longitude = math.radians(point[1])
        radianPoints.append((latitude, longitude))
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
    totDistance = distanceCalc(currentPoint, radianPoints)

    # Test points for a better center
    for point in radianPoints:
        newDistance = distanceCalc(point, radianPoints)
        if newDistance < totDistance:
            currentPoint = point
            totDistance = newDistance
    
    testDistance = 10018 / 6371.0
    while testDistance > 0.000000002:
        testPoints = generate_test_points(currentPoint[0], currentPoint[1], testDistance)
        newPointFlag = False
        for point in testPoints:
            testPointDistance = distanceCalc(point, radianPoints)
            if testPointDistance < totDistance:
                currentPoint = point
                totDistance = testPointDistance
                newPointFlag = True
        if not newPointFlag:
            testDistance = testDistance / 2
    currentPoint = (math.degrees(currentPoint[0]), math.degrees(currentPoint[1]))
    return currentPoint


def readInSchools():
    conferencesByEraObjects = []
    cities = createMajorCitiesList()

    # Find all the files in the directory
    for file in os.listdir("ConferenceByEraDB"):
        if file.endswith(".db") and file != "GeoCenters.db" and file != "ConferenceSummary.db":

            conf = file[:-3] 

            print("Processing " + file + "...")

            # Connect to the database
            conn = sqlite3.connect("ConferenceByEraDB/" + file)
            cursor = conn.cursor()

            # Select table names from database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

            tables = cursor.fetchall()

            # Itereate tables
            for table in tables:
                # Connect to table
                # print(f"Processing {table[0]}")
                cursor.execute(f"SELECT * FROM {table[0]}")
                
                # Make conference era object
                confEra = conference(conf, table[0][6:10], table[0][11:])
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
                    latitude = convertDegreesMinutesSecondsToDecimal(latitude)
                    longitude = convertDegreesMinutesSecondsToDecimal(longitude)
                    schoolObj = school(name, location, football, basketball, latitude, longitude)
                    confEra.addSchool(schoolObj)
                
                # Find the schools that play basketball and football
                confEra.findSportSpecificSchools()

                # Calculate the center of the conference
                confEra.findGeoCenter()

                # Find the capital of the conference
                confEra.findCapital(cities)

                # Find the average distance between the schools
                confEra.findAvgDistanceFromOtherSchools()

                # Find the average distance from the center of the conference
                confEra.findAvgDistanceFromGeoCenter()

                # Add the conference era object to the list of conference era objects
                conferencesByEraObjects.append(confEra)
            conn.close()

    return conferencesByEraObjects 





# conferenceSummaryDBBuilder()



# confs = readInSchools()

# for c in confs:
#     if c.bBallSchools != c.fBallSchools:
#         print(c)
#         print(c.bBallGeoCenter, c.fBallGeoCenter)
#         print(c.bBallCapital.city, c.fBallCapital.city)