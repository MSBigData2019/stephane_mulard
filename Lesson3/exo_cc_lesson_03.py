# coding: utf-8

import requests
import unittest
import re
import pandas as pd
from bs4 import BeautifulSoup
import json
import numpy as np
import time
import concurrent.futures
import urllib.request

# API Google Map
url_api = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
url_villes = "https://www.insee.fr/fr/statistiques/1906659?sommaire=1906743"

API_KEY = open("tokenMap.txt", "r").read()

def get_request_from_url_and_build_soup(url):
    request = requests.get(url)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding : " + str(request.status_code))


def get_request_from_url_and_build_json(url, body):
    request = requests.post(url+API_KEY, data=body)
    if request.status_code == 200:
        jsonObject = json.loads(request.text)
        return jsonObject
    else:
        print("erreur requête json : ", str(request.status_code), request.text)
        return


#Matrice distance entre les 50 plus grandes villes de France


soup = get_request_from_url_and_build_soup(url_villes)

tblvilles = soup.find(id="produit-tableau-T16F014T4")

df = pd.read_html(str(tblvilles))[0]
print(df.head())

# 50 plus grandes villes
df2 = df.iloc[:50]



body = r"{  'locations': [ 'Paris, Fr','Marseilles','Lyon'], " \
       r"'options': {'allToAll': true}}"

# http://developer.mapquest.com/documentation/directions-api/route-matrix/post/
test = get_request_from_url_and_build_json(url_api, body)

matrix = np.array(test['distance'])

print(matrix)
