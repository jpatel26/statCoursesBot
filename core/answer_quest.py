#!/usr/bin/env python3

import logging

import pymysql

from .loader import load_questions
import re

logging.basicConfig(level=logging.INFO)
con = pymysql.connect(host='localhost', user='jpatel26466', passwd='jpatel26db466', db='jpatel26466')
cursor = con.cursor(pymysql.cursors.DictCursor)

df = load_questions()

def answer(qid, var):
   #print(qid, var)
   if qid == 84:
      course_nums = []
      print(var)
      v = str(var)
      x = re.findall(r'stat(\d+)', v)
      if x:
         for xx in x:
            course_nums.append(int(xx))

      y = re.findall(r'data(\d+)', v)
      if y:
         for yy in y:
            course_nums.append(int(yy))

      course_nums.sort()
      ans = "You should take them in this order: " 
      for c in course_nums:
         ans = ans + str(c) + ", "
      return(ans)

   if qid == 16:
      clas = var['[TOPIC]'][0]
      for cl in clas:
         if cl in var['[STAT-COURSE]'][0]:
             return 'Yes, you will learn that and much more.'
      return 'Unfortunately not. Check out catalog.calpoly.edu to see what class will teach you that!'

   if qid == 81:
      clas = var['[STAT-COURSE]'][0][0]
      if clas[4] == '5':
         return "That is a graduate level class."
      return "Yes, that is an undergraduate level class."

   q = df.loc[df.answerId == qid, 'query']
   q = q.iloc[0]
   q = str(q)
   #print("qis", q)

   
   if q == 'p' and str(qid) == '12':
      courses = var['[TOPIC]']
      return "Here are some classes: " + ', '.join([x for x in courses[0]])
   
   if str(qid) == '77':
      return "Sorry, there are no alternatives to that class."


   for key, value in var.items():
      if len(value) > 1:
         for value in value:
            q = q.replace(key, value[0], 1)
      else:
         q = q.replace(key, value[0][0]) 
  

   #print(q)
   cursor.execute(q) #Executes Query
   c = cursor.fetchall() #Executes Query



   ans = df.loc[df.answerId == qid, 'a_primary']
   
   if (len(ans)) > 1:
      ans = ans.iloc[0]
   

   for key, value in var.items():
      if len(value) > 1:
         for v in value:
            ans = ans.replace(key, value[0], 1)
      else:
         ans = ans.replace(key, value[0][0])

   if 'COURSE-LIST' in ans:
      yee = " ".join(c[0].values())
      ans = ans.replace('[COURSE-LIST]', yee)
      return ans

   for key, value in c[0].items():
      key = key.upper()
      key = key.replace("_", "-")
      key = "[" + key + "]"
      ans = ans.replace(key, value)

   if qid == 24:
      print(c)
      profs = ""
      for l in c:
         profs = profs + l['faculty_last_name'] + ", "
      ans = "The following teachers teach that course: " + profs.title()

   if qid == 126 or qid == 104:
      courses = ''
      for l in c:
         courses = courses + l['course_term'] 
         ans = "That class is offered during the following terms: " + courses
      return ans

      
      
   return ans 
