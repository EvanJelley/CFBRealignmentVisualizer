import pandas as pd
import sqlite3
import os


def dbBuilder(year, rawData, csv):
    # Create a new database for each year
    conn = sqlite3.connect("ConferenceByEra/" + csv[:-4] + "/" + str(round(year)) + ".db")
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE Conference
                 (Team text, Location text, Football text, Basketball text, Coordinates text)''')

    # Insert data
    for index, row in rawData.iterrows():
        if row["Joined"] <= year and (row["Left"] > year or pd.isna(row["Left"])):
            c.execute("INSERT INTO Conference VALUES (?, ?, ?, ?, ?)", (row["Institution"], row["Location"], row["Football"], row["Basketball"], row["Coordinates"]))

    # Save (commit) the changes
    conn.commit()

    # Close connection
    conn.close()

def conferenceEraBuilder(csv):
    
    # Read in csv
    rawData = pd.read_csv("ConferenceCSVs/" + csv)

    # Set starting point
    year = min(rawData["Joined"])

    while True:

        if not os.path.exists("ConferenceByEra/" + csv[:-4] + "/" + str(round(year)) + ".db"):
            dbBuilder(year, rawData, csv)
        else:
            yearOptions = []
            for joinYear in rawData["Joined"]:
                if joinYear > year:
                    yearOptions.append(joinYear)
            for leftYear in rawData["Left"]:
                if not leftYear:
                    continue
                if leftYear > year:
                    yearOptions.append(leftYear)
            if len(yearOptions) == 0:
                break
            year = min(yearOptions)
            dbBuilder(year, rawData, csv)

def main():
    for file in os.listdir("ConferenceCSVs"):
        if file.endswith(".csv"):
            print("Processing " + file + "...")
            os.makedirs("ConferenceByEra/" + file[:-4], exist_ok=True)
            conferenceEraBuilder(file)

main()