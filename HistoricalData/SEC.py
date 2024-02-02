##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Southeastern_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 3, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

combinedDFs.to_csv("SEC.csv", index=False)

print(combinedDFs)