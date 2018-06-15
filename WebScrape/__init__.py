# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
import html5lib, requests
from bs4 import BeautifulSoup
import shutil
import os, sys, socket
import time, datetime
import numpy as np, pandas as pd
import stopit
import json
import bson

cName = socket.gethostname()

if cName == 'DESKTOP-HOKP1GT':
    ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/it0uu1ch.default"
    uofcPath = "D:/benmo/OneDrive - University of Calgary"
    mainDisk = "C:/Users/benmo"
    dataDisk = "D:/Data"
elif sys.platform == 'linux':
    ffProfilePath = "/home/benmo/.mozilla/firefox/w55ako72.dev-edition-default"
    mainDisk = "/home/benmo"
    dataDisk = "/home/benmo/Data"
else:
    ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/vpv78y9i.default"
    uofcPath = "D:/OneDrive - University of Calgary"
    mainDisk = "C:/Users/benmo"
    dataDisk = "D:/Data"
