# coding: utf-8

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

# Renault Zoe : version (3), année, kilométrage, prix, téléphone du propriétaire,
# vendue par un professionnel ou un particulier.
# Vous ajouterez une colonne sur le prix de l'Argus du modèle que vous récupérez
# sur ce site http://www.lacentrale.fr/cote-voitures-renault-zoe--2013-.html.

# 1 dataFrame année kilo prix argus (0 - 50 000)
# 2 ZOE Intens 0-50 000 5700 €

url_central = "https://www.lacentrale.fr"
url_recherche = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-IDF%2CFR-NAQ%2CFR-PAC"
url_cote = "/fiche_cote_auto_flat.php?source=detail&marque=renault&modele=zoe&version=q90%2Blife&type=perso&millesime=2015&km=16461&zipcode=92400&price=9200&ref=69103359226&fh=1&fdt=2015-07"

def get_request_from_url_and_build_soup(url):
    request_headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "http://thewebsite.com",
        "Connection": "keep-alive"
    }
    request = requests.get(url, headers = request_headers)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding : " + str(request.status_code))

def get_all_links_for_ads(url_recherche):
    links = []
    for i in range(1, nbPages + 1):
        url_page = url_recherche + "&page=" + str(i)
        print(url_page)
        soup = get_request_from_url_and_build_soup(url_page)
        Atags = soup.findAll("a", class_="linkAd ann")
        links = links + list(map(lambda x: url_central + x.attrs['href'], Atags))
    return links


def get_info_zoe_for_link(link):
    soup = get_request_from_url_and_build_soup(link)
    rawPrice = soup.find("strong", class_="sizeD lH35 inlineBlock vMiddle ").get_text().strip()
    price = int(rawPrice.replace(" ", "")[:-2])
    yearReg = re.compile("Année")
    year = int(soup.find("h4", text=yearReg).findNext("span").get_text())
    kiloReg = re.compile("Kilométrage")
    kilo = soup.find("h4", text=kiloReg).findNext("span").get_text()
    kilo = int(kilo.replace(" ", "")[:-2])
    typeVendeur = soup.find("div", class_="bold italic mB10").contents[0].strip()
    tel = soup.find("div", class_="phoneNumberContent").findNext("span").contents[0].strip()
    tel = tel.replace("\xa0", "")
    version = soup.find("div", class_="versionTxt txtGrey7C sizeC mB10 hiddenPhone").get_text().strip()
    # addresse = soup.find("strong", class_ = "w50 floatL bGreyCR borderBox clearPhone b0Phone")
    adresseReg = re.compile("Adresse")
    dep = list(soup.find("strong", text=adresseReg).parent.children)[8][:5]
    linkCote = soup.find("a", class_="btnDark txtL block").attrs["href"]
    linkCote = url_central + linkCote
    soup2 = get_request_from_url_and_build_soup(linkCote)
    argus = soup2.find("span", class_="jsRefinedQuot")
    if argus is not None:
        argus = argus.get_text().strip().replace(" ", "")
    else:
        argus  = "None"
    return [version, year, kilo, typeVendeur, dep, tel, price, argus]

infoZoe = []
counter = 1

soup = get_request_from_url_and_build_soup(url_recherche)

nbAnnonces = int(soup.find("span", class_="numAnn").get_text())
nbAnnoncesParPage = len(soup.findAll("div", class_="adLineContainer"))
nbPages = nbAnnonces // nbAnnoncesParPage if (nbAnnonces % nbAnnoncesParPage) == 0 else nbAnnonces // nbAnnoncesParPage + 1

linksAnnonces = get_all_links_for_ads(url_recherche)


# p = Pool(5)
# p.map(get_popularity_for_people, people)
#linksAnnonces = [item for sublist in linksAnnonces for item in sublist]

# for link in linksAnnonces:
#     infoZoe.append(get_info_zoe_for_link(link))
#     print(counter if counter%10==0 else "")
#     counter += 1

p = Pool(10)
infoZoe = list(p.map(get_info_zoe_for_link,linksAnnonces[:100]))

dfZoe = pd.DataFrame(infoZoe)

# https://www.lacentrale.fr/get_co_prox.php?km=16461&zipcode=92000&month=04&year=2015
# réponse : {"cote_brute":9585,"cote_perso":9364,"year_mileage":7680,"price_new":21900,"commercialModel":"ZOE","shouldDisplayMvcLink":true}

