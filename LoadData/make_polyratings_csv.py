import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from numpy import random
import warnings
warnings.filterwarnings("ignore")
with open('data301.txt', 'r') as f:
    read_data = f.readlines()
i = 0
d = {}
lis = []
while i < len(read_data):
    l = ((read_data[i].strip() + " " + read_data[i + 1]).strip()).split()
    try:
        lis.append({'last': l[0].lower().strip(','),
                    'first': l[1].lower(),
                    'rating': float(l[2]),
                    'department': l[3],
                    'evals': int(l[4])})
    except:
        if l[2] == 'N/A':
            lis.append({'last': l[0].lower().strip(','),
                        'first': l[1].lower(),
                        'rating': l[2],
                        'department': l[3],
                        'evals': int(l[4])})
        elif "," in l[0]:
            lis.append({'last': l[0].lower().strip(','),
                        'first': l[1].lower() + " " + l[2].lower(),
                        'rating': float(l[3]),
                        'department': l[4],
                        'evals': (l[4:])})
        else:
            try:
                lis.append({'last': l[0].lower() + " " + l[1].lower().strip(','),
                            'first': l[2].lower(),
                            'rating': float(l[3]),
                            'department': l[4],
                            'evals': l[4:]})
            except:
                lis.append({'last': l[0].lower() + " " + l[1].lower().strip(','),
                            'first': l[2].lower() + " " + l[3].lower(),
                            'rating': float(l[4]),
                            'department': l[5],
                            'evals': l[5:]})
    i += 2
    if lis[-1]['evals'] == ['evals']:
        lis[-1]['evals'] = int(lis[-1]['rating'])
        lis[-1]['department'] = 'N/A'
        lis[-1]['rating'] = float(lis[-1]['first'][-4:])
        lis[-1]['first'] = lis[-1]['first'][:-5]
data = pd.DataFrame(lis)
data = data.drop(data.index[1949])
data = data.reset_index()
data = data.drop('index', axis = 1)
data['evals'] = data['evals'].apply(lambda x: int(x[1]) if type(x) == list else int(x))
data.to_csv('ratings.csv')

url = ("polyratings.com/list.php")
r  = requests.get("http://" +url)
da = r.text
soup = BeautifulSoup(da, 'lxml')
l = [link.get('href') for link in soup.find_all('a')[7:-5]]
del l[1949]


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def df(n):
    page = requests.get(l[n])
    page.content
    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    p = list(body.children)[7]
    s = p.get_text()
    s = s.split('\n\n\n')
    d = []
    for i in s:
        if "Freshman" in i or "Sophomore" in i or "Junior" in i or "Senior" in i or 'Grad' in i:
            j = s.index(i)
            break
    while j < len(s) - 2:
        s[j] = s[j].strip().split('\n')
        if (has_numbers(s[j][0]) or s[j] == ['']) and ("Senior" not in s[j][0]):
            j += 1
            continue
        if "\n\n" in s[j + 1]:
            s[j + 1] = s[j + 1][:s[j + 1].index('\n\n')]
        d.append({'year': s[j][0],
                  'comment': s[j + 1],
                  'grade': s[j][1],
                  'requirement': s[j][2],
                  'date': s[j][3]})
        j += 2
    return pd.DataFrame(d)

