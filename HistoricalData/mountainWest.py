##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Mountain_West_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 3, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

# Drop Colorado College
cleanedDFs[1].drop(0, inplace=True)

# Change Hawai'i basketball value to false
cleanedDFs[1].at[1, "Basketball"] = False

combinedDFs = scrape.combineDataFrames(cleanedDFs)

combinedDFs.to_csv("HistoricalData/MountainWest.csv", index=False)

print(combinedDFs)