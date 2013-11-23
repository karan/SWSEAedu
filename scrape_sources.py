#!/usr/bin/env python

import json
import re
from urllib2 import urlopen
from collections import defaultdict
from itertools import chain

from bs4 import BeautifulSoup

CODE = 'CSE'

BASE_URL = "http://www.washington.edu/students/crscat/%s.html" % CODE.lower()

def sanitize(ps):
    new_ps = []
    for i in range(len(ps) - 2):
            row = str(ps[i].contents[0].next.next)
            if row.find('<b>') != 0 and row.find('<i>') != 0 and row.find('Instructor') != 0 and row != '\n' and row != '':
                new_ps.append(ps[i])
    return new_ps

soup = BeautifulSoup(urlopen(BASE_URL).read().replace('<BR>', '<p>'))
ps = soup.findAll('p')

# now get only the part with courses
try:
    new_c = str(ps[3])[:str(ps[3]).index('<div id="footer"')]
except ValueError:
    new_c = str(ps[4])[:str(ps[4]).index('<div id="footer"')]
soup = BeautifulSoup(new_c)
ps = soup.findAll('p')

ps = sanitize(ps)

catalog = defaultdict(dict)

#for i in range(len(ps) - 2):
for i in range(4, 6):
    #if ps[i].contents[0].next.next.find(CODE) == 0:
        course = str(ps[i].contents[0].next.next).strip()
        name = str(ps[i].contents[0].next.next.next).strip()
        description = str(ps[i]).split('<p>')[2].strip()
        
        ### pre-reqs
        pre_req = [] # all pre reqs
        hard_req = [] # non-optional pre-reqs
        choice_req = [] # either/or pre-reqs
        other_req = [] # everything else
        
        choice_pattern = re.compile(r'.*(either|)(.*) or (.*)')
        hard_req_pattern = re.compile(r'.{2,6} [0-9]{3}')
        
        pre_req_index = description.lower().find('Prerequisite'.lower())
        offered_index = description.lower().find('Offered'.lower())
        
        new_description = description[:pre_req_index].strip()
        
        if pre_req_index != -1: # there are some pre reqs
            pre_req_string = description[pre_req_index + len('Prerequisite: '): offered_index]
            pre_req = pre_req_string.split(';') # all pre-reqs
            pre_req = [p.strip().replace('.', '') for p in pre_req]
            
            for pre in pre_req:
                if 'Recommended'.lower() in pre.lower() or 'concurrent' in pre.lower() or 'permission of instructor' in pre.lower():
                    other_req.append(pre)
                else:
                    match = re.search(choice_pattern, pre)
                    if not match:
                        # it's a hard requirement, or something else
                        match2 = re.search(hard_req_pattern, pre)
                        if match2:
                            # it's a hard requirement
                            hard_req.append(pre)
                        else:
                            # it's something else
                            other_req.append(pre)
                    else:
                        courses = match.groups()
                        c = [course.split(',') for course in courses]
                        c = list(chain.from_iterable(c)) # flatten the list
                        c = [course for course in c if course not in ['either', 'or']]
                        choice_req.append([course.strip() for course in c if len(course) > 3])
                #pre_req.remove(pre)
        
        catalog[course] = {
            'name': name,
            'description': new_description,
            'hard_req': hard_req,
            'choice_req': choice_req,
            'other_req': other_req, 
            'i': i
            }

data_json = json.dumps(catalog, indent=4, sort_keys=True)

print data_json