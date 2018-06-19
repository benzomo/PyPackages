# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


import os, sys, socket
import time, datetime
import numpy as np, pandas as pd


cName = socket.gethostname()

if cName == 'DESKTOP-HOKP1GT':
    ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/it0uu1ch.default"
    uofcPath = "D:/benmo/OneDrive - University of Calgary"
    mainDisk = "C:/Users/benmo"
    dataDisk = "D:/Data"
elif sys.platform == 'linux':
    ffProfilePath = "/home/benmo/.mozilla/firefox/bcnujh2r.auto"
    mainDisk = "/home/benmo"
    dataDisk = "/home/benmo/Data"
else:
    ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/vpv78y9i.default"
    uofcPath = "D:/OneDrive - University of Calgary"
    mainDisk = "C:/Users/benmo"
    dataDisk = "D:/Data"
    

    
def get_indices():
    
    fp = webdriver.FirefoxProfile(ffProfilePath)
    if sys.platform == 'linux':
        browser = webdriver.Firefox(executable_path="/home/benmo/Apps/Selenium/geckodriver",firefox_profile=fp)
    else:
        browser = webdriver.Firefox(firefox_profile=fp)
    
    tickers = pd.read_csv('/home/benmo/Data/Databases/ETFS.csv', header=None)[0]
    
     
    for ticker in tickers + ['^VIX']:
        url = "https://finance.yahoo.com/quote/{tk}/history?p={tk}".format(tk=ticker)   
        browser.get(url)
        
        try:
            WebDriverWait(browser, 5).until(
                        lambda x: x.find_element_by_xpath(
                "//*[@class='Bd(0) P(0) O(n):f D(ib) Fz(s) Fl(end) Mt(6px) Mend(8px) close']")).click()

        except:
            pass
        
        browser.find_element_by_xpath(
                "//*[@data-test='date-picker-full-range']").click()
        
        try:
            browser.find_element_by_xpath("//*[@data-value='Max']").click()
        except:
            browser.find_element_by_xpath(
                "//span[contains(text(), 'Max')]").click()
        browser.find_element_by_xpath(
                "//button/span[contains(text(), 'Done')]").click()
        browser.find_element_by_xpath(
                "//button/span[contains(text(), 'Apply')]").click()
        
        time.sleep(5)
        
        browser.find_element_by_xpath(
                "//*[contains(text(), 'Download Data')]").click()
        
    
    files = list(filter(lambda x: x[:-4] in tickers.tolist(), os.listdir(
            "/home/benmo/Downloads")))
    
    indices = pd.DataFrame([])
    
    for file in files:
        tempdf = pd.read_csv('/home/benmo/Downloads/' + file)
        tempdf['Ticker'] = file[:-4]
        indices = indices.append(tempdf)
    
    indices.to_csv("/home/benmo/Data/Databases/StockIndices.csv", index=False)
    
    
    browser.close()
    
    

