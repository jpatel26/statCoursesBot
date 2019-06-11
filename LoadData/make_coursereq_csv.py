import pandas as pd
import sys
import os
import requests
import time
import urllib.request
from bs4 import BeautifulSoup
import re
import csv

stat_df = pd.DataFrame()

resp = requests.get("http://catalog.calpoly.edu/collegesandprograms/collegeofsciencemathematics/statistics/bsstatistics")
soup = BeautifulSoup(resp.content, 'html.parser')
 
div = soup.find("body")
#div = div.find("div", {"id" : "courseinventorycontainer"})
div = div.find("div", {"id" : "wrapper"})
div = div.find("div", {"id" : "container", "class": "clearfix"})
div = div.find("div", {"id" : "left-col"})
div = div.find("div", {"id" : "content"})
div = div.find("div", {"id" : "textcontainer", "class": "tab_content"})
#div = div.find("div", {"class": "table-pair"})
div = div.find("table", {"class": "sc_courselist"})
#courses = div.find_all("div", {"class" : "courseblock"})
courses = div.find_all("tr", {"class" : "even"}) + div.find_all("tr", {"class": "odd"})

classes = {}

for c in courses:
   c = str(c)
   t = ((re.findall("(STAT [0-9]{3})", c)))
   if len(t) < 1:
      continue
   classes[t[0]] = []
   if t[0] in ["STAT 425", "STAT 426", "STAT 427", "STAT 465"]:
      classes[t[0]] = ['y','n', 'n']
   elif (re.findall(" (.)", t[0]))[0] != "4":
      classes[t[0]] = ['y', 'n', 'n']
   else:
      classes[t[0]] = ['y', 'y', 'n']
      
   
resp = requests.get("http://catalog.calpoly.edu/collegesandprograms/collegeofsciencemathematics/statistics/statisticsminor")
soup = BeautifulSoup(resp.content, 'html.parser')
 
div = soup.find("body")
#div = div.find("div", {"id" : "courseinventorycontainer"})
div = div.find("div", {"id" : "wrapper"})
div = div.find("div", {"id" : "container", "class": "clearfix"})
div = div.find("div", {"id" : "left-col"})
div = div.find("div", {"id" : "content"})
div = div.find("div", {"id" : "textcontainer", "class": "tab_content"})
#div = div.find("div", {"class": "table-pair"})
div = div.find("table", {"class": "sc_courselist"})
#courses = div.find_all("div", {"class" : "courseblock"})
courses = div.find_all("tr", {"class" : "even"}) + div.find_all("tr", {"class": "odd"})

for c in courses:
   c = str(c)
   t = ((re.findall("(STAT [0-9]{3})", c)))
   if len(t) < 1:
      continue
   if len(t) == 1:
      t = t[0]
      if t in classes.keys():
         classes[t][2] = 'y'
      else:
         classes[t] = ['n', 'n', 'y']
   else:
      for cl in t:
         if cl in classes.keys():
            classes[cl][2] = 'y'
         else:
            classes[cl] = ['n', 'n', 'y']

vals = list(classes.values())

stat_df = pd.DataFrame.from_records(vals)

#keys = [i.split()[1] for i in list(classes.keys())]
#keys = list(classes.keys())
keys = ["stat" + i.split()[1] for i in list(classes.keys())]
keys = [i.lower().replace(' ','') for i in keys]
stat_df["course_num"] = pd.Series(keys)
stat_df.columns = ['major_req', 'major_elect', 'minor', 'course_num']

cols = stat_df.columns.tolist()
cols = cols[-1:] + cols[:-1]
stat_df = stat_df[cols]


stat_df.to_csv("course_req.csv", index=False, header=False)

