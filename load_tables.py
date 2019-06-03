#!/usr/bin/python
import MySQLdb as mdb
import sys
import os
import config

import warnings
warnings.filterwarnings("ignore")
 
db = mdb.connect(config.host, config.user, config.passwd,config.db)
 
# Create a Cursor object to execute queries.
cur = db.cursor()

# Delete old tables
for line in open("delete_tables.sql"):
   if line == '':
      break;
   cur.execute(line)

# Make new tables
for line in open("make_tables.sql"):
   if line == '':
      break;
   cur.execute(line)

# Load courses table
os.system('python3 make_courses_csv.py')
cur.execute("LOAD DATA LOCAL INFILE 'courses.csv' INTO TABLE courses FIELDS TERMINATED BY ','")

# Load polyratings table
os.system('python3 make_polyratings_csv.py')
cur.execute("LOAD DATA LOCAL INFILE 'poly_ratings.csv' INTO TABLE polyratings FIELDS TERMINATED BY ','")
