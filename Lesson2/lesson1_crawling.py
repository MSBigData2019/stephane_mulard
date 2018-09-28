# coding: utf-8

import requests
from bs4 import BeautifulSoup

url = "http://www.purepeople.fr/rechercher"

#res = requests.get(url)
res = requests.post(url, data = {'q','macron'})

if res.status_code == 200:
    htmldoc = res.text
    # print(htmldoc)
    soup = BeautifulSoup(htmldoc, 'html.parser')
    specific_class = "c-article-flux__title"
    all_links =  list(map(lambda x : x['href'], soup.find_all('a', class_=specific_class)))
    print all_links



