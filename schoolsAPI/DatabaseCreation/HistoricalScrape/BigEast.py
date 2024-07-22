import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Big_East_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(3, 4, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

for row in combinedDFs.iterrows():
    combinedDFs['Football'] = False

# print(combinedDFs)

# Save the dataframes to a csv
combinedDFs.to_csv("BigEast.csv", index=False)