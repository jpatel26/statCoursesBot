import re
import pandas as pd
import pymysql

con = pymysql.connect(host = 'localhost', user = 'jpatel26466', passwd = 'jpatel26db466', db = 'jpatel26466')
cursor = con.cursor(pymysql.cursors.DictCursor)

#cursor.execute("select * from centroids;")
#c = cursor.fetchall()

df = pd.read_csv('bot_questions.csv')

def resolve(l):
   li = [int(i[-3:]) for i in l]
   li.sort()
   return "stat" + str(li[0])


def answer(qid, var):


   q = df.loc[df.answerId == qid, 'query']
   if (len(q)) > 1:
      q = q.loc[0]
   q = str(q)

   for key, value in var.items():
      if len(value) > 1:
         for value in value:
            q = q.replace(key, value[0], 1)
      else:
         q = q.replace(key, value[0][0])
      
   q = q + ";"
   
   cursor.execute(q)
   c = cursor.fetchall()

   ans = df.loc[df.answerId == qid, 'primary']
   if (len(ans)) > 1:
      ans = ans.loc[0]
   
   for key, value in var.items():
      if len(value) > 1:
         for value in value:
            ans = ans.replace(key, value[0], 1)
      else:
         ans = ans.replace(key, value[0][0])


   for key, value in c[0].items():
      key = key.upper()
      key = key.replace("_", "-")
      key = "[" + key + "]"
      ans = ans.replace(key, value)
   
   print(ans)

answer(1, {"[STAT-COURSE]": [["stat324"]]})
