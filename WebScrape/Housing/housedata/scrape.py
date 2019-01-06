#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 18:43:02 2018

@author: benmo
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import os, sys, socket, copy
import time, datetime, dill
import numpy as np, pandas as pd
import json, re


from fake_useragent import UserAgent


cName = socket.gethostname()

wait_rand = np.random.normal  

def test():
    print("this is a TEST!!!!")
    
    
def kill_popups(browser, t=5):
    try:
        WebDriverWait(browser, t).until(
                        lambda x: x.find_element_by_id('btnAcceptTOSModal')).click()
        
        
    except:
        try:
            browser.find_element_by_xpath(
                "//*[@title='Click to close.']").click()
        except:
            pass
        

if sys.platform == 'linux':
    
    options = Options()
    ua = UserAgent()
    #userAgent = ua.random
    #options.add_argument(f'user-agent={userAgent}')
    options.add_argument(f'user-agent=Chrome/24.0.1309.0')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    #options.add_argument("--incognito")
    #options.add_argument("--disable-plugins-discovery")
    options.add_argument("--start-maximized")
  
    browser = webdriver.Chrome(options=options,
                               executable_path="/home/benmo/Apps/Selenium/chromedriver")
    #fp = webdriver.FirefoxProfile('/home/benmo/.mozilla/firefox/v2onam20.scraper')
    #fp.set_preference("general.useragent.override", "Chrome/40.0.2214.85")
    #browser = webdriver.Firefox(executable_path="/home/benmo/Apps/Selenium/geckodriver", firefox_profile=fp)
    
class REScraper():
    def __init__(self, browser, pricei, nh):    
        self.neighborhoods = ['Tuscany', 'Sage Hill', 'Dalhousie', 'Country Hills', 'Brentwood']
        self.lprices = [450000 + i for i in range(0, 250000, 25000)]
        
        
        self.data = pd.read_pickle('/home/benmo/Data/Databases/CREA/data.pkl')    

        self.browser = browser

        time.sleep(wait_rand(3,0.25))
        self.browser.get('https://www.realtor.ca')
        time.sleep(wait_rand(3,0.25))
        
        self.today = datetime.date.today().strftime('%Y-%m-%d')
        
        self.collected_data = pd.read_pickle('/home/benmo/Data/Databases/CREA/collecteddata.pkl')
    

    def get_search_criteria(self):
        self.browser.find_element_by_id('homeSearchMoreBtn').click()
        time.sleep(wait_rand(2,0.25))
        self.browser.find_element_by_id('buildingType').click()




        house_selection = self.browser.find_element_by_id('select2-ddlBuildingType-results').find_elements(
                            By.CSS_SELECTOR , '*')[1]

        ActionChains(self.browser).move_to_element(house_selection).click().perform()
        self.browser.find_element_by_id('homeSearchMoreBtn').click()
        time.sleep(wait_rand(1,0.25))

        self.browser.find_element_by_id('homeSearchTxtCon').click()
        time.sleep(wait_rand(4,0.25))
        
    
    def collect_data(self, pricei, nh): 
        
        self.get_search_criteria()
        
        self.collected_data = self.collected_data.append(pd.DataFrame(
                np.array([pd.to_datetime(datetime.date.today()), nh, pricei]).reshape(1,-1), 
                columns=['Date','Neihborhood', 'LPrice'], 
                index=[0]), ignore_index=True)
            
        kill_popups(self.browser)
        
        self.browser.find_element_by_id('homeSearchTxt').send_keys('Calgary' + ', ' + nh)
        time.sleep(wait_rand(2,0.25))
        
        price_i = True
            
        kill_popups(self.browser)
        
        for el_id, val in zip(['MinPriceTop', 'MaxPriceTop'],
                           [pricei, pricei + 25000]):
            
            self.browser.find_element_by_id(el_id).click()
            time.sleep(wait_rand(2.5,0.25))
            el = self.browser.find_element_by_class_name('select2-search__field')
            ActionChains(self.browser).move_to_element(el).send_keys(val,Keys.ENTER).perform()
        
        time.sleep(wait_rand(5,0.25))
        
        self.go_to_map()
        self.collect_cards(nh=nh)    
            
    def check_listing(self, cardj):
        _mls = WebDriverWait(cardj, 7.5).until(
                    lambda x: x.find_element_by_class_name('listingCardMLS')
                    ).text.replace('MLS®: ','')
        
        noMLS = True if _mls not in self.data.keys() else False
        if not noMLS:
            hasPrice = True if WebDriverWait(cardj, 7.5).until(
                        lambda x: x.find_element_by_class_name('listingCardPrice')
                        ).text not in self.data[_mls]['ListingPrice'].values() else False
            
            noMLS = True if hasPrice else False
            
        else:
            hasPrice = True
            
        
        return True if noMLS & hasPrice else False
    
        
    def go_to_map(self):
        self.browser.find_element_by_id('homeSearchBtn').click()
        time.sleep(wait_rand(2,0.25))
    
        self.browser.find_element(By.LINK_TEXT,'Map').click()
        time.sleep(wait_rand(2,0.25))
        self.browser.find_element(By.LINK_TEXT,'List').click()

    def collect_cards(self, nh):
        cardlist = self.browser.find_element_by_id('listInnerCon').find_elements_by_class_name('cardCon')
        trigger=False
            
        for j in range(len(cardlist)):
            if trigger == True:
                time.sleep(wait_rand(3,0.5))
            
            trigger=False
            time.sleep(wait_rand(0.1,0.05))
            self.cardlisti = self.browser.find_element_by_id('listInnerCon').find_elements_by_class_name('cardCon')
            
            if self.check_listing(self.cardlisti[j]):
                kill_popups(self.browser)
                trigger=True
                
                
                self.cardlisti[j].click()
                
                time.sleep(wait_rand(5,1))
                
                soup = BeautifulSoup(self.browser.page_source, 'html5lib')
                
                datai = {}
                datai['MLSNum'] = soup.find('div', {'id': 'listingMLSNum'}).text
                
                
                datai['Neighborhood'] = nh
                datai['Address'] = soup.find('div', {'id': 'listingAddress'}).text
                datai['Description'] = soup.find('div', {'id': 'propertyDescriptionCon'}).text.strip()
                
                _listingprice = soup.find('div', {'id': 'listingPrice'}).text
                _mlsnum = datai['MLSNum'].replace('MLS® Number: ','')
                if _mlsnum in self.data.keys():
                    if _listingprice in self.data[_mlsnum]['ListingPrice'].values():
                        self.data[_mlsnum]['ListingPrice'] = dict(self.data[_mlsnum]['ListingPrice'], **{self.today: soup.find('div', {'id': 'listingPrice'}).text})
                    
                else:
                    
                    datai['ListingPrice'] = {self.today: soup.find('div', {'id': 'listingPrice'}).text}
                    #get building & property summary:
                    for cat in ['PropertySummary','listingDetailsBuildingCon', 'propertyDetailsLandSection']:
                        temp = soup.find('div', {'id': cat})
                        try:
                            datai[cat] = dict(zip(list(map(lambda x: x.text, temp.find_all('div', {'class': re.compile(r'ContentLabel')}))), 
                                 list(map(lambda x: x.text, temp.find_all('div', {'class': re.compile(r'ContentValue')})))))
                        except:
                            pass
                    
                    
                    #get room details:
                    temp = soup.find('div', {'class': 'propertyDetailsRoomContent'})
                    datai['RoomDetails'] = dict(zip(list(map(lambda x: x.text, temp.find_all('div', {'class': 'listingDetailsRoomDetails_Room'}))), 
                                 list(map(lambda x: x.text, temp.find_all('div', {'class': 'listingDetailsRoomDetails_Dimensions Metric'})))))
                    
                    
                    self.browser.find_element_by_class_name('whiteButtonLeftIcon').click()
                    
                    self.data[datai['MLSNum'].replace('MLS® Number: ','')] = datai.copy()
        

