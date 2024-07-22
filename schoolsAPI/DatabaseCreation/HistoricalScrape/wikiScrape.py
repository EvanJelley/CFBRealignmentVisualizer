# import required modules
from bs4 import BeautifulSoup
import requests
import pandas as pd
import io
import numpy as np

def getDataFrames(firstTable, lastTable, URL):
    """
    This function takes a URL and returns a list of dataframes containing the tables from the Wikipedia page. The firstTable and lastTable parameters are used to specify which tables to scrape.
    """
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})[firstTable:lastTable]
    dfs = []
    for table in tables:
        tableString = str(table)
        df = pd.read_html(io.StringIO(tableString))
        df = pd.DataFrame(df[0])
        dfs.append(df)
    return dfs

def dfCleaner(df):
    """
    This function takes a dataframe and cleans it up by removing unwanted columns and rows, flattening MultiIndex columns, renaming columns, removing unwanted characters, and resetting the index.
    """

    # Remove unwanted columns
    keepers = ["Institution", "Location", "Join", "City", "State", "Left", "Joined"]
    columns = df.columns
    if type(columns) == pd.core.indexes.multi.MultiIndex:
        columns = list(columns.get_level_values(0))
    trash = []
    for column in columns:
        dumpFlag = True
        for keeper in keepers:
            if keeper in column:
                dumpFlag = False
        if dumpFlag:
            trash.append(column)
    df.drop(trash, axis=1, inplace=True)

    # Remove unwanted rows
    trash = []
    schoolWords = ["University", "College", "School", "Institute", "Campus", "Center", "Academy", "State", "Tech"]
    for index, row in df.iterrows():
        dumpFlag = True
        for word in schoolWords:
            if word in str(row["Institution"]):
                dumpFlag = False
        if dumpFlag:
            trash.append(index)
    df.drop(trash, axis=0, inplace=True)

    # Flatten MultiIndex columns
    if type(df.columns) == pd.core.indexes.multi.MultiIndex:
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    # Check for 'Left' in any column and add it if it doesn't exist
    if not any('Left' in col for col in df.columns):
        df['Left'] = np.NaN

    if not any('Joined' in col for col in df.columns):
        df['Joined'] = np.NaN

    # Check if 'City' and 'State' columns exist
    if 'City' in df.columns and 'State' in df.columns:
        # Merge 'City' and 'State' columns
        df['Location'] = df['City'] + ', ' + df['State']
        # Drop 'City' and 'State' columns
        df.drop(['City', 'State'], axis=1, inplace=True)
        # Reorder columns
        df = df.loc[:,['Institution', 'Location', 'Joined', 'Left']]

    # Add Football and Basketball columns with default value of True
    if 'Football' not in df.columns:
        df['Football'] = True
    if 'Basketball' not in df.columns:
        df['Basketball'] = True
    
    # Rename columns
    newColumnNames = ["Institution", "Location", "Joined", "Left", "Football", "Basketball"]
    df.columns = newColumnNames

    # Remove unwanted characters
    df['Joined'] = df['Joined'].astype(str).str.slice(0, 4)
    df['Left'] = df['Left'].astype(str).str.slice(0, 4)

    # Change Left column NaN values to False
    df['Left'] = df['Left'].replace('nan', False)

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Final scrub for bracketed text
    df = df.replace(to_replace=r'\[[^\]]*\]', value='', regex=True)

    return df

def cleanDataFrames(dfs):
    """
    This function takes a list of dataframes and cleans them up using the dfCleaner function.
    """
    cleanedDFs = []
    for df in dfs:
        cleanedDFs.append(dfCleaner(df))
    return cleanedDFs


def combineDataFrames(dfs):
    """
    This function takes a list of dataframes and combines them into one dataframe.
    """
    combinedDF = pd.concat(dfs)
    combinedDF.reset_index(drop=True, inplace=True)
    return combinedDF

