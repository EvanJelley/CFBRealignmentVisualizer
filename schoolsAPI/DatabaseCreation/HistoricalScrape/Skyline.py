import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Skyline_Conference_(1938–1962)"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 2, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

# print(combinedDFs)

# Save the dataframes to a csv
combinedDFs.to_csv("Skyline.csv", index=False)