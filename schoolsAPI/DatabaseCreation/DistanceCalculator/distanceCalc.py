import math
import sqlite3
import os
import re
import requests
import pandas as pd
import io
from bs4 import BeautifulSoup
import csv

class School(object):

    def __init__(self, name, city, state, football, basketball, latitude, longitude):
        self.name = name
        self.city = city
        self.state = state
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
            self.bBallGeoCenter = calculateGeoCenter(bBallLocations)
            if self.name != "BigEast":
                for s in self.fBallSchools:
                    latitude = s.getLatitude()
                    longitude = s.getLongitude()
                    fBallLocations.append((latitude, longitude))
                self.fBallGeoCenter = calculateGeoCenter(fBallLocations)
            else:
                self.fBallGeoCenter = None

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
            if self.name != "BigEast":
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
            if self.name == "BigEast":
                self.fBallAvgDistanceFromGeoCenter = 0
            else:
                distance = 0
                for school in self.fBallSchools:
                    distance += pointToPointCalc(math.radians(self.fBallGeoCenter[0]), math.radians(self.fBallGeoCenter[1]), math.radians(school.getLatitude()), math.radians(school.getLongitude()))
                self.fBallAvgDistanceFromGeoCenter = round(distance / len(self.fBallSchools), 2)
    
    def findAvgDistanceFromOtherSchools(self):
        if self.bBallSchools == self.fBallSchools:
            avgDistances = []
            for school in self.schools:
                distance = 0
                for school2 in self.schools:
                    if school != school2:
                        distance += pointToPointCalc(math.radians(school.getLatitude()), math.radians(school.getLongitude()), math.radians(school2.getLatitude()), math.radians(school2.getLongitude()))
                avgDistances.append(round(distance / (len(self.schools) - 1), 2))
            self.avgDistanceFromOtherSchools = round(sum(avgDistances) / len(avgDistances), 2)
        else:
            bBallAvgDistances = []
            for school in self.bBallSchools:
                distance = 0
                for school2 in self.bBallSchools:
                    if school != school2:
                        distance += pointToPointCalc(math.radians(school.getLatitude()), math.radians(school.getLongitude()), math.radians(school2.getLatitude()), math.radians(school2.getLongitude()))
                bBallAvgDistances.append(round(distance / (len(self.bBallSchools) - 1), 2))
            if bBallAvgDistances:  # Check if the list is not empty
                self.bBallAvgDistanceFromOtherSchools = round(sum(bBallAvgDistances) / len(bBallAvgDistances), 2)
            if self.name == "BigEast":
                self.fBallAvgDistanceFromOtherSchools = 0
            else:
                fBallAvgDistances = []
                for school in self.fBallSchools:
                    distance = 0
                    for school2 in self.fBallSchools:
                        if school != school2:  # Ensure we don't calculate distance from the school to itself
                            distance += pointToPointCalc(math.radians(school.getLatitude()), math.radians(school.getLongitude()), math.radians(school2.getLatitude()), math.radians(school2.getLongitude()))
                    fBallAvgDistances.append(round(distance / (len(self.fBallSchools) - 1), 2))
                if fBallAvgDistances:  # Check if the list is not empty
                    self.fBallAvgDistanceFromOtherSchools = round(sum(fBallAvgDistances) / len(fBallAvgDistances), 2)
                else:
                    self.fBallAvgDistanceFromOtherSchools = 0

    def __str__(self):
        return self.name + " " + str(self.year)
    
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

