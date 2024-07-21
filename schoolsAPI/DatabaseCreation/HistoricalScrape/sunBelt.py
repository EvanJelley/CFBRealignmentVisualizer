##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Sun_Belt_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 1, URL)
dfs += scrape.getDataFrames(2, 4, URL)

cleanedDFs = scrape.cleanDataFrames(dfs)

# Adjust for non-football and non-basketball schools
for index, row in cleanedDFs[2].iterrows():
    if row["Institution"] != "University of Idaho" and row["Institution"] != "New Mexico State University" and row["Institution"] != "Utah State University":
        cleanedDFs[2].drop(index, inplace=True)

# Change UCF, UMass, and Temple basketball values to false
rows = [3, 4, 6, 7]
for row in rows:
    cleanedDFs[2].at[row, "Basketball"] = False


combinedDFs = scrape.combineDataFrames(cleanedDFs)

combinedDFs.to_csv("sunBelt.csv", index=False)

print(combinedDFs)