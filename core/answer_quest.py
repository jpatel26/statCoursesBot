#!/usr/bin/env python3

import logging

import pymysql

from .loader import load_questions

logging.basicConfig(level=logging.INFO)
con = pymysql.connect(host='localhost', user='jpatel26466', passwd='jpatel26db466', db='jpatel26466')
cursor = con.cursor(pymysql.cursors.DictCursor)

df = load_questions()


def answer(aid, var):
    logging.debug(f"AnswerId: {aid}, Variables: {var}")
    if aid == 16:
        clas = var['[TOPIC]'][0]
        for cl in clas:
            if cl in var['[STAT-COURSE]'][0]:
                return 'Yes, you will learn that and much more.'
        return 'Unfortunately not. Check out catalog.calpoly.edu to see what class will teach you that!'

    if aid == 81:
        clas = var['[STAT-COURSE]'][0][0]
        if clas[4] == '5':
            return "That is a graduate level class."
        return "Yes, that is an undergraduate level class."

    q = df.loc[df.answerId == aid, 'query']
    q = q.iloc[0]
    q = str(q)

    if q == 'p' and str(aid) == '12':
        courses = var['[TOPIC]']
        return "Here are some classes: " + ', '.join([x for x in courses[0]])

    if str(aid) == '77':
        return "Sorry, there are no alternatives to that class."

    for key, value in var.items():
        if len(value) > 1:
            for value in value:
                q = q.replace(key, value[0], 1)
        else:
            q = q.replace(key, value[0][0])

    logging.info(f"Executing: {q}")
    cursor.execute(q)  # Executes Query
    c = cursor.fetchall()  # Executes Query
    logging.info(f"Results: {c}")

    ans = df.loc[df.answerId == aid, 'a_primary']

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

    if aid == 24:
        profs = ", ".join([l['faculty_last_name'].capitalize() for l in c])
        ans = "The following teachers teach that course: " + profs

    if aid == 126:
        courses = ''
        for l in c:
            courses = courses + l['course_term']
            ans = "That class is offered during the following terms: " + courses
        return ans

    return ans
