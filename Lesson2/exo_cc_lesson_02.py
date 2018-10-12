# coding: utf-8
# Entre les ordinateur DELL ou ACER plus soldés sur Rue du commerce

url = "https://www.rueducommerce.fr/rayon/ordinateurs-64/ordinateur-portable-657?sort=remise&view=grid&marque=acer"


import requests
import unittest
import re
import pandas as pd
from pprint import pprint
from locale import *
from numpy import nan as NA
from bs4 import BeautifulSoup
from datetime import datetime

url_root = "https://www.darty.com/nav/recherche?s=relevence&prix_barre=dcom_BONPLAN-dcom_BonPlan&fa=139552-756-790&text="

def get_request_from_marque_and_build_soup(marque):
    request = requests.get(url_root +  marque)
    print(url_root + marque)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding or the brand " + marque + " is not found" + str(request.status_code))


MarqueDict = {"Acer": "acer", "DELL": "Dell"}


for marque in MarqueDict.items():
    soup = get_request_from_marque_and_build_soup(marque[1])
    TagNb = soup.find("div", class_="list_number_product").findNext("b").text
    pprint("bons plans de " + marque[1] + ": " + TagNb)
