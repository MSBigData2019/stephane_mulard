# coding: utf-8

import requests
import unittest
import re
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
import concurrent.futures
from multiprocessing import Pool

url_256_contributors = "https://gist.github.com/paulmillr/2657075"
url_api_profile_test = 'https://api.github.com/users/fabpot/repos'

def get_request_from_url_and_build_soup(url):
    request = requests.get(url)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding : " + str(request.status_code))


def get_request_from_url_and_build_json(url):
    headers = {'Authorization' : 'token 2fdaf474421adf415e0c63fa36abcf9c70a4d2a4'}
    request = requests.get(url, headers=headers)
    jsonObject = json.loads(request.text)
    return jsonObject


def get_all_links_from_top256(url):
    soup = get_request_from_url_and_build_soup(url_256_contributors)
    info = soup.find_all("th", text=re.compile("#[0-9]"))

    all_links = list(map(lambda x : (x.get_text()[1:],
                                      x.findNext("a").attrs['href'],
                                      x.findNext("a").get_text()), info))

    return list(zip(*all_links))


def get_starcount_per_page (url_api):
    response_object = get_request_from_url_and_build_json(url_api)
    nbstar = 0
    if len(response_object)!= 0:
        for dico in response_object:
            nbstar = nbstar + int(dico['stargazers_count'])
        return nbstar
    else:
        # cas de 0 repository
        return 0


def get_nb_repos_for_account(url):
    response_object = get_request_from_url_and_build_json(url)
    nbrepos = 0
    if len(response_object) != 0:
        nbrepos = response_object['public_repos']
        return nbrepos
    else:
        # cas de 0 repository
        return 0

def get_starcount_per_user(linkApiUser,nbRepos):
    total_star = 0
    for i in range(1, nbRepos//100 + 2):
        linkApiRepos = linkApiUser + "/repos?page=" + str(i) + "&per_page=100"
        total_star = total_star + get_starcount_per_page(linkApiRepos)
    return total_star

################# main #####################

start = time.time()
all_links = get_all_links_from_top256(url_256_contributors)
end = time.time()
print("time to retrieve the 256 links : {:.2f} seconds".format(round(end - start, 2)))

# Build the DataFrame
df = pd.DataFrame(all_links)
df=df.T

# Initialize lists
listrepos = []
liststar = []
listmoy = []

counter = 1

start = time.time()
for name in df[2]:
    linkApiUser = "https://api.github.com/users/" + name
    nbRepos = get_nb_repos_for_account(linkApiUser)

    total_star = get_starcount_per_user(linkApiUser,nbRepos)

    average_star_count = int(total_star / nbRepos) if nbRepos != 0 else 0
    print("{} - {} : {} repos --> {} stars, avg = {}".format(counter, name, nbRepos, total_star, average_star_count))

    listrepos.append(nbRepos)
    liststar.append(total_star)
    listmoy.append(average_star_count)
    counter += 1

end = time.time()
print("time to count the stars for all 256 contributors : {:.2f} minutes".format((end - start)/60))

# Adding the constructed lists to the DataFrame
df['Nb repos'] = listrepos
df['Total star'] = liststar
df['Average'] = listmoy

df.sort_values(by='Average',  ascending=False)

df.to_csv("GithubTop256.csv")

