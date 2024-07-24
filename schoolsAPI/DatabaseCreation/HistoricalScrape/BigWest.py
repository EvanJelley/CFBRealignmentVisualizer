import wikiScrape as scrape
import pandas as pd
import numpy as np

# Define the URL
URL = "https://en.wikipedia.org/wiki/Big_West_Conference"

# Pull and clean dataframes
dfs = scrape.getDataFrames(0, 1, URL) + scrape.getDataFrames(2, 3, URL) + scrape.getDataFrames(4, 5, URL)
cleanedDFs = scrape.cleanDataFrames(dfs)

combinedDFs = scrape.combineDataFrames(cleanedDFs)

drop_indices = []

# Iterate over the DataFrame
for index, row in combinedDFs.iterrows():
    # Check if the 'Joined' year is greater than or equal to 2000
    if int(row['Joined']) >= 2000:
        drop_indices.append(index)

# Drop the rows outside the loop
combinedDFs.drop(drop_indices, inplace=True)

# Update 'Left' column based on conditions
combinedDFs.loc[(combinedDFs['Left'] == False) | (combinedDFs['Left'].astype(int) >= 2000), 'Left'] = 2000
combinedDFs['Left'] = combinedDFs['Left'].astype(int) - 1


# print(combinedDFs)

# Save the dataframes to a csv
combinedDFs.to_csv("BigWest.csv", index=False)