##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Pac-12_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 1, URL)
dfs += scrape.getDataFrames(2, 3, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

# Adjust for schools that have left the conference
for index, row in cleanedDFs[0].iterrows():
    if row["Institution"] != "Oregon State University" and row["Institution"] != "Washington State University":
        cleanedDFs[0].at[index, "Left"] = "2024"

combinedDFs = scrape.combineDataFrames(cleanedDFs)

combinedDFs.to_csv("HistoricalData/Pac12.csv", index=False)

print(combinedDFs)