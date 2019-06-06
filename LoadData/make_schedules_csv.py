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
Lastnames = []
Alias = []
Title = []
Phone = []
Office	= []
Office_hours = []
Coursenums = []
Courseprof = []

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
        Name.append(n.lower())
        #print(n.split(' '))
        ln = n.split(' ')[0]
        #print(type(ln))
        Lastnames.append(ln.lower())
        prof = ln.lower()
        Alias.append(str(name[1]).lower())
    else:
        Name.append("None")
        Alias.append("None")
        Lastnames.append("None")

    title = re.search('personTitle"(.*)>(.*)<', str(p))
    if title:
        #print(title.group(1))
        Title.append(title.group(2).lower())
    else:
        Title.append("None")

    phone_num = re.search(r'tel:(\+\d+)', str(p))
    if phone_num:
        Phone.append(phone_num.group(1))
    else:
        Phone.append("None")

    office = re.search(r'personLocation"(.*)>(.*)<\/td>', str(p))
    if office:
        Office.append(office.group(2).lower())
    else:
        Office.append("None")

    office_hours = re.search(r'Hours"[\S\s]*?>(.*)<\/td>', str(p))
    if office_hours:
        oh = str(office_hours.group(1))
        oh = oh.replace('</br>', ' ').replace('<br>', ', ')
        nq = re.sub(r'"','', oh)
        if nq:
           oh = nq
           Office_hours.append(nq.lower())
        else:
           Office_hours.append(oh.lower())
    else:
        Office_hours.append("None")

    everything_else = re.findall(r'active"><.*title="(.*)">[\s\S]+?courseSection active">(.*)<\/td>[\s\S]+?title="(.*)"[\s\S]+?title="(.*)">[\s\S]+?Time">(.*)<[\s\S]+?Time">(.*)<[\s\S]+?title="(.*)">(.*)<\/a', str(p))
    if everything_else:
        courses = []
        for i in range(0,8):
           if i != 3 and i != 0:
              courses.append(str(everything_else[0][i]).lower())
           else:
              newstr  = ''.join(everything_else[0][i])
              newstr = newstr.replace(",", '').lower()
              cn = re.search(r'[0-9][0-9][0-9]', newstr)
              if cn:
                 Coursenums.append(cn.group(0).lower())
                 Courseprof.append(prof.lower())
              courses.append(newstr.lower())
              

        #print(type(everything_else[0]))
        #everything_else[0][3] = (newstr)
        Courses.append(courses)
        
        #print(type(everything_else[0]))

    #else :
    #    Courses.append("None")

data = []
data.append(Lastnames)
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

spkey = 0
for l in Courses:
   l.append(spkey)
   l.append(Coursenums[spkey])
   spkey += 1
