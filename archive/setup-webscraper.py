# -*- coding: utf-8 -*-
"""
Created on Mon May 13 13:32:11 2019

@author: CAmao
"""

from distutils.core import setup
import py2exe
import sys
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib.request

#sys.setrecursionlimit(5000)
setup(console=['WSWebScraper.py'])
