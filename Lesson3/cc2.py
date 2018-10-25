# coding: utf-8
import pandas as pd
import requests

population = pd.read_excel('population.xls', skiprows=7, sheet_name="Communes")
population = population[['Nom de la commune','Population totale','Code département']]

population = population.sort_values(by=['Population totale'],ascending=False)
population = population[~population['Nom de la commune'].str.contains('Paris')]

#population = population[population['Code département'] == '14']

LIMIT = 30

population = population[3:10]


API_KEY = open("api_key.txt", "r").read()

url_template = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={}&destinations={}&key={}"

origins = '|'.join(population['Nom de la commune'])
destinations = '|'.join(population['Nom de la commune'])
url_formatted = url_template.format(origins, destinations, API_KEY)


results =  requests.get(url_formatted).json()

distances = list(map(lambda x: list(map(lambda y: y['distance']['text'],x['elements'])), results['rows']))
distance_matrix = pd.DataFrame(distances,columns=population['Nom de la commune'], index=population['Nom de la commune'])


