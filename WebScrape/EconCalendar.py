# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

import shutil, stopit
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
    

@stopit.threading_timeoutable(default='not finished')
def moveDL(fileout, ftype='.csv',err=0):       
    try:
        fileName = list(filter(lambda x: ftype in x, os.listdir(mainDisk + "/Downloads")))[0]
        shutil.move(mainDisk + "/Downloads/{fn}".format(
                fn=fileName), fileout)
        
        while len(os.listdir(mainDisk + "/Downloads")) > 1:
            pass
        
        return 1
    
    except:
        if err < 10:
            time.sleep(0.33)
            moveDL(fileout, ftype=ftype, err=err+1)
            


def test():
    print("this is a TEST!!!!")

    
def get_calendar():
    fp = webdriver.FirefoxProfile(ffProfilePath)
    if sys.platform == 'linux':
        browser = webdriver.Firefox(executable_path="/home/benmo/Apps/Selenium/geckodriver",firefox_profile=fp)
    else:
        browser = webdriver.Firefox(firefox_profile=fp)
    
    url = "https://www.fxstreet.com/economic-calendar"  
    browser.get(url)
    
    
    
    browser.find_element_by_xpath("//*[contains(text(), 'Today')]").click()
    time.sleep(1)

    browser.find_element_by_xpath(
            "//*[@class='fxs_btn_group fxs_btn_group_align_calendar']").click()
    
    browser.find_element_by_xpath("//*[contains(text(), 'Export as CSV')]").click()
    
    time.sleep(1)
    
    browser.close()
    
    moveDL("/home/benmo/Data/EconomicCalendar/{date}.csv".format(
            date=time.strftime("%d-%m-%Y")), timeout=10)
    


    

