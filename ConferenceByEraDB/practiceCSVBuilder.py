import sqlite3
import csv

# Connect to the database
conn = sqlite3.connect('ConferenceByEraDB/BigTen.db')
cursor = conn.cursor()

# Get the table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()
table_name = table_names[-1]
print('Table name:', table_name[0])

# Fetch all rows from the table
cursor.execute("SELECT * FROM " + table_name[0] + ";")
rows = cursor.fetchall()

# Get the column names
column_names = [description[0] for description in cursor.description]

# Close the database connection
conn.close()

# Write the data to a CSV file
with open('practiceBigTen.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(column_names)
    writer.writerows(rows)
print('CSV file created successfully.')