def convertToTwoLetterState(state):
    state = state.strip()
    if state == "Alabama":
        return "AL"
    elif state == "Alaska":
        return "AK"
    elif state == "Arizona":
        return "AZ"
    elif state == "Arkansas":
        return "AR"
    elif state == "California":
        return "CA"
    elif state == "Colorado":
        return "CO"
    elif state == "Connecticut":
        return "CT"
    elif state == "Delaware":
        return "DE"
    elif state == "Florida":
        return "FL"
    elif state == "Georgia":
        return "GA"
    elif state == "Hawaii":
        return "HI"
    elif state == "Idaho":
        return "ID"
    elif state == "Illinois":
        return "IL"
    elif state == "Indiana":
        return "IN"
    elif state == "Iowa":
        return "IA"
    elif state == "Kansas":
        return "KS"
    elif state == "Kentucky":
        return "KY"
    elif state == "Louisiana":
        return "LA"
    elif state == "Maine":
        return "ME"
    elif state == "Maryland":
        return "MD"
    elif state == "Massachusetts":
        return "MA"
    elif state == "Michigan":
        return "MI"
    elif state == "Minnesota":
        return "MN"
    elif state == "Mississippi":
        return "MS"
    elif state == "Missouri":
        return "MO"
    elif state == "Montana":
        return "MT"
    elif state == "Nebraska":
        return "NE"
    elif state == "Nevada":
        return "NV"
    elif state == "New Hampshire":
        return "NH"
    elif state == "New Jersey":
        return "NJ"
    elif state == "New Mexico":
        return "NM"
    elif state == "New York":
        return "NY"
    elif state == "North Carolina":
        return "NC"
    elif state == "North Dakota":
        return "ND"
    elif state == "Ohio":
        return "OH"
    elif state == "Oklahoma":
        return "OK"
    elif state == "Oregon":
        return "OR"
    elif state == "Pennsylvania":
        return "PA"
    elif state == "Rhode Island":
        return "RI"
    elif state == "South Carolina":
        return "SC"
    elif state == "South Dakota":
        return "SD"
    elif state == "Tennessee":
        return "TN"
    elif state == "Texas":
        return "TX"
    elif state == "Utah":
        return "UT"
    elif state == "Vermont":
        return "VT"
    elif state == "Virginia":
        return "VA"
    elif state == "Washington":
        return "WA"
    elif state == "West Virginia":
        return "WV"
    elif state == "Wisconsin":
        return "WI"
    elif state == "Wyoming":
        return "WY"
    else:
        return ""


def readCSV(Conference, endYear):
    conferencesByEraObjects = []
    schoolObjects = []
    cities = createMajorCitiesList()

    # Read the CSV file
    with open(f"DatabaseCreation/GeoScrape/{Conference}.csv", "r") as file:
        reader = list(csv.reader(file))
        reader.pop(0)

        startYear = 3000
        # Iterate over each row in the CSV file
        for row in reader:
            if int(row[2]) < startYear:
                startYear = int(row[2])

        for schoolObj in schoolObjects:
            print(schoolObj.name, schoolObj.location, schoolObj.football, schoolObj.basketball, schoolObj.latitude, schoolObj.longitude)

        for i in range(startYear, endYear + 1):
            print(f"Processing {Conference} {i}...")
            confEra = conference(Conference, i)
            for row in reader:

                # Add the schools to the conference object
                name = row[0]
                location = row[1].split(',')
                city = location[0].strip()
                state = convertToTwoLetterState(location[1].strip())
                football = True if row[4] == "True" else False
                basketball = True if row[5] == "True" else False
                coordinates = row[6]
                latitude, longitude = coordinateCleaner(coordinates)
                latitude = convertDegreesMinutesSecondsToDecimal(latitude)
                longitude = convertDegreesMinutesSecondsToDecimal(longitude)
                schoolObj = School(name, city, state, football, basketball, latitude, longitude)

                add = True
                for s in schoolObjects:
                    if s.name == name:
                        add = False
                if add:
                    schoolObjects.append(schoolObj)

                if int(row[2]) <= i:
                    if str(row[3]) == "False" or str(row[3]) == "":
                        confEra.addSchool(schoolObj)
                    elif int(row[3]) > i:
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

    return conferencesByEraObjects, schoolObjects

# AACYears, AACSchools = readCSV("AAC")

# BigEastEras, BigEastSchools = readCSV("BigEast")

# BigEightEras, BigEightSchools = readCSV("BigEight", 1996)

# SWCEras, SWCSchools = readCSV("SWC", 1996)

# BigWestEras, BigWestSchools = readCSV("BigWest", 2000)

# BorderEras, BorderSchools = readCSV("Border", 1962)

# SkylineEras, SkylineSchools = readCSV("Skyline", 1962) 

# WACEras, WACSchools = readCSV("WAC", 2012)

# PAC12Eras, PAC12Schools = readCSV("Pac12", 2024)

# ACCEras, ACCSchools = readCSV("ACC", 2024)

# SECCEras, SECCSchools = readCSV("SEC", 2024)

# Big10Eras, Big10Schools = readCSV("BigTen", 2024)

# Big12Eras, Big12Schools = readCSV("Big12", 2024)

# CUSAEras, CUSASchools = readCSV("CUSA", 2024)

# MACEras, MACSchools = readCSV("MAC", 2024)

# SunBeltEras, SunBeltSchools = readCSV("SunBelt", 2024)

# MountainWestEras, MountainWestSchools = readCSV("MountainWest", 2024)


