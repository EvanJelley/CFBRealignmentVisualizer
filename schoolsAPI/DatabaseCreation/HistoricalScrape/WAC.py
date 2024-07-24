import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Western_Athletic_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(2, 3, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

# print(combinedDFs)

# Save the dataframes to a csv
combinedDFs.to_csv("WAC.csv", index=False)