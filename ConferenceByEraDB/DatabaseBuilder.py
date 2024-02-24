import pandas as pd
import sqlite3
import os

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
                                    (Team text, Location text, Football text, Basketball text, Coordinates text)''')
    
                    # Insert data
                    for index, row in rawData.iterrows():
                        if row["Joined"] <= startYear and (row["Left"] > startYear or pd.isna(row["Left"])):
                            c.execute(f"INSERT INTO teams_{startYear}_{endYear} VALUES (?, ?, ?, ?, ?)", (row["Institution"], row["Location"], row["Football"], row["Basketball"], row["Coordinates"]))
    
                    # Save (commit) the changes
                    conn.commit()
                    
                    # Update starting point
                    startYear = endYear
                    if len(yearOptions) == 0:
                        break


dbBuilder()