def script(scraper, nh):
    cardlist = scraper.browser.find_element_by_id('listInnerCon').find_elements_by_class_name('cardCon')
    trigger=False
        
    for j in range(len(cardlist)):
        if trigger == True:
            time.sleep(wait_rand(3,0.5))
        
        trigger=False
        
        scraper.cardlisti = scraper.browser.find_element_by_id('listInnerCon').find_elements_by_class_name('cardCon')
        
        if  WebDriverWait(scraper.cardlisti[j], 7.5).until(
                lambda x: x.find_element_by_class_name('listingCardMLS')).text.replace('MLS®: ','') not in scraper.data.keys():
            kill_popups(scraper.browser)
            trigger=True
            
            scraper.cardlisti[j].click()
            
            time.sleep(wait_rand(5,1))
            
            soup = BeautifulSoup(scraper.browser.page_source, 'html5lib')
            
            datai = {}
            datai['MLSNum'] = soup.find('div', {'id': 'listingMLSNum'}).text
            datai['Neighborhood'] = nh
            datai['Address'] = soup.find('div', {'id': 'listingAddress'}).text
            datai['Description'] = soup.find('div', {'id': 'propertyDescriptionCon'}).text.strip()
            datai['ListingPrice'] = soup.find('div', {'id': 'listingPrice'}).text
    
            
            #get building & property summary:
            for cat in ['PropertySummary','listingDetailsBuildingCon', 'propertyDetailsLandSection']:
                temp = soup.find('div', {'id': cat})
                try:
                    datai[cat] = dict(zip(list(map(lambda x: x.text, temp.find_all('div', {'class': re.compile(r'ContentLabel')}))), 
                         list(map(lambda x: x.text, temp.find_all('div', {'class': re.compile(r'ContentValue')})))))
                except:
                    pass
            
            
            #get room details:
            temp = soup.find('div', {'class': 'propertyDetailsRoomContent'})
            datai['RoomDetails'] = dict(zip(list(map(lambda x: x.text, temp.find_all('div', {'class': 'listingDetailsRoomDetails_Room'}))), 
                         list(map(lambda x: x.text, temp.find_all('div', {'class': 'listingDetailsRoomDetails_Dimensions Metric'})))))
            
            
            scraper.browser.find_element_by_class_name('whiteButtonLeftIcon').click()
            
            scraper.data[datai['MLSNum'].replace('MLS® Number: ','')] = datai.copy()
            
            return scraper
    
    