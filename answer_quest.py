import re
import pandas as pd
import pymysql

con = pymysql.connect(host = 'localhost', user = 'jpatel26466', passwd = 'jpatel26db466', db = 'jpatel26466')
cursor = con.cursor(pymysql.cursors.DictCursor)

#cursor.execute("select * from centroids;")
#c = cursor.fetchall()

df = pd.read_csv('bot_questions.csv')

def answer(qid, var):
   #[0, 1, 2, 3, 24, 25, 26, 28, 29, 30, 31, 32, 33]

   q = df.loc[qid, 'query']
   q = q.replace("[", "~")
   q = q.replace("]", "~")
   q = q.split('~')
   q = q[0] + var + q[2]
   
   cursor.execute(q)
   c = cursor.fetchall()

   ans = df.loc[qid, 'primary']
   ans = ans.replace("[", "~")
   ans = ans.replace("]", "~")
   ans = ans.split('~')
   
   fin = []

   for i in range(len(ans)):
      if i % 2 == 0:
         fin.append(ans[i])
      elif i == 1:
         fin.append(var)
      else:
         fin.append("\"")
         fin.append(list(c[0].values())[0])
         fin.append("\"")
   
   fin = "".join(fin)
   print(fin)

 
   
answer(48, "stat331")
