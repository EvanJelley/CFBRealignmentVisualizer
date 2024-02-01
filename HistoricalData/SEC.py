import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Southeastern_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 3, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

print(combinedDFs)