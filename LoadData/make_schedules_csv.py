import pandas as pd
import sys
import os
from bs4 import BeautifulSoup
import requests
import time
import urllib.request
import re
import csv

stat_df = pd.DataFrame()
Name = []
Alias = []
Title = []
Phone = []
Office	= []
Office_hours = []

Courses = []


resp = requests.get("http://schedules.calpoly.edu/depts_76-CSM_curr.htm")
soup = BeautifulSoup(resp.content, 'html.parser')
div = soup.find("div", {"id" : "content"})
table = div.find("table", {"id" : "listing"})
trs = table.find_all("tr")
x = re.search(r'CSM-Statistics<([\s\S]*)CSM-Mathematics', str(trs))
if x:
    people_block = x.group(1)
else:
    print("Error")
people = re.findall(r'<tr>([\s\S]+?)<\/tr>', str(people_block))
for p in people:
    #print("Person")
    #print(p)
    name = re.findall(r'curr.htm">(.*)<\/a', str(p))
    if name:
        #print("Name: " + name[0] + " Username: " + name[1])
        n = str(name[0]).replace(",", '');
        Name.append(n)
        Alias.append(name[1])
    else:
        Name.append("None")
        Alias.append("None")

    title = re.search('personTitle"(.*)>(.*)<', str(p))
    if title:
        #print(title.group(1))
        Title.append(title.group(2))
    else:
        Title.append("None")

    phone_num = re.search(r'tel:(\+\d+)', str(p))
    if phone_num:
        Phone.append(phone_num.group(1))
    else:
        Phone.append("None")

    office = re.search(r'personLocation"(.*)>(.*)<\/td>', str(p))
    if office:
        Office.append(office.group(2))
    else:
        Office.append("None")

    office_hours = re.search(r'Hours"[\S\s]*?>(.*)<\/td>', str(p))
    if office_hours:
        oh = str(office_hours.group(1))
        oh = oh.replace('</br>', ' ').replace('<br>', ', ')
        nq = re.sub(r'"','', oh)
        if nq:
           oh = nq
           Office_hours.append(nq)
        else:
           Office_hours.append(oh)
    else:
        Office_hours.append("None")

    everything_else = re.findall(r'active"><.*title="(.*)">[\s\S]+?courseSection active">(.*)<\/td>[\s\S]+?title="(.*)"[\s\S]+?title="(.*)">[\s\S]+?Time">(.*)<[\s\S]+?Time">(.*)<[\s\S]+?title="(.*)">(.*)<\/a', str(p))
    if everything_else:
        courses = []
        for i in range(0,8):
           if i != 3 and i != 0:
              courses.append(everything_else[0][i])
           else:
              newstr  = ''.join(everything_else[0][i])
              newstr = newstr.replace(",", '')
              courses.append(newstr)
              

        #print(type(everything_else[0]))
        #everything_else[0][3] = (newstr)
        Courses.append(courses)
        
        #print(type(everything_else[0]))

    #else :
    #    Courses.append("None")

data = []
data.append(Name)
data.append(Alias)
data.append(Title)
data.append(Phone)
data.append(Office)
data.append(Office_hours)
#data.append(Courses)
df = pd.DataFrame(data)
df = df.transpose()
df = df[df[0] != "None"]

#print(Courses)
df_courses = pd.DataFrame(Courses)
df_courses.to_csv("sections.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)
#print(df_courses)

#print(df)

df.to_csv("schedules.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)