df_courses = pd.DataFrame(Courses)
df_courses.to_csv("sections.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)
df_c = pd.read_csv("sections.csv")
mystring =  re.search(r'[0-9][0-9][0-9]', str(df_c[df_c.columns[0]]))
df_c["course_num"] = mystring.group(0)
df_c.to_csv("sections.csv", index=False)
#print(df_courses)

cp  = []
keys = []
for s in range(0, len(Coursenums)):
   keys.append(s)
cp.append(Courseprof)
cp.append(Coursenums)
cp.append(keys)
df_cp = pd.DataFrame(cp)
df_cp = df_cp.transpose()
df_cp.to_csv("courseprof.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)
#print(df)

df.to_csv("schedules.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)

syn = pd.read_csv("schedules.csv", error_bad_lines=False)
syns = []

def make_entry(lastname, Syn):
   tmp = []
   tmp.append('faculty')
   tmp.append('faculty_last_name')
   tmp.append(lastname)
   tmp.append(Syn)
   syns.append(tmp)

def make_entry_pr(lastname, Syn):
   tmp = []
   tmp.append('polyratings')
   tmp.append('faculty_last_name')
   tmp.append(lastname)
   tmp.append(Syn)
   syns2.append(tmp)

for index, row in syn.iterrows():
   firstname = str(row[1]).split(' ')[2]
   make_entry(str(row[0]), str(row[0]))
   make_entry(str(row[0]), str(row[1]))
   make_entry(str(row[0]), str(row[2]))
   make_entry(str(row[0]), str("dr." + firstname))
   make_entry(str(row[0]), "professor " + firstname)
   make_entry(str(row[0]), "mr." + firstname)
   make_entry(str(row[0]), "mrs." + firstname)

   make_entry(str(row[0]), "dr." + str(row[0]))
   make_entry(str(row[0]), "professor " + str(row[0]))
   make_entry(str(row[0]), "mr." + str(row[0]))
   make_entry(str(row[0]), "mrs." + str(row[0]))

   make_entry(str(row[0]), "dr." + str(row[1]))
   make_entry(str(row[0]), "professor " + str(row[1]))
   make_entry(str(row[0]), "mr." + str(row[1]))
   make_entry(str(row[0]), "mrs." + str(row[1]))

   make_entry(str(row[0]), firstname)
   
syns_df = pd.DataFrame(syns)
syns_df.to_csv("syn_faculty_2.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)

syns2 = []
syn2 = pd.read_csv("poly_ratings.csv", error_bad_lines=False)
for index, row in syn2.iterrows():
   firstname = str(row[3])
   lastname = str(row[4])
   make_entry_pr(lastname, lastname);
   make_entry_pr(lastname, "dr." + lastname);
   make_entry_pr(lastname, "professor" + lastname);
   make_entry_pr(lastname, lastname +"," + firstname);
   make_entry_pr(lastname, firstname + lastname);
   make_entry_pr(lastname, firstname);
   make_entry_pr(lastname, "professor " + firstname);
   make_entry_pr(lastname, "dr." + firstname + lastname);
   make_entry_pr(lastname, "mr." + firstname + lastname);
   make_entry_pr(lastname, "mrs." + firstname + lastname);
   make_entry_pr(lastname, "professor " + firstname + lastname);

syns2_df = pd.DataFrame(syns2)
syns2_df.to_csv("syn_faculty_3.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)
def isInt(s):
   try: 
      int(s)
      return int(s)
   except ValueError:
      return 0

syns3 = []
syn3 = pd.read_csv("sections.csv", error_bad_lines=False)
def make_entry_cn(Col, Canon, sss):
   tmp = []
   tmp.append('sections')
   tmp.append(Col)
   tmp.append(Canon)
   tmp.append(sss)
   syns3.append(tmp)
   
for index, row in syn3.iterrows():
   cnlist = str(row[0]).split(' ')
   desc = ' '.join(cnlist[4:])
   can = str(cnlist[2])
   if can == 'has':
      continue
   s = ' '
   make_entry_cn('course_num', can, desc)
   make_entry_cn('course_num', can, str(row[0]))
   if isInt(can) >= 500:
      make_entry_cn('course_num', can, desc + " graduate")
      make_entry_cn('course_num', can, desc + " graduate level")
      make_entry_cn('course_num', can, desc + " grad")
      make_entry_cn('course_num', can, desc + " grad level")
      make_entry_cn('course_num', can, "graduate " + desc)
      make_entry_cn('course_num', can, "grad " + desc)
      make_entry_cn('course_num', can, "graduate level " + desc)
      make_entry_cn('course_num', can, "grad level " + desc)
      make_entry_cn('course_num', can, "masters level " + desc)
      make_entry_cn('course_num', can, desc + " masters")

      make_entry_cn('course_num', can, str(row[0]) + " graduate")
      make_entry_cn('course_num', can, str(row[0]) + " graduate level")
      make_entry_cn('course_num', can, str(row[0]) + " grad")
      make_entry_cn('course_num', can, str(row[0]) + " grad level")
      make_entry_cn('course_num', can, "graduate " + str(row[0]))
      make_entry_cn('course_num', can, "grad " + str(row[0]))
      make_entry_cn('course_num', can, "graduate level " + str(row[0]))
      make_entry_cn('course_num', can, "grad level " + str(row[0]))
      make_entry_cn('course_num', can, "masters level " + str(row[0]))
      make_entry_cn('course_num', can, str(row[0]) + " masters")

   make_entry_cn('course_room', str(row[7]) ,str(row[6]))
   make_entry_cn('course_room', str(row[7]) , ' '.join((row[6]).split(' ')[:-3]))
   make_entry_cn('course_room', str(row[7]) , str(row[6]).split(' ')[0])
   make_entry_cn('course_room', str(row[7]) ,''.join(str(row[6]).split(' ')[0:3]))

make_entry_cn( "course_type", "lecture", "lecture")
make_entry_cn( "course_type", "lecture", "lec")
make_entry_cn( "course_type", "laboratory", "laboratory")
make_entry_cn( "course_type", "laboratory", "lab")
make_entry_cn( "course_type", "lecture", "lecs")
make_entry_cn( "course_type", "lecture", "lectures")
make_entry_cn( "course_type", "laboratory", "labs")
make_entry_cn( "course_type", "independent  study", "independent  study" )
make_entry_cn( "course_type", "independent  study", "ind" )
make_entry_cn( "course_type", "activity", "activity" )
make_entry_cn( "course_type", "activity", "activities")
make_entry_cn( "course_type", "intependent study", "independent studies")
make_entry_cn( "course_type", "seminar", "seminar")
make_entry_cn( "course_type", "seminar", "seminars")

make_entry_cn( "course_days", "monday", "monday")
make_entry_cn( "course_days", "monday", "m")
make_entry_cn( "course_days", "monday", "mon")
make_entry_cn( "course_days", "tuesday", "tuesday")
make_entry_cn( "course_days", "tuesday", "t")
make_entry_cn( "course_days", "tuesday", "tues")
make_entry_cn( "course_days", "tuesday", "tu")
make_entry_cn( "course_days", "wednesday", "wednesday")
make_entry_cn( "course_days", "wednesday", "wed")
make_entry_cn( "course_days", "wednesday", "w")
make_entry_cn( "course_days", "thursday", "thurs")
make_entry_cn( "course_days", "thursday", "thursday")
make_entry_cn( "course_days", "thursday", "th")
make_entry_cn( "course_days", "thursday", "tr")
make_entry_cn( "course_days", "friday", "fri")
make_entry_cn( "course_days", "friday", "friday")
make_entry_cn( "course_days", "friday", "f")
make_entry_cn( "course_days", "friday", "fr")
#print(syns3)

syns3_df = pd.DataFrame(syns3)
syns3_df.to_csv("syn_sections_4.csv", index=False, header=False, escapechar=' ', quoting=csv.QUOTE_NONE)

s1 = pd.read_csv("syn_courses_1.csv", error_bad_lines=False)
s2 = pd.read_csv("syn_faculty_3.csv", error_bad_lines=False)
s3 = pd.read_csv("syn_faculty_2.csv", error_bad_lines=False)
s4 = pd.read_csv("syn_sections_4.csv", error_bad_lines=False)
import glob

os.remove("syn_table.csv")
filenames = ['syn_courses_1.csv', 'syn_faculty_2.csv', 'syn_faculty_3.csv', 'syn_sections_4.csv']
with open('result.csv', 'w') as outfile:
   for fname in filenames:
      with open(fname) as infile:
         for line in infile:
            outfile.write(line)

s_table = pd.concat([s1, s2, s3, s4])

df5 = pd.DataFrame(s_table)
df5.drop_duplicates()
df5.to_csv("syn_table.csv", header = False, escapechar=' ', quoting=csv.QUOTE_NONE)
