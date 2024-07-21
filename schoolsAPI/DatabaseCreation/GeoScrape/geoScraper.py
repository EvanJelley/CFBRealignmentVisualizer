import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import os
import numpy as np

def getCoordinates(city, state):
    """
    This function takes a city and state and returns the latitude and longitude of the city.
    """
    page = requests.get(f"https://en.wikipedia.org/wiki/{city},_{state}")
    soup = bs(page.text, 'lxml')
    latitude = soup.find("span", {"class": "latitude"})
    print(latitude)
    longitude = soup.find("span", {"class": "longitude"})
    print(longitude)
    
    return latitude.text, longitude.text

def addCoordinatesToCSV(csvFile):
    """
    This function takes a csv file and adds a column called "Coordinates" to the csv file."
    """
    df = pd.read_csv("DatabaseCreation/GeoScrape/" + csvFile)
    df["Coordinates"] = ""

    for index, row in df.iterrows():
        location = row["Location"]
        print("Processing " + location + "...")
        city = location.split(",")[0]
        state = location.split(",")[1]
        city = city.replace(" ", "_")
        state = state.replace(" ", "_")
        coordinates = getCoordinates(city, state)
        df.at[index, "Coordinates"] = coordinates[0] + ',' + coordinates[1]
    
    df.to_csv("DatabaseCreation/GeoScrape/" + csvFile, index=False)

def updateCSVs():
    """
    This function updates all csv files in the current directory.
    """
    for file in os.listdir("DatabaseCreation/GeoScrape"):
        if file.endswith(".csv"):
            print("Processing " + file + "...")
            addCoordinatesToCSV(file)

# Correct "Left" column for csvs by replacing False with NaN
def correctLeftColumn():
    for file in os.listdir("ConferenceCSVs"):
        if file.endswith(".csv"):
            df = pd.read_csv("ConferenceCSVs/" + file)
            df["Left"] = df["Left"].replace("False", np.nan) 
            df.to_csv("ConferenceCSVs/" + file, index=False)

updateCSVs()
# correctLeftColumn()

