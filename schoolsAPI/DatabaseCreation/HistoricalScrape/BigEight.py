import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Big_Eight_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 2, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

# print(combinedDFs)

# Save the dataframes to a csv
combinedDFs.to_csv("BigEight.csv", index=False)