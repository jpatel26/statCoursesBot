#!/usr/bin/env python3
import re
import random
import string
import warnings

import numpy as np

from .loader import load_synonym_table, load_questions
import pymysql

con = pymysql.connect(host = 'localhost', user = 'jpatel26466', passwd = 'jpatel26db466', db = 'jpatel26466')
cursor = con.cursor(pymysql.cursors.DictCursor)


df = load_questions()


def answer(qid, var):
   #print(qid, var)

   q = df.loc[df.answerId == qid, 'query']
   q = q.iloc[0]
   q = str(q)
   #print("qis", q)

   
   if q == 'p' and str(qid) == '12':
      courses = var['[TOPIC]']
      return "Here are some classes: " + ', '.join([x for x in courses[0]])
   

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


   for key, value in c[0].items():
      key = key.upper()
      key = key.replace("_", "-")
      key = "[" + key + "]"
      ans = ans.replace(key, value)

   if qid == 24:
      profs = ""
      for l in c:
         profs = profs + l['faculty_last_name'] + ", "
      ans = "The following teachers teach that course: " + profs
      
      
   return ans 
