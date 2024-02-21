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
        self.geoCenter = None
        self.capital = None
    
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
        self.geoCenter = currentPoint

        ##### Use Method A & B from this site: http://www.geomidpoint.com/calculation.html to calculate the center of the conference from #####

    def findCapital(self, cities):
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
        self.capital = capital.city, capital.state


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
    R = 6371.009 # radius of the earth in kilometers
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

    # Find all the files in the directory
    for file in os.listdir("ConferenceByEraDB"):
        if file.endswith(".db"):

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
                print(f"Processing {table[0]}")
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
                    print(name)
                    latitude = convertDegreesMinutesSecondsToDecimal(latitude)
                    longitude = convertDegreesMinutesSecondsToDecimal(longitude)
                    schoolObj = school(name, location, football, basketball, latitude, longitude)
                    confEra.addSchool(schoolObj)
                
                # Calculate the center of the conference
                print("Calculating center of conference...")
                confEra.calculateGeoCenter()

                # Find the capital of the conference
                confEra.findCapital(cities)

                # Add the conference era object to the list of conference era objects
                conferencesByEraObjects.append(confEra)
            conn.close()

    return conferencesByEraObjects   

def geoCenterDBBuilder():

    # Read in the schools
    conferences = readInSchools()

    # Create a new database
    conn = sqlite3.connect("ConferenceByEraDB/GeoCenters.db")
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS GeoCenters
                    (Conference text, Era text, Latitude real, Longitude real)''')
    for conference in conferences:
        c.execute(f"INSERT INTO GeoCenters VALUES (?, ?, ?, ?)", (conference.name, conference.startYear + "-" + conference.endYear, conference.geoCenter[0], conference.geoCenter[1]))
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
    print(df)

    majorCities = []
    for row in df.iterrows():
        city = row[1]["City"]
        state = row[1]["ST"]
        coord = str(row[1]["Location"]).strip()
        coord = coord.split("/")[1:2]
        for i in coord:
            coord = i
        print(coord)
        print(type(coord))
        latList = []
        lonList = []
        for i in coord:
            nOrSFlag = False
            if not nOrSFlag:
                latList.append(i)
            else:
                lonList.append(i)
            if type(i) == str:
                nOrSFlag = True
        print(latList)
        print(lonList)
        latList = latList[2:]
        lat = "".join(str(element) for element in latList)
        lon = "".join(str(element) for element in lonList)
        # print(lat)
        print(lon)
        lon = float(lon[1:2])
        lat = float(lat[1:2])
        cityobj = majorCity(city, state, lat, lon)
        majorCities.append(cityobj)
    return majorCities

cities = createMajorCitiesList()

# print(cities[0].latitude, cities[0].longitude)
# for city in cities:
#     print(city.city, city.state, city.latitude, city.longitude)

# conferences = readInSchools()

# for conference in conferences:
#     print(conference.name, conference.startYear, conference.endYear, conference.geoCenter, conference.capital)
#     print("\n")


# geoCenterDBBuilder()


