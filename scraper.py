#!/usr/bin/env python

# spits out a list of majors

from urllib2 import urlopen

from bs4 import BeautifulSoup

URL = "http://www.washington.edu/uaa/advising/majors/majoff.php"

soup = BeautifulSoup(urlopen(URL).read())

divs = soup.find("div", {"id": "content"})
sub_divs = divs.findChildren('div')

for s in sub_divs[7:]:
    print s.text.strip()