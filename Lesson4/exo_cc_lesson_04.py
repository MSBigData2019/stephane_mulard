# coding: utf-8
# construire une base propre de conditionnement pour chaque vendeurs
# open medicaments
# extraire dosage, forme galénique, nb gélule... pour calculer un équivalent traitement

url_api = "https://www.open-medicaments.fr/api/v1/medicaments?query=paracetamol&limit=100"

import requests
import unittest
import re
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
import concurrent.futures
import urllib.request
from multiprocessing import Pool

request = requests.get(url_api)

df = pd.read_json(request.text)

# df[['denom','conditionnement']] = df['denomination'].str.split(',',expand=True)
# df['conditionnement'] = df['conditionnement'].str.strip()

reg2 = r""
reg = r",([\w\s]*)"

denom = "PARACETAMOL MYLAN 500 mg, comprimé"

re.findall(reg,denom)

serie = df["denomination"]

# fonction extract !
serie.str.extract(reg)

reg = r"([\D]*)(\d+)(.*),(.*)"

serie.str.extract(reg)

df["mul"] = 1000

# fonction where !!!
df["mul"] = df["mul"].where(df[2].str.strip() == "g", 1)

# missing value
df["dosage"] = df[1].fillna(0).astype(int) * df["mul"]