def grade_req_year(n):
    dataa = df(n)
    tot = len(dataa)
    y = ["N/A", "Freshman", "Sophomore", "Junior", "Senior", "5th Year Senior", "6th Year Senior"]
    cu = 0
    maj = 0
    sup = 0
    el = 0
    gen = 0
    lets = ['A', 'B', 'C', 'D', 'F']
    g = [90, 80, 70, 60, 50]
    avg = []
    for i in range(len(dataa)):
        if dataa.iloc[i]['year'] == "Graduate Student" or dataa.iloc[i]['requirement'] == "N/A":
            tot -= 1
        else:
            cu += y.index(dataa.iloc[i]['year'])
        if "Maj" in dataa.iloc[i]['requirement']:
            maj += 1
        elif "Support" in dataa.iloc[i]['requirement']:
            sup += 1
        elif "Elec" in dataa.iloc[i]['requirement']:
            el += 1
        else:
            gen += 1
        if dataa.iloc[i]['grade'] in lets:
            avg.append(g[lets.index(dataa.iloc[i]['grade'])])
    try:
        a = lets[g.index(int(sum(avg) / len(avg) // 10) * 10)]
        b = (sum(avg) / len(avg))
    except:
        a = "N/A"
        b = 'N/A'
    data.loc[n, 'avg grade'] = a
    data.loc[n, 'avg grade num'] = b
    try:
        #data.loc[n, "proportion major"] = maj / len(dataa)
        #data.loc[n, "proportion support"] = sup / len(dataa)
        #data.loc[n, "proportion elective"] = el / len(dataa)
        #data.loc[n, "proportion gen ed"] = gen / len(dataa)
        data.loc[n, "average year"] = cu / tot
    except:
        #data.loc[n, "proportion major"] = None
        #data.loc[n, "proportion support"] = None
        #data.loc[n, "proportion elective"] = None
        #data.loc[n, "proportion gen ed"] = None
        data.loc[n, "average year"] = None

def college_dept(n):
    csm = ['CHEM', 'MATH', 'BIO', 'PHYS', 'STAT', 'EDUC', 'LS', 'PE', 'SCI']
    ceng = ['AERO', 'EE', 'CSC', 'IME', 'CE', 'ME', 'MATE', 'CPE', 'BMED', 'ENGR']
    caed = ['ARCH', 'ARCE', 'LA', 'CM', 'CRP']
    cafes = ['AGB', 'ASCI', 'FSN', 'DSCI', 'SS', 'NRM', 'BRAE', 'AGED', 'CRSC', 'EHS', 'GBA']
    ocob = ['IT', 'BUS', 'ECON']
    cla = ['PHIL', 'ENGL', 'ART', 'SOC', 'JOUR', 'POLS', 'TH', 'MU', 'COMS', 'HIST', 'PSY', 'GRC',
          'ES', 'MSC', 'HUM', 'WS', 'WGS', 'LIB']
    dept = data['department'][n]
    if dept in csm:
        data.loc[n, 'college'] = "COSAM"
    elif dept in ceng:
        data.loc[n, 'college'] = "CENG"
    elif dept in caed:
        data.loc[n, 'college'] = "CAED"
    elif dept in cafes:
        data.loc[n, 'college'] = "CAFES"
    elif dept in ocob:
        data.loc[n, 'college'] = "OCOB"
    elif dept in cla:
        data.loc[n, 'college'] = "CLA"
    else:
        data.loc[n, 'college'] = "N/A"

#This cell takes a few minutes to run
np.random.seed(100)
r = random.randint(0, len(data), 1300)
for n in r:
    grade_req_year(n)
    college_dept(n)
sub = data.iloc[r]
sub = sub[sub.rating != 'N/A']
sub = sub[sub['avg grade'] != 'N/A']
sub = sub[sub['college'] != 'N/A']
sub = sub[sub['average year'] != None]
sub = sub[sub['department'] != "SCI"]
sub = sub[sub['department'] != "MSC"]
sub['rating'] = sub['rating'].apply(lambda x: float(x))
sub = sub.reset_index()
sub = sub.drop('index', axis = 1)

#cols = ['department', 'evals', 'first', 'last', 'rating', 'avg grade', 'avg grade num', 'proportion major',
#        'proportion support', 'proportion elective', 'proportion gen ed', 'average year', 'college']
cols = ['department', 'evals', 'first', 'last', 'rating', 'avg grade', 'avg grade num', 'average year', 'college']
assert (list(sub.columns)) == cols
assert (sub['avg grade'].dtype) == object
#assert (sub['proportion major'].dtype) == float
#assert (sub['proportion support'].dtype) == float
#assert (sub['proportion elective'].dtype) == float
#assert (sub['proportion gen ed'].dtype) == float
assert (sub['average year'].dtype) == float
assert sub['college'].dtype == object
assert sub['department'].dtype == object
assert sub['evals'].dtype == int
assert sub['first'].dtype == object
assert sub['last'].dtype == object
assert sub['rating'].dtype == float

sub = sub.loc[sub['department'] == 'STAT']
sub.to_csv('poly_ratings.csv', header=False, index=False)
