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

import requests
import unittest
import re
import pandas as pd
from pprint import pprint
from locale import *
from numpy import nan as NA
from bs4 import BeautifulSoup
from datetime import datetime


def get_request_from_company_and_build_soup(company):
    request = requests.get("https://www.reuters.com/finance/stocks/financial-highlights/" +  company)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding or the company " + company + " is not found")


def get_share_price_and_percent_change_from_soup(soup):
    # Share price
    share_price = soup.find("span", class_="nasdaqChangeHeader").findNext("span").text.strip()
    share_price = _convert_string_to_float_or_nan(share_price)

    # Percent change
    share_percent_change = soup.find("span", class_="valueContentPercent").findNext("span").text.strip()
    share_percent_change = re.sub('[()]', '', share_percent_change)[:-1]
    share_percent_change = _convert_string_to_float_or_nan(share_percent_change)

    return [share_price, share_percent_change]

def get_quarter_sales_end_dec2018_from_soup(soup):

    sales_tag = soup.find(lambda tag: tag.name == "td" and "Quarter Ending Dec-18" in tag.text)
    sales_values_tag = list(sales_tag.parent.children)

    sales_nb_estimate = sales_values_tag[3].text
    sales_mean = sales_values_tag[5].text
    sales_high = sales_values_tag[7].text
    sales_low = sales_values_tag[9].text
    sales_1year_ago = sales_values_tag[11].text

    sales_nb_estimate = _convert_string_to_int_or_nan(sales_nb_estimate)
    sales_mean = _convert_string_to_float_or_nan(sales_mean)
    sales_high = _convert_string_to_float_or_nan(sales_high)
    sales_low = _convert_string_to_float_or_nan(sales_low)
    sales_1year_ago = _convert_string_to_float_or_nan(sales_1year_ago)

    return [sales_nb_estimate, sales_mean, sales_high, sales_low, sales_1year_ago]


def get_percent_shares_owned_from_Soup(soup):
    # Alternative :
    # SharesOwnedTag = soup_LVMH.find(lambda tag: tag.name == "strong" and "Shares Owned" in tag.text)
    # SharesOwned = list(SharesOwnedTag.parent.parent.children)[3].text

    pattern = re.compile(r'Shares Owned')
    SharesOwned = soup.find("td", text=pattern).findNext("td").text[:-1]

    SharesOwned = _convert_string_to_float_or_nan(SharesOwned)

    return [SharesOwned]


def get_dividend_yield_from_soup(soup):
    dividend_tag = soup.find(lambda tag: tag.name == "td" and "Dividend Yield" in tag.text)
    dividend_values_tag = list(dividend_tag.parent.children)
    dividend_company = dividend_values_tag[3].text
    dividend_industry = dividend_values_tag[5].text
    dividend_sector = dividend_values_tag[7].text

    dividend_company = _convert_string_to_float_or_nan(dividend_company)
    dividend_industry = _convert_string_to_float_or_nan(dividend_industry)
    dividend_sector = _convert_string_to_float_or_nan(dividend_sector)

    return [dividend_company, dividend_industry, dividend_sector]


def _convert_string_to_float_or_nan(string):
    if string is not "" and string.find("-") == -1 :

        return float(string.replace(",", ""))

        #Alternative using locale to convert number with "," for thousands
        #setlocale(LC_NUMERIC, "en_GB")
        #floatNb = atof(string)
        #setlocale(LC_NUMERIC, "")

    else:
        return NA


def _convert_string_to_int_or_nan(string):
    if string is not "" and string.find("-") == -1:
        return int(string)
    else:
        return NA

# -------------------------------------------------------------------------- #


CompaniesDict = {"LVMH": "LVMH.PA", "Airbus": "AIR.PA", "Danone": "DANO.PA"}
CompaniesDataDict = {}
CompaniesData2 = []
now = datetime.now()
dateDuJour = str(now.day) + "/" + str(now.month) + "/" + str(now.year)

# used for the first DataFrame with information presented vertically
InformationIndex = ["Sales - #Estimates",
                    "Sales - Mean",
                    "Sales - High",
                    "Sales - Low",
                    "Sales - 1 Year Ago",
                    "Share price" + " (" + dateDuJour + ")",
                    "Share percent change",
                    "% Shares owned",
                    "Dividend yield company",
                    "Dividend yield Industry",
                    "Dividend yield Sector"]

# used to create the second DataFrame with info in columns
InformationCol = ["Company",
                  "Sales_NbEstimates",
                  "Sales_Mean",
                  "Sales_High",
                  "Sales_Low",
                  "Sales_1_year_ago",
                  "Share_price",
                  "Share_percent_change",
                  "Shares_owned",
                  "Dividend_yield_company",
                  "Dividend_yield_industry",
                  "Dividend_yield_sector"]

for company in CompaniesDict.items():

    soup = get_request_from_company_and_build_soup(company[1])

    CompanyData = get_quarter_sales_end_dec2018_from_soup(soup)
    CompanyData = CompanyData + get_share_price_and_percent_change_from_soup(soup)
    CompanyData = CompanyData + get_percent_shares_owned_from_Soup(soup)
    CompanyData = CompanyData + get_dividend_yield_from_soup(soup)

    CompaniesDataDict[company[0]] = CompanyData

    CompaniesData2.append([company[0]] + CompanyData)

CompaniesDataDF = pd.DataFrame(CompaniesDataDict, index=InformationIndex)
print("Informations Reuters pour 3 entreprises \
dans un DataFrame vertical\n avec index sur les informations pour lisibilité")
print(CompaniesDataDF)

CompaniesDataDF2 = pd.DataFrame(CompaniesData2, columns=InformationCol)
print("\nInformations Reuters pour 3 entreprises \
dans un DataFrame horizontal\n avec les informations en colonnes pour les analyses")
print(CompaniesDataDF2)


class CrawlerTests(unittest.TestCase):
    def testConvToFloatWithComma(self):
        self.assertEqual(_convert_string_to_float_or_nan("123,456.7"), 123456.7)
        #self.assertEqual(_convert_string_to_float_or_nan(""), NA)


def main():
    unittest.main()

if __name__ == '__main__':
    main()