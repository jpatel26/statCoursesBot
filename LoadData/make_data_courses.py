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

resp = requests.get("http://catalog.calpoly.edu/coursesaz/data/")
soup = BeautifulSoup(resp.content, 'html.parser')
 
div = soup.find("div", {"id" : "content"})
div = div.find("div", {"id" : "courseinventorycontainer"})
div = div.find("div", {"class" : "courses"})
courses = div.find_all("div", {"class" : "courseblock"})
course_num = []
course_title = []
course_units = []
course_area = []
course_terms = []
course_pre = []
course_description = []

for c in courses:
   title = c.find("p", {"class" : "courseblocktitle"})
   title = title.find("strong")
   credits = title.find("span", {"class" : "courseblockhours"})
   course_units.append((str(credits.string.strip())[:-6]).lower())
   tmp_title = str(title)[12:16]
   number = "data" + tmp_title.replace(",", '').lower()
   newstr = number[:4] + number[5:]
   course_num.append(newstr)
   jank = str(title)[17:]
   text = jank.partition(".")[0]
   course_title.append(text.replace(",", '').replace('"', '').lower())

   area = c.find_all("p", {"class" : "noindent"})
   if len(area) == 2:
      tmp_terms = str(area[1])[43:-4]
      course_terms.append(tmp_terms.replace(',','').lower())
      course_area.append((str(area[0])[20:-4]).lower())
   else:
      tmp_terms = str(area[0])[43:-4]
      course_terms.append(tmp_terms.replace(',','').lower())
      course_area.append("None")

   pre = c.find_all("p", {"class" : None})
   pr = re.search(r'<p>Prerequisite:(.*)<\/p>,', str(pre))
   if not pr:
      pr = re.search(r'<p>Corequisite:(.*)<\/p>,', str(pre))
   if pr:
      # Replace links with names
      link = re.findall(r'<a(.*)<\/a>', str(pr.groups()))
      if link: # There is a link in the description
         extracted = re.findall(r'([A-Z]+ \d+)', str(link))
         #print("Extracted: ", extracted)
         prgood = re.sub(r'<a(.*)<\/a>', str(extracted), str(pr.groups()))
         if prgood:
            course_pre.append(prgood.replace('[', '').replace(']', '').replace("'",'').replace(",", '').replace(')','').replace('(','').lower());

      else:
         course_pre.append(str(pr.groups()).replace('[', '').replace(']', '').replace("'",'').replace(",", '').replace(')','').replace('(','').lower());

   else:
      course_pre.append("None")

   if pre != None and len(pre) > 1:
      desc = str(pre[1])[3:-4]
      #course_description.append(str(pre[1])[3:-4])
   else:
      desc = str(pre[0])[3:-4]
      #course_description.append(str(pre[0]))

   link2 = re.findall(r'<a(.*)<\/a>', desc)
   if link2:
      extracted2 = re.findall(r'([A-Z]+ \d+)', str(link2))
      prgood2 = re.sub(r'<a(.*)<\/a>', str(extracted2), desc)
      if prgood2:
         course_description.append(prgood2.replace('[', '').replace(']', '').replace('"','').replace(',', ''))
   else:
      course_description.append(desc.replace('"', '').replace(',', ''))

stat_df["course_num"] = pd.Series(course_num)
stat_df["title"] = pd.Series(course_title)
stat_df["units"] = pd.Series(course_units)
stat_df["area"] = pd.Series(course_area)
stat_df["terms"] = pd.Series(course_terms)
stat_df["pre"] = pd.Series(course_pre)
stat_df["description"] = pd.Series(course_description)

stat_df.to_csv("datacourses.csv", header=False, index=False)


