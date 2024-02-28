import pandas as pd
import sqlite3
import os
import re


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


def dbBuilder():
    # Pull CSVs
    for file in os.listdir("FinalConferenceCSVs"):
        if file.endswith(".csv"):
            rawData = pd.read_csv("FinalConferenceCSVs/" + file)
            print("Processing " + file + "...")

            # Create a new database for the conference
            conn = sqlite3.connect("ConferenceByEraDB/" + file[:-4] + ".db")
            c = conn.cursor()

            # Set starting point
            startYear = min(rawData["Joined"])

            while True:
                    
                    yearOptions = []
                    for joinYear in rawData["Joined"]:
                        if joinYear > startYear:
                            yearOptions.append(joinYear)
                    for leftYear in rawData["Left"]:
                        if not leftYear:
                            continue
                        if leftYear > startYear:
                            yearOptions.append(leftYear)
                    if len(yearOptions) == 0:
                        endYear = 'Present'
                    else:
                        endYear = round(min(yearOptions))
                    
                    c.execute(f"DROP TABLE IF EXISTS teams_{startYear}_{endYear}")
                    # Create table
                    c.execute(f'''CREATE TABLE IF NOT EXISTS teams_{startYear}_{endYear}
                                    (Team text, Location text, Football text, Basketball text, Latitude text, Longitude text)''')
    
                    # Insert data
                    for index, row in rawData.iterrows():
                        lat, lon = coordinateCleaner(row["Coordinates"])
                        print(lat)
                        print(lon)
                        lat = toDecimal(lat)
                        lon = toDecimal(lon)
                        if row["Joined"] <= startYear and (row["Left"] > startYear or pd.isna(row["Left"])):
                            c.execute(f"INSERT INTO teams_{startYear}_{endYear} VALUES (?, ?, ?, ?, ?, ?)", (row["Institution"], row["Location"], row["Football"], row["Basketball"], lat, lon))
    
                    # Save (commit) the changes
                    conn.commit()
                    
                    # Update starting point
                    startYear = endYear
                    if len(yearOptions) == 0:
                        break


dbBuilder()