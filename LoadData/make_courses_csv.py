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

resp = requests.get("http://catalog.calpoly.edu/coursesaz/stat/")
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
   number = "stat" + tmp_title.replace(",",'').lower()
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

stat_df.to_csv("courses.csv", index=False, header=False)

syn = pd.read_csv("courses.csv")
syns = []

def make_entry(Canon, Syn):
   tmp = []
   tmp.append('courses')
   tmp.append('course_num')
   tmp.append(str(Canon))
   tmp.append(Syn)
   if (str(Syn).isspace()):
      return
   syns.append(tmp)

for index, row in syn.iterrows():
   tmp = []
   text = str(''.join([i for i in str(row[6]) if not i.isdigit()]).replace('lectures',''))
   cleantext = re.search(r'([\s\S]+?)Not[\s\S]+?\.', text)
   if cleantext:
      text = cleantext.group(1)
   cleantext = re.search(r'([\s\S]+?)Fulfills[\s\S]+?\.', text)
   if cleantext:
      text = cleantext.group(1)
   cleantext = re.search(r'([\s\S]+?)Total[\s\S]+?\.', text)
   if cleantext:
      text = cleantext.group(1)

   make_entry(row[0], text.lower().replace('.','')) # add course descriptions

   number = str(row[0])[4:]
   make_entry(row[0], "stat " + (number + " " + str(row[1])))
   make_entry(row[0], "stat " + (str(row[1]) + " " + number))
   make_entry(row[0], "stat " + number)
   make_entry(row[0], "stat " + (str(row[1])))
   make_entry(row[0], "stat" + (number + " " + str(row[1])))
   make_entry(row[0], "stat" + (str(row[1]) + " " + number))
   make_entry(row[0], "stat" + number)
   make_entry(row[0], "stat" + (str(row[1])))
   make_entry(row[0], (number + " " + str(row[1])))
   make_entry(row[0], (str(row[1]) + " " + number))
   make_entry(row[0], number)
   make_entry(row[0], (str(row[1])))

   if str(row[1])[-2:] == "ii":
      row[1] = str(row[1]).replace("ii", "2")
      make_entry(row[0], "stat " + (number + " " + str(row[1])))
      make_entry(row[0], "stat " + (str(row[1]) + " " + number))
      make_entry(row[0], "stat " + (str(row[1])))
      make_entry(row[0], "stat" + (number + " " + str(row[1])))
      make_entry(row[0], "stat" + (str(row[1]) + " " + number))
      make_entry(row[0], "stat" + (str(row[1])))
      make_entry(row[0], (number + " " + str(row[1])))
      make_entry(row[0], (str(row[1]) + " " + number))
      make_entry(row[0], (str(row[1])))
   elif str(row[1])[-1] == "i":
      row[1] = str(row[1])[:-1] + "1"
      make_entry(row[0], "stat " + (number + " " + str(row[1])))
      make_entry(row[0], "stat " + (str(row[1]) + " " + number))
      make_entry(row[0], "stat " + (str(row[1])))
      make_entry(row[0], "stat" + (number + " " + str(row[1])))
      make_entry(row[0], "stat" + (str(row[1]) + " " + number))
      make_entry(row[0], "stat" + (str(row[1])))
      make_entry(row[0], (number + " " + str(row[1])))
      make_entry(row[0], (str(row[1]) + " " + number))
      make_entry(row[0], (str(row[1])))


   if int(str(row[0])[4:]) >= 500:
      make_entry(row[0], "graduate stat " + (number + " " + str(row[1])))
      make_entry(row[0], "grad stat " + (str(row[1]) + " " + number))
      make_entry(row[0], "grad level stat " + number)
      make_entry(row[0], "graduate level stat " + (str(row[1])))
      make_entry(row[0], "masters level stat " + (number + " " + str(row[1])))
      make_entry(row[0], "stat" + (str(row[1]) + " " + number + " grad level"))
      make_entry(row[0], "stat" + number + " for grad students")
      make_entry(row[0], "stat" + (str(row[1])) + " graduate level")
      make_entry(row[0], (number + " " + str(row[1]))+ " for grads")
      make_entry(row[0], (str(row[1]) + " " + number + " for graduates"))
      make_entry(row[0], number)
      make_entry(row[0], (str(row[1]))+ " for graduate students")

