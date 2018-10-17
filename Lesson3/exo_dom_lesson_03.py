# coding: utf-8

import requests
import unittest
import re
import pandas as pd
from bs4 import BeautifulSoup
import json
from requests.auth import HTTPBasicAuth

url = "https://gist.github.com/paulmillr/2657075"

def get_request_from_url_and_build_soup(url):
    request = requests.get(url)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding : " + str(request.status_code))


def get_request_from_url_and_build_json(url):
    headers = {'Authorization' : 'token 9597e64b1c0c976a0cb925c070421b85464800a5'}
    request = requests.get(url, headers=headers)
    jsonObject = json.loads(request.text)
    return jsonObject


soup = get_request_from_url_and_build_soup(url)

info = soup.find_all("th", text=re.compile("#[0-9]"))

info[0].findNext("a").get_text()
info[0].findNext("td").get_text().split("(")


all_links = [list(map(lambda x : x.get_text()[1:] , info)),
             list(map(lambda x : x.findNext("a").attrs['href'] , info)),
             list(map(lambda x: x.findNext("a").get_text(), info))
             #list(map(lambda x: x.findNext("td").get_text(), test))
             ]

df = pd.DataFrame(all_links)
df=df.T

# for link in df[1]:
#     #print(link)
#     soup2 = get_request_from_url_and_build_soup(link)
#     nbstar = soup2.find(title="Stars").findNext("span").get_text().strip()
#     print(nbstar)

url_api_profile = 'https://api.github.com/users/fabpot/repos'

def get_starcount (url_api):
    response_object = get_request_from_url_and_build_json(url_api)
    nbstar = 0
    if len(response_object)!= 0:
        for dico in response_object:
           nbstar = nbstar + dico['stargazers_count']
        return nbstar, nbstar / len(response_object)
    else:
        # cas de 0 repository
        return 0, 0

liststar = []
listmoy = []

for name in df[2]:
    linkApi = "https://api.github.com/users/" + name + "/repos?per_page=100"
    print(linkApi)
    total_star, moy_star = get_starcount(linkApi)
    liststar.append(total_star)
    listmoy.append(moy_star)

df['Total star'] = liststar
df['Average'] = listmoy