# for era in SECCEras:
#     print(era.name, era.year, era.fBallAvgDistanceFromOtherSchools, era.bBallAvgDistanceFromOtherSchools)
#     if era.fBallSchools == era.bBallSchools:
#         print(era.name, era.year, era.avgDistanceFromOtherSchools)
#         for school in era.schools:
#             print(school.name)
#         print("\n")
#     else:
#         print("Football")
#         for school in era.fBallSchools:
#             print(school.name)
#         print("\n")
#         print("Basketball")
#         for school in era.bBallSchools:
#             print(school.name)
#         print("\n")

def buildHistoricConferences(apps, schema_editor):
    ConferenceBuilder(apps, schema_editor, "BigEight", 1996)
    ConferenceBuilder(apps, schema_editor, "SWC", 1996)
    ConferenceBuilder(apps, schema_editor, "BigWest", 1999)
    ConferenceBuilder(apps, schema_editor, "Border", 1961)
    ConferenceBuilder(apps, schema_editor, "Skyline", 1961)
    ConferenceBuilder(apps, schema_editor, "WAC", 2011)

def correctPac12DistanceBetweenSchools(apps, schema_editor):
    recalculateConferences(apps, schema_editor, "Pac12", 2024)



def correctMoreConferences(apps, schema_editor):
    recalculateConferences(apps, schema_editor, "ACC", 2024)
    recalculateConferences(apps, schema_editor, "SEC", 2024)
    recalculateConferences(apps, schema_editor, "BigTen", 2024)
    recalculateConferences(apps, schema_editor, "BigEight", 1996)
    ConferenceBuilder(apps, schema_editor, "BigWest", 2000)
    recalculateConferences(apps, schema_editor, "Border", 1962)
    recalculateConferences(apps, schema_editor, "Skyline", 1962)
    recalculateConferences(apps, schema_editor, "SWC", 1996)
    ConferenceBuilder(apps, schema_editor, "WAC", 2012)
    recalculateConferences(apps, schema_editor, "Big12", 2024)
    recalculateConferences(apps, schema_editor, "CUSA", 2024)
    recalculateConferences(apps, schema_editor, "MAC", 2024)
    recalculateConferences(apps, schema_editor, "SunBelt", 2024)
    recalculateConferences(apps, schema_editor, "MountainWest", 2024)




def recalculateConferences(apps, schema_editor, conferenceName, endYear):
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')

    eras, schools = readCSV(conferenceName, endYear)

    for confERA in eras:
        if confERA.fBallSchools == confERA.bBallSchools:
            print("Recalculating " + conferenceName + " " + str(confERA.year) + "..." + " " + str(confERA.avgDistanceFromOtherSchools))
            ConferenceByYear.objects.filter(year__year=confERA.year, conference__name=conferenceName).update(avgDistanceBetweenSchools=confERA.avgDistanceFromOtherSchools)
        else:
            ConferenceByYear.objects.filter(year__year=confERA.year, conference__name=conferenceName, football=True).update(avgDistanceBetweenSchools=confERA.fBallAvgDistanceFromOtherSchools)
            ConferenceByYear.objects.filter(year__year=confERA.year, conference__name=conferenceName, basketball=True).update(avgDistanceBetweenSchools=confERA.bBallAvgDistanceFromOtherSchools)
            