syns.append(['courses', 'term','sp', 'this quarter'])
syns.append(['courses', 'term','su', 'next quarter'])
syns.append(['courses', 'term','sp', 'now'])
syns.append(['courses', 'term','su', 'next summer'])
syns.append(['courses', 'term','f', 'next fall'])
syns.append(['courses', 'term','w', 'next winter'])
syns.append(['courses', 'term','sp', 'next spring'])
syns.append(['courses', 'term','sp', 'today'])

syns.append(['courses', 'term', 'w', 'w'])
syns.append(['courses', 'term','w', 'winter'])
syns.append(['courses', 'term','w', 'w19'])
syns.append(['courses', 'term','w', 'w18'])
syns.append(['courses', 'term','w', 'winter18'])
syns.append(['courses', 'term','w', 'winter19'])
syns.append(['courses', 'term','w', 'winter20'])
syns.append(['courses', 'term','w', 'w20'])
syns.append(['courses', 'term','w', 'winter quarter'])
syns.append(['courses', 'term','w', 'q'])

syns.append(['courses', 'term','f', 'f'])
syns.append(['courses', 'term','f', 'fall'])
syns.append(['courses', 'term','f', 'f19'])
syns.append(['courses', 'term','f', 'f18'])
syns.append(['courses', 'term','f', 'f20'])
syns.append(['courses', 'term','f', 'fall19'])
syns.append(['courses', 'term','f', 'fall20'])
syns.append(['courses', 'term','f', 'fall18'])
syns.append(['courses', 'term','f', 'fall quarter'])

syns.append(['courses', 'term','sp', 'sp'])
syns.append(['courses', 'term','sp', 's'])
syns.append(['courses', 'term','sp', 'spring'])
syns.append(['courses', 'term','sp', 'sp19'])
syns.append(['courses', 'term','sp', 'sp18'])
syns.append(['courses', 'term','sp', 'sp20'])
syns.append(['courses', 'term','sp', 'spring19'])
syns.append(['courses', 'term','sp', 'spring20'])
syns.append(['courses', 'term','sp', 'spring18'])
syns.append(['courses', 'term','sp', 'spring quarter'])

syns.append(['courses', 'term','su', 'su'])
syns.append(['courses', 'term','su', 'summerq'])
syns.append(['courses', 'term','su', 'summer'])
syns.append(['courses', 'term','su', 'su19'])
syns.append(['courses', 'term','su', 'su18'])
syns.append(['courses', 'term','su', 'su20'])
syns.append(['courses', 'term','su', 'summer19'])
syns.append(['courses', 'term','su', 'summer20'])
syns.append(['courses', 'term','su', 'summer18'])
syns.append(['courses', 'term','su', 'summer quarter'])

syns.append(['courses', 'course_area', 'ge area b1', 'b1'])  
syns.append(['courses', 'course_area', 'ge area b1', 'areab1'])  
syns.append(['courses', 'course_area', 'ge area b1', 'geb1'])  
syns.append(['courses', 'course_area', 'ge area b1', 'ge b1'])  
syns.append(['courses', 'course_area', 'ge area b1', 'ge area b1'])  
syns.append(['courses', 'course_area', 'ge area b1', 'area b1'])  
syns.append(['courses', 'course_area', 'ge area b1', 'b1'])  
syns.append(['courses', 'course_area', 'ge area b6', 'b6'])  
syns.append(['courses', 'course_area', 'ge area b6', 'areab6'])  
syns.append(['courses', 'course_area', 'ge area b6', 'geb6'])  
syns.append(['courses', 'course_area', 'ge area b6', 'ge b6'])  
syns.append(['courses', 'course_area', 'ge area b6', 'ge area b6'])  
syns.append(['courses', 'course_area', 'ge area b6', 'area b6'])  
syns.append(['courses', 'course_area', 'cr/nc', 'credit no credit'])  
syns.append(['courses', 'course_area', 'cr/nc', 'cr no cr'])  
syns.append(['courses', 'course_area', 'cr/nc', 'credit'])  
syns.append(['courses', 'course_area', 'cr/nc', 'no credit or credit'])  
syns.append(['courses', 'course_area', 'cr/nc', 'pass or fail'])  
syns.append(['courses', 'course_area', 'cr/nc', 'pass/fail'])

