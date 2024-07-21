##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Mid-American_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 1, URL)
dfs += scrape.getDataFrames(3, 5, URL)

cleanedDFs = scrape.cleanDataFrames(dfs)

# Adjust for non-football and non-basketball schools
for index, row in cleanedDFs[2].iterrows():
    if row["Institution"] != "University of Central Florida" and row["Institution"] != "University of Massachusetts" and row["Institution"] != "Temple University":
        cleanedDFs[2].drop(index, inplace=True)

# Change UCF, UMass, and Temple basketball values to false
rows = [1, 11, 17]
for row in rows:
    cleanedDFs[2].at[row, "Basketball"] = False

combinedDFs = scrape.combineDataFrames(cleanedDFs)

combinedDFs.to_csv("HistoricalData/MAC.csv", index=False)

print(combinedDFs)