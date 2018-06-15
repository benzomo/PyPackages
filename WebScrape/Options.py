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
    

def test():
    print("this is a TEST!!!!")

    
def get_options():
    
    fp = webdriver.FirefoxProfile(ffProfilePath)
    if sys.platform == 'linux':
        browser = webdriver.Firefox(executable_path="/home/benmo/Apps/Selenium/geckodriver",firefox_profile=fp)
    else:
        browser = webdriver.Firefox(firefox_profile=fp)
    
    tickers = pd.read_csv('/home/benmo/Data/Databases/ETFS.csv', header=None)[0]
    
    def get_json(browser, docx, expDates, i):
        WebDriverWait(browser, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "//div/select[@class='Fz(s)']").find_elements(
                                    By.CSS_SELECTOR , '*')[i]).click()
            
        datetxt = expDates[i]

        
        bob = browser.find_element_by_xpath("//script[contains(text(), '(function (root)')]")
        bob = bob.get_attribute('innerText')
        
        
        date = datetime.datetime.strptime(
                datetxt,"%B %d, %Y").strftime('%m-%d-%Y')
       
        
        bob = bob.replace("\n", '')
        bob = bob.replace("\\", '')
        
        start = bob.find(""""OptionContractsStore":""")
        
        bob = bob[start:]
        end = bob.find('}}}') + 3
    
               
        bob = '{' + bob[:end] + '}}'
    
        bob = json.loads(bob)
        
        docx[ticker][today][date] = bob
    
        return docx
    
    
    for ticker in tickers:
        url = "https://finance.yahoo.com/quote/{tk}/options?p={tk}".format(tk=ticker)   
        browser.get(url)
        
        
        today = time.strftime("%m-%d-%Y")
        
        expDates = list(map(lambda x: x.text, browser.find_element_by_xpath(
                "//div/select[@class='Fz(s)']").find_elements(By.CSS_SELECTOR , '*')))
        
        docx = {}
        docx[ticker] = {}
        docx[ticker][today] = {}
        
        
        for i in range(len(expDates)):
            try:
                docx = get_json(browser, docx, expDates, i)
            except:
                time.sleep(1)
                browser.get(url)
                docx = get_json(browser, docx, expDates, i)
            
                     
        with open('/home/benmo/Data/Options/{tk}/{dt}.json'.format(
                tk=ticker,dt=today), 'w') as outfile:
            outfile.write(json.dumps(docx))
    
    

