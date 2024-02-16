##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Conference_USA"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 2, URL)
dfs += scrape.getDataFrames(4, 6, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

# Adjust for non-football and non-basketball schools
for index, row in cleanedDFs[3].iterrows():
    if row["Institution"] != "United States Military Academy (Army)":
        cleanedDFs[3].drop(index, inplace=True)

# Change Army basketball value to false
cleanedDFs[3].at[1, "Basketball"] = False

combinedDFs = scrape.combineDataFrames(cleanedDFs)

combinedDFs.to_csv("HistoricalData/CUSA.csv", index=False)

print(combinedDFs)