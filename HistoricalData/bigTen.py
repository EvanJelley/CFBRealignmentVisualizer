import wikiScrape as scrape
import pandas as pd

# Define the URL
URL = "https://en.wikipedia.org/wiki/Big_Ten_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 4, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

# Manually clean football and basketball data
cleanedDFs[2]['Football'] = False
cleanedDFs[2]['Basketball'] = False

combinedDFs = scrape.combineDataFrames(cleanedDFs)

print(combinedDFs)
