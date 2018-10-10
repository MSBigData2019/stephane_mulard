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
from locale import *
from numpy import nan as NA
import pandas as pd

def Get_Request_From_Company_and_Build_Soup(company):
    request = requests.get("https://www.reuters.com/finance/stocks/financial-highlights/" +  company)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding or the company " + company + " is not found")


def Get_Share_Price_And_Percent_Change_From_Soup(soup):
    # Share price
    SharePrice = soup.find("span", class_="nasdaqChangeHeader").findNext("span").text.strip()
    SharePrice = Convert_To_Float_With_Comma_Or_Nan(SharePrice)

    # Percent change
    SharePercentChange = soup.find("span", class_="valueContentPercent").findNext("span").text.strip()
    SharePercentChange = re.sub('[()]', '', SharePercentChange)[:-1]
    SharePercentChange = Convert_To_Float_Or_Nan(SharePercentChange)

    return [SharePrice, SharePercentChange]

def Get_Quarter_Sales_End_Dec2018_From_Soup(soup):

    SalesTag = soup.find(lambda tag: tag.name == "td" and "Quarter Ending Dec-18" in tag.text)
    SalesValuesTag = list(SalesTag.parent.children)

    SalesNbEstimate = SalesValuesTag[3].text
    SalesMean = SalesValuesTag[5].text
    SalesHigh = SalesValuesTag[7].text
    SalesLow = SalesValuesTag[9].text
    Sales1YearAgo = SalesValuesTag[11].text

    SalesNbEstimate = Convert_To_Int_Or_Nan(SalesNbEstimate)
    SalesMean = Convert_To_Float_With_Comma_Or_Nan(SalesMean)
    SalesHigh = Convert_To_Float_With_Comma_Or_Nan(SalesHigh)
    SalesLow = Convert_To_Float_With_Comma_Or_Nan(SalesLow)
    Sales1YearAgo = Convert_To_Float_With_Comma_Or_Nan(Sales1YearAgo)

    return [SalesNbEstimate, SalesMean, SalesHigh, SalesLow, Sales1YearAgo]


def Get_Percent_Shares_Owned_From_Soup(soup):
    # Alternative :
    # SharesOwnedTag = soup_LVMH.find(lambda tag: tag.name == "strong" and "Shares Owned" in tag.text)
    # SharesOwned = list(SharesOwnedTag.parent.parent.children)[3].text

    pattern = re.compile(r'Shares Owned')
    SharesOwned = soup.find("td", text=pattern).findNext("td").text[:-1]

    SharesOwned = Convert_To_Float_Or_Nan(SharesOwned)

    return [SharesOwned]


def Get_Dividend_Yield_From_Soup(soup):
    DividendTag = soup.find(lambda tag: tag.name == "td" and "Dividend Yield" in tag.text)
    DividendValuesTag = list(DividendTag.parent.children)
    DividendCompany = DividendValuesTag[3].text
    DividendIndustry = DividendValuesTag[5].text
    DividendSector = DividendValuesTag[7].text

    DividendCompany = Convert_To_Float_Or_Nan(DividendCompany)
    DividendIndustry = Convert_To_Float_Or_Nan(DividendIndustry)
    DividendSector = Convert_To_Float_Or_Nan(DividendSector)

    return [DividendCompany, DividendIndustry, DividendSector]


def Convert_To_Float_Or_Nan(string):
    if string is not "" and string != "--":
        return float(string)
    else:
        return NA


def Convert_To_Float_With_Comma_Or_Nan(string):
    # Use locale to convert string to float when comma separator for thousands are present
    # alternative  : remove the "," character and cast to float
    setlocale(LC_NUMERIC, "en_GB")

    if string is not "" and string != "--":
        floatNb = atof(string)

        # returning to local locale
        setlocale(LC_NUMERIC, "")

        return floatNb
    else:
        return NA

def Convert_To_Int_Or_Nan(string):
    if string is not "" and string != "--":
        return int(string)
    else:
        return NA

CompaniesDict = {"LVMH" :"LVMH.PA", "Airbus" :"AIR.PA", "Danone" : "DANO.PA"}
CompaniesDataDict = {}

InformationIndex = ["Sales - #Estimates",
                    "Sales - Mean",
                    "Sales - High",
                    "Sales - Low",
                    "Sales - 1 Year Ago",
                    "Share price",
                    "Share percent change",
                    "% Shares owned",
                    "Dividend yield company",
                    "Dividend yield Industry",
                    "Dividend yield Sector"]

for company in CompaniesDict.items():

    soup = Get_Request_From_Company_and_Build_Soup(company[1])

    CompanyData = Get_Quarter_Sales_End_Dec2018_From_Soup(soup)
    CompanyData = CompanyData + Get_Share_Price_And_Percent_Change_From_Soup(soup)
    CompanyData = CompanyData + Get_Percent_Shares_Owned_From_Soup(soup)
    CompanyData = CompanyData + Get_Dividend_Yield_From_Soup(soup)

    CompaniesDataDict[company[0]] = CompanyData

CompaniesDataDF = pd.DataFrame( CompaniesDataDict,
                                index = InformationIndex)
print(CompaniesDataDF)


# pprint(soup_LVMH.find("strong", text=pattern).__dict__)
# pprint(soup_LVMH.find(text=pattern).parent.__dict__)


class CrawlerTests(unittest.TestCase):
    def testConvToFloatWithComma(self):
        self.assertEqual(Convert_To_Float_With_Comma_Or_Nan("123,456.7"), 123456.7)
        #self.assertEqual(Convert_To_Float_With_Comma_Or_Nan(""), NA)

def main():
    unittest.main()

if __name__ == '__main__':
    main()