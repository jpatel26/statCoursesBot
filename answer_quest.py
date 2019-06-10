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
   q = q.replace("[", "~")
   q = q.replace("]", "~")
   q = q.split('~')
   q = q[0] + var + q[2] + ";"
   
   cursor.execute(q)
   c = cursor.fetchall()

   ans = df.loc[df.answerId == qid, 'primary']
   if (len(ans)) > 1:
      ans = ans.loc[0]
   ans = ans.replace("[", "~[")
   ans = ans.replace("]", "]~")
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

answer(1, "stat324")