def ConferenceBuilder(apps, schema_editor, conferenceName, endYear):
    ConferenceName = apps.get_model('conferences', 'ConferenceName')
    School = apps.get_model('conferences', 'School')
    Year = apps.get_model('conferences', 'Year')
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')
    MajorCity = apps.get_model('conferences', 'MajorCity')

    eras, schools = readCSV(conferenceName, endYear)

    if not ConferenceName.objects.filter(name=conferenceName).exists():
        ConferenceName.objects.create(name=conferenceName)

    for university in schools:
        if not School.objects.filter(name=university.name).exists():
            School.objects.create(name=university.name, city=university.city, state=university.state, latitude=university.latitude, longitude=university.longitude)                            

    for confERA in eras:
        if confERA.fBallSchools == confERA.bBallSchools:
            if not MajorCity.objects.filter(name=confERA.capital.city).exists():
                MajorCity.objects.create(name=confERA.capital.city, state=confERA.capital.state, latitude=confERA.capital.latitude, longitude=confERA.capital.longitude)
            conference_by_year = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                                            conference=ConferenceName.objects.get(name=conferenceName),
                                            football=True,
                                            basketball=True,
                                            centerLat= confERA.geoCenter[0],
                                            centerLon= confERA.geoCenter[1],
                                            capital= MajorCity.objects.get(name=confERA.capital.city),
                                            avgDistanceFromCenter= confERA.avgDistanceFromGeoCenter,
                                            avgDistanceBetweenSchools= confERA.avgDistanceFromOtherSchools)
            uniNames = []
            for team in confERA.schools:
                uniNames.append(team.name)
            conference_by_year.schools.set(School.objects.filter(name__in=uniNames))
        else:
            if not MajorCity.objects.filter(name=confERA.bBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.bBallCapital.city, state=confERA.bBallCapital.state, latitude=confERA.bBallCapital.latitude, longitude=confERA.bBallCapital.longitude)

            if not MajorCity.objects.filter(name=confERA.fBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.fBallCapital.city, state=confERA.fBallCapital.state, latitude=confERA.fBallCapital.latitude, longitude=confERA.fBallCapital.longitude)
            
            footballSchools = []
            basketballSchools = []
            for team in confERA.fBallSchools:
                footballSchools.append(team.name)
            for team in confERA.bBallSchools:
                basketballSchools.append(team.name)
            conference_by_year_fball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name=conferenceName),
                football=True,
                basketball=False,
                centerLat= confERA.fBallGeoCenter[0],
                centerLon= confERA.fBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.fBallCapital.city),
                avgDistanceFromCenter= confERA.fBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.fBallAvgDistanceFromOtherSchools)
            conference_by_year_bball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name=conferenceName),
                football=False,
                basketball=True,
                centerLat= confERA.bBallGeoCenter[0],
                centerLon= confERA.bBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.bBallCapital.city),
                avgDistanceFromCenter= confERA.bBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.bBallAvgDistanceFromOtherSchools)
            
            conference_by_year_fball.schools.set(School.objects.filter(name__in=footballSchools))
            conference_by_year_bball.schools.set(School.objects.filter(name__in=basketballSchools))



def SWCBuilder(apps, schema_editor):
    ConferenceName = apps.get_model('conferences', 'ConferenceName')
    School = apps.get_model('conferences', 'School')
    Year = apps.get_model('conferences', 'Year')
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')
    MajorCity = apps.get_model('conferences', 'MajorCity')

    eras, schools = readCSV("SWC", 1996)

    ConferenceName.objects.create(name="SWC")

    for university in schools:
        if not School.objects.filter(name=university.name).exists():
            School.objects.create(name=university.name, city=university.city, state=university.state, latitude=university.latitude, longitude=university.longitude)                            

    for confERA in eras:
        if confERA.fBallSchools == confERA.bBallSchools:
            if not MajorCity.objects.filter(name=confERA.capital.city).exists():
                MajorCity.objects.create(name=confERA.capital.city, state=confERA.capital.state, latitude=confERA.capital.latitude, longitude=confERA.capital.longitude)
            conference_by_year = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                                            conference=ConferenceName.objects.get(name="SWC"),
                                            football=True,
                                            basketball=True,
                                            centerLat= confERA.geoCenter[0],
                                            centerLon= confERA.geoCenter[1],
                                            capital= MajorCity.objects.get(name=confERA.capital.city),
                                            avgDistanceFromCenter= confERA.avgDistanceFromGeoCenter,
                                            avgDistanceBetweenSchools= confERA.avgDistanceFromOtherSchools)
            uniNames = []
            for team in confERA.schools:
                uniNames.append(team.name)
            conference_by_year.schools.set(School.objects.filter(name__in=uniNames))
        else:
            if not MajorCity.objects.filter(name=confERA.bBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.bBallCapital.city, state=confERA.bBallCapital.state, latitude=confERA.bBallCapital.latitude, longitude=confERA.bBallCapital.longitude)

            if not MajorCity.objects.filter(name=confERA.fBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.fBallCapital.city, state=confERA.fBallCapital.state, latitude=confERA.fBallCapital.latitude, longitude=confERA.fBallCapital.longitude)
            
            footballSchools = []
            basketballSchools = []
            for team in confERA.fBallSchools:
                footballSchools.append(team.name)
            for team in confERA.bBallSchools:
                basketballSchools.append(team.name)
            conference_by_year_fball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name="SWC"),
                football=True,
                basketball=False,
                centerLat= confERA.fBallGeoCenter[0],
                centerLon= confERA.fBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.fBallCapital.city),
                avgDistanceFromCenter= confERA.fBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.fBallAvgDistanceFromOtherSchools)
            conference_by_year_bball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name="SWC"),
                football=False,
                basketball=True,
                centerLat= confERA.bBallGeoCenter[0],
                centerLon= confERA.bBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.bBallCapital.city),
                avgDistanceFromCenter= confERA.bBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.bBallAvgDistanceFromOtherSchools)
            
            conference_by_year_fball.schools.set(School.objects.filter(name__in=footballSchools))
            conference_by_year_bball.schools.set(School.objects.filter(name__in=basketballSchools))

