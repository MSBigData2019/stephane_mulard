# coding: utf-8

# On va s'interesser aux données entreprise disponible sur le site de Reuters.
# Besoin métier: Analyser les performances financières des sociétés cotées
# pour décider d'une stratégie d'investissement.
#
# Je vous demande donc de récupérer les infos suivantes :
# * les ventes au quartier à fin décembre 2018
# * le prix de l'action et son % de changement au moment du crawling
# * le % Shares Owned des investisseurs institutionels
# * le dividend yield de la company, le secteur et de l'industrie
#
# pour les sociétés suivantes : Aribus, LVMH et Danone.
# Un exemple de page https://www.reuters.com/finance/stocks/financial-highlights/LVMH.PA.

url_LVMH = "https://www.reuters.com/finance/stocks/financial-highlights/LVMH.PA"
url_Airbus = "https://www.reuters.com/finance/stocks/financial-highlights/AIR.PA"
url_Danone = "https://www.reuters.com/finance/stocks/financial-highlights/DANO.PA"

cssClass_vente_action = "sectionQuote nasdaqChange/sectionQuoteDetail/span sans classe"
cssClass_pourcent_changement = "sectionQuote priceChange/sectionQuoteDetail/valueContent/valueContentPercent"

#ventes au quartier
#Chaine "SALES (in millions)" TD class dataTitle, à l'intérieur chaine "Quarter Ending Dec-18" dans TD class stripe
#Données dans siblings TD class data, puis sélection 2, 3 ou 4 poour mean, high, low

#% share owned
#Chaine  "% Shares Owned", sibling TD class data pour la valeur en %

#dividend yield
#chaine exacte Dividend Yield dans TD puis 3 sibling TD class data pour les 3 valeurs

import requests
import unittest
from bs4 import BeautifulSoup
import re
from pprint import pprint
import locale

page_LVMH = requests.get("https://www.reuters.com/finance/stocks/financial-highlights/LVMH.PA")

if page_LVMH.status_code == 200:
    html_LVMH = page_LVMH.text
    soup_LVMH = BeautifulSoup(html_LVMH, "html.parser")

#print(soup_LVMH.find("strong", text="Shares Owned")) #ne fonctionne pas

print("Info LVMH")

#ventes au quartier à fin décembre 2018
SalesTag = soup_LVMH.find(lambda tag:tag.name=="td" and "Quarter Ending Dec-18" in tag.text)
SalesListValues = list(SalesTag.parent.children)
SalesNbEstimate = SalesListValues[3].text
SalesMean = SalesListValues[5].text
SalesHigh = SalesListValues[7].text
SalesLow = SalesListValues[7].text

print("Vente au quartier à fin dec. 2018 :")
print("Nb estimate : " + SalesNbEstimate)
print("Mean : " + SalesMean)
print("High : " + SalesHigh)
print("Low : " + str(SalesLow))

#setlocale(LC_NUMERIC,"")
#print("Low2 : " + str(locale.atof(SalesLow)))

#Shares Owned
SharesOwnedTag = soup_LVMH.find(lambda tag:tag.name=="strong" and "Shares Owned" in tag.text)
SharesOwnedValueString = list(SharesOwnedTag.parent.parent.children)[3].text
#SharesOwnedValue = float(SharesOwnedValueString[:-1])
print("% Shares Owned des investisseurs : " + str(SharesOwnedValueString))

# pattern = re.compile(r'Shares')
# print(soup_LVMH.find("strong", text=pattern))
# pprint(soup_LVMH.find("strong", text=pattern).__dict__)
#pprint(soup_LVMH.find(text=pattern).parent.__dict__)
#print(soup_LVMH(text=pattern))

#dividend yield
DividendTag = soup_LVMH.find(lambda tag:tag.name=="td" and "Dividend Yield" in tag.text)
DividendListValue = list(DividendTag.parent.children)
DividendTagCompany = DividendListValue[3].text
DividendTagIndustry = DividendListValue[5].text
DividendTagSector = DividendListValue[7].text

print("Dividend Yield company : " + DividendTagCompany)
print("Dividend Yield industry : " + DividendTagIndustry)
print("Dividend Yield sector : " + DividendTagSector)



# class Lesson1Tests(unittest.TestCase):
#     def test(self):
#         self.assertEqual("", "")
#
# def main():
#     unittest.main()
#
# if __name__ == '__main__':
#     main()