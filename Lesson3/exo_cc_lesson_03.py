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

def get_request_from_url_and_build_soup(url):
    request = requests.get(url)
    if request.status_code == 200:
        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup
    else:
        print("The website is not responding : " + str(request.status_code))