# Should this be to class nums like 300, 400, 500?
syns.append(['unknown', 'course_level', 'first_year', 'first year']) 
syns.append(['unknown', 'course_level', 'first_year', '1st year']) 
syns.append(['unknown', 'course_level', 'first_year', 'freshman']) 
syns.append(['unknown', 'course_level', 'second_year', 'second year']) 
syns.append(['unknown', 'course_level', 'second_year', '2nd year']) 
syns.append(['unknown', 'course_level', 'second_year', 'sophomore']) 
syns.append(['unknown', 'course_level', 'third_year', 'third year']) 
syns.append(['unknown', 'course_level', 'third_year', '3rd year']) 
syns.append(['unknown', 'course_level', 'third_year', 'junior']) 
syns.append(['unknown', 'course_level', 'fourth_year', 'fourth year']) 
syns.append(['unknown', 'course_level', 'fourth_year', '4th year']) 
syns.append(['unknown', 'course_level', 'fourth_year', 'senior']) 
syns.append(['unknown', 'course_level', 'graduate', 'fifth year']) 
syns.append(['unknown', 'course_level', 'graduate', 'graduate']) 
syns.append(['unknown', 'course_level', 'graduate', 'grad']) 
syns.append(['unknown', 'course_level', 'graduate', 'masters']) 
syns.append(['unknown', 'course_level', 'graduate', 'sixth year']) 
syns.append(['unknown', 'course_level', 'graduate', '5th year']) 
syns.append(['unknown', 'course_level', 'graduate', '6th year']) 

syns_df = pd.DataFrame(syns)
syns_df.to_csv("syn_courses_1.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)


dsyn = pd.read_csv("datacourses.csv", header=None)
dsyns = []
def dmake_entry(Canon, Syn):
   tmp = []
   tmp.append('datacourses')
   tmp.append('course_num')
   tmp.append(Canon)
   tmp.append(Syn)
   if (str(Syn).isspace()):
      return
   dsyns.append(tmp)

for index, row in dsyn.iterrows():
   tmp = []
   text = str(''.join([i for i in str(row[6]) if not i.isdigit()]).replace('lectures',''))
   cleantext = re.search(r'([\s\S]+?)Not[\s\S]+?\.', text)
   if cleantext:
      text = cleantext.group(1)
   cleantext = re.search(r'([\s\S]+?)Fulfills[\s\S]+?\.', text)
   if cleantext:
      text = cleantext.group(1)
   cleantext = re.search(r'([\s\S]+?)Total[\s\S]+?\.', text)
   if cleantext:
      text = cleantext.group(1)

   number = str(row[0])[4:]
   dmake_entry(row[0], text.lower().replace('.','')) # add course descriptions

   dmake_entry(row[0], "data" + number)
   dmake_entry(row[0], "data" + (str(row[1])))
   dmake_entry(row[0], (number + " " + str(row[1])))
   dmake_entry(row[0], (str(row[1]) + " " + number))
   dmake_entry(row[0], number)
   dmake_entry(row[0], (str(row[1])))

   if str(row[1])[-2:] == "ii":
      row[1] = str(row[1]).replace("ii", "2")
      dmake_entry(row[0], (number + " " + str(row[1])))
      dmake_entry(row[0], (str(row[1]) + " " + number))
      dmake_entry(row[0], (str(row[1])))
   elif str(row[1])[-1] == "i":
      row[1] = str(row[1])[:-1] + "1"
      dmake_entry(row[0], (number + " " + str(row[1])))
      dmake_entry(row[0], (str(row[1]) + " " + number))
      dmake_entry(row[0], (str(row[1])))

dsyns_df = pd.DataFrame(dsyns)
dsyns_df.to_csv("syn_courses_6.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)

