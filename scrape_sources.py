#!/usr/bin/env python

import json
from urllib2 import urlopen
from collections import defaultdict

from bs4 import BeautifulSoup
import dataset

CODE = 'BIOEN'

BASE_URL = "http://www.washington.edu/students/crscat/%s.html" % CODE.lower()

db = dataset.connect('postgresql:///course.db')

soup = BeautifulSoup(urlopen(BASE_URL).read().replace('<BR>', '<p>'))
ps = soup.findAll('p')

# now get only the part with courses
try:
    new_c = str(ps[3])[:str(ps[3]).index('<div id="footer"')]
except ValueError:
    new_c = str(ps[4])[:str(ps[4]).index('<div id="footer"')]
soup = BeautifulSoup(new_c)
ps = soup.findAll('p')

catalog = defaultdict(lambda: defaultdict(str))

for i in range(len(ps) - 2):
    if ps[i].contents[0].next.next.find(CODE) == 0:
        course = str(ps[i].contents[0].next.next).strip()
        name = str(ps[i].contents[0].next.next.next).strip()
        description = str(ps[i + 1]).split('<p>')[1].strip()
        
        ### pre-reqs
        pre_req = []
        pre_req_index = description.find('Prerequisite')
        offered_index = description.find('Offered')
        if pre_req_index > -1:
            pre_req = description[pre_req_index + len('Prerequisite: '): offered_index].split(';')
            description = description[:pre_req_index]
        
        pre_req = [p.strip().replace('.', '') for p in pre_req]
        
        catalog[course] = {'name': name,
                           'description': description,
                           'prerequisite': pre_req}

table = db[CODE.lower] # create a table
for record in catalog:
    table.insert(record)

data_json = json.dumps(catalog, indent=4, sort_keys=True)

print data_json