""" from itertools import product
from pprint import pprint
import shelve
from urllib.parse import urlparse

from bs4 import BeautifulSoup

url = "https://www.animecenterbr.com/youkoso-jitsuryoku-light-novel-pt-br/"


with shelve.open("pages") as db:
    soup = BeautifulSoup(db.get(urlparse(url).path), features='html.parser')

    titles = soup.select('.post-text-content > :is(h3, span, strong, p)')

    for title in titles:
        print(title.get_text(strip=True))

 """

import mimetypes

mimetypes.add_type('image/webp', '.webp')

type = mimetypes.guess_extension(None)

print(type)