def BigEastBuilder(apps, schema_editor):
    ConferenceName = apps.get_model('conferences', 'ConferenceName')
    School = apps.get_model('conferences', 'School')
    Year = apps.get_model('conferences', 'Year')
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')
    MajorCity = apps.get_model('conferences', 'MajorCity')

    BigEastEras, BigEastSchools = readCSV("BigEast")

    ConferenceName.objects.create(name="BigEast")

    for university in BigEastSchools:
        if not School.objects.filter(name=university.name).exists():
            School.objects.create(name=university.name, city=university.city, state=university.state, latitude=university.latitude, longitude=university.longitude)                            

    for confERA in BigEastEras:
        print(confERA.name, confERA.year)
        if not MajorCity.objects.filter(name=confERA.bBallCapital.city).exists():
            MajorCity.objects.create(name=confERA.bBallCapital.city, state=confERA.bBallCapital.state, latitude=confERA.bBallCapital.latitude, longitude=confERA.bBallCapital.longitude)
        
        basketballSchools = []
        for team in confERA.bBallSchools:
            basketballSchools.append(team.name)
        conference_by_year_bball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
            conference=ConferenceName.objects.get(name="BigEast"),
            football=False,
            basketball=True,
            centerLat= confERA.bBallGeoCenter[0],
            centerLon= confERA.bBallGeoCenter[1],
            capital= MajorCity.objects.get(name=confERA.bBallCapital.city),
            avgDistanceFromCenter= confERA.bBallAvgDistanceFromGeoCenter,
            avgDistanceBetweenSchools= confERA.bBallAvgDistanceFromOtherSchools)
        
        conference_by_year_bball.schools.set(School.objects.filter(name__in=basketballSchools))

def BigEightBuilder(apps, schema_editor):
    ConferenceName = apps.get_model('conferences', 'ConferenceName')
    School = apps.get_model('conferences', 'School')
    Year = apps.get_model('conferences', 'Year')
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')
    MajorCity = apps.get_model('conferences', 'MajorCity')

    eras, schools = readCSV("BigEight", 1996)

    ConferenceName.objects.create(name="BigEight")

    for university in schools:
        if not School.objects.filter(name=university.name).exists():
            School.objects.create(name=university.name, city=university.city, state=university.state, latitude=university.latitude, longitude=university.longitude)                            

    for confERA in eras:
        if confERA.fBallSchools == confERA.bBallSchools:
            if not MajorCity.objects.filter(name=confERA.capital.city).exists():
                MajorCity.objects.create(name=confERA.capital.city, state=confERA.capital.state, latitude=confERA.capital.latitude, longitude=confERA.capital.longitude)
            conference_by_year = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                                            conference=ConferenceName.objects.get(name="BigEight"),
                                            football=True,
                                            basketball=True,
                                            centerLat= confERA.geoCenter[0],
                                            centerLon= confERA.geoCenter[1],
                                            capital= MajorCity.objects.get(name=confERA.capital.city),
                                            avgDistanceFromCenter= confERA.avgDistanceFromGeoCenter,
                                            avgDistanceBetweenSchools= confERA.avgDistanceFromOtherSchools)
            uniNames = []
            for team in confERA.schools:
                uniNames.append(team.name)
            conference_by_year.schools.set(School.objects.filter(name__in=uniNames))
        else:
            if not MajorCity.objects.filter(name=confERA.bBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.bBallCapital.city, state=confERA.bBallCapital.state, latitude=confERA.bBallCapital.latitude, longitude=confERA.bBallCapital.longitude)

            if not MajorCity.objects.filter(name=confERA.fBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.fBallCapital.city, state=confERA.fBallCapital.state, latitude=confERA.fBallCapital.latitude, longitude=confERA.fBallCapital.longitude)
            
            footballSchools = []
            basketballSchools = []
            for team in confERA.fBallSchools:
                footballSchools.append(team.name)
            for team in confERA.bBallSchools:
                basketballSchools.append(team.name)
            conference_by_year_fball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name="BigEight"),
                football=True,
                basketball=False,
                centerLat= confERA.fBallGeoCenter[0],
                centerLon= confERA.fBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.fBallCapital.city),
                avgDistanceFromCenter= confERA.fBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.fBallAvgDistanceFromOtherSchools)
            conference_by_year_bball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name="BigEight"),
                football=False,
                basketball=True,
                centerLat= confERA.bBallGeoCenter[0],
                centerLon= confERA.bBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.bBallCapital.city),
                avgDistanceFromCenter= confERA.bBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.bBallAvgDistanceFromOtherSchools)
            
            conference_by_year_fball.schools.set(School.objects.filter(name__in=footballSchools))
            conference_by_year_bball.schools.set(School.objects.filter(name__in=basketballSchools))

def AACBuilder(apps, schema_editor):
    ConferenceName = apps.get_model('conferences', 'ConferenceName')
    School = apps.get_model('conferences', 'School')
    Year = apps.get_model('conferences', 'Year')
    ConferenceByYear = apps.get_model('conferences', 'ConferenceByYear')
    MajorCity = apps.get_model('conferences', 'MajorCity')

    AACEras, AACSchools = readCSV("AAC")

    ConferenceName.objects.create(name="AAC")

    for university in AACSchools:
        if not School.objects.filter(name=university.name).exists():
            School.objects.create(name=university.name, city=university.city, state=university.state, latitude=university.latitude, longitude=university.longitude)                            

    for confERA in AACEras:
        if confERA.fBallSchools == confERA.bBallSchools:
            if not MajorCity.objects.filter(name=confERA.capital.city).exists():
                MajorCity.objects.create(name=confERA.capital.city, state=confERA.capital.state, latitude=confERA.capital.latitude, longitude=confERA.capital.longitude)
            conference_by_year = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                                            conference=ConferenceName.objects.get(name="AAC"),
                                            football=True,
                                            basketball=True,
                                            centerLat= confERA.geoCenter[0],
                                            centerLon= confERA.geoCenter[1],
                                            capital= MajorCity.objects.get(name=confERA.capital.city),
                                            avgDistanceFromCenter= confERA.avgDistanceFromGeoCenter,
                                            avgDistanceBetweenSchools= confERA.avgDistanceFromOtherSchools)
            uniNames = []
            for team in confERA.schools:
                uniNames.append(team.name)
            conference_by_year.schools.set(School.objects.filter(name__in=uniNames))
        else:
            if not MajorCity.objects.filter(name=confERA.bBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.bBallCapital.city, state=confERA.bBallCapital.state, latitude=confERA.bBallCapital.latitude, longitude=confERA.bBallCapital.longitude)

            if not MajorCity.objects.filter(name=confERA.fBallCapital.city).exists():
                MajorCity.objects.create(name=confERA.fBallCapital.city, state=confERA.fBallCapital.state, latitude=confERA.fBallCapital.latitude, longitude=confERA.fBallCapital.longitude)
            
            footballSchools = []
            basketballSchools = []
            for team in confERA.fBallSchools:
                footballSchools.append(team.name)
            for team in confERA.bBallSchools:
                basketballSchools.append(team.name)
            conference_by_year_fball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name="AAC"),
                football=True,
                basketball=False,
                centerLat= confERA.fBallGeoCenter[0],
                centerLon= confERA.fBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.fBallCapital.city),
                avgDistanceFromCenter= confERA.fBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.fBallAvgDistanceFromOtherSchools)
            conference_by_year_bball = ConferenceByYear.objects.create(year=Year.objects.get(year=confERA.year),
                conference=ConferenceName.objects.get(name="AAC"),
                football=False,
                basketball=True,
                centerLat= confERA.bBallGeoCenter[0],
                centerLon= confERA.bBallGeoCenter[1],
                capital= MajorCity.objects.get(name=confERA.bBallCapital.city),
                avgDistanceFromCenter= confERA.bBallAvgDistanceFromGeoCenter,
                avgDistanceBetweenSchools= confERA.bBallAvgDistanceFromOtherSchools)
            
            conference_by_year_fball.schools.set(School.objects.filter(name__in=footballSchools))
            conference_by_year_bball.schools.set(School.objects.filter(name__in=basketballSchools))

                





# confs = readInSchools()

# for c in confs:
#     if c.bBallSchools != c.fBallSchools:
#         print(c)
#         print(c.bBallGeoCenter, c.fBallGeoCenter)
#         print(c.bBallCapital.city, c.fBallCapital.city)