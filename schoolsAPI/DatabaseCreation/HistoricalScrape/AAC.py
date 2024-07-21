##### NOTE THE FOLLOWING CODE IS SET TO THE LOCATION AND SHAPE OF THE RELEVANT CHARTS AT THE TIME OF WRITING. IF THE LOCATION OR SHAPE OF THE CHARTS CHANGE, THE CODE WILL NEED TO BE UPDATED #####
##### NEED TO FIGURE OUT WHAT TO DO WITH THE BIG EAST #####

import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/American_Athletic_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 3, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

print(combinedDFs)

# Save the dataframes to a csv
combinedDFs.to_csv("AAC.csv", index=False)