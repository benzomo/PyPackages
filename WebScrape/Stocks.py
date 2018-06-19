# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

import pandas as pd, numpy as np, datetime
import time
import sys, os, socket
from selenium import webdriver
import quandl



cName = socket.gethostname()


if sys.platform == 'linux':
    genDir = "/home/benmo/OneDrive/GitHub/DataPlayground" #get general functions path
    drive = "/home/benmo/Data"
    stocks = pd.read_csv("/home/benmo/Data/Valuation.csv")
else:
    try: 
        genDir = "D:/OneDrive/GitHub/DataPlayground" #get general functions path
        drive = "D:"
        stocks = pd.read_excel("C:/Users/benmo/OneDrive/Personal Research/Investing/Valuation.xlsm", sheetname='Stock',
                           skiprows=3)
    except: 
        genDir = "D:/benmo/OneDrive/GitHub/DataPlayground"
        drive = "D:"
        stocks = pd.read_excel("D:/benmo/OneDrive/Personal Research/Investing/Valuation.xlsm", sheetname='Stock',
                           skiprows=3)



ffProfilePath = "/home/benmo/.mozilla/firefox/w55ako72.dev-edition-default"
mainDisk = "/home/benmo"
dataDisk = "/home/benmo/Data"



#fp = webdriver.FirefoxProfile(ffProfilePath)
#fp.set_preference('webdriver.load.strategy', 'unstable')

#browser = webdriver.Firefox(executable_path="/home/benmo/Apps/Selenium/geckodriver",firefox_profile=fp)


#browser.set_page_load_timeout(5)

def get_daily():
    stocks = stocks.drop(stocks[(stocks['Country'] != 'USA')].index)
    stocks = stocks.drop(stocks[(stocks['Exchange'] != 'NYQ') & (stocks['Exchange'] != 'NMS')].index)

    todayDate = time.strptime(time.strftime("%d/%m/%Y"), '%d/%m/%Y')
    todayDateNum = time.mktime(todayDate)
    todayDateStr = time.strftime("%d_%m_%Y")
    fileDir = "/home/benmo/Data/Daily"



    for i in range(stocks['Ticker'].size):  # stocks['Ticker'].size:

        ticker = stocks['Ticker'][stocks.index[i]]
        if os.path.exists("{fd}/daily{tk}.csv".format(fd=fileDir, tk=ticker)):
            pass
        else:
            try:

                x = quandl.get("WIKI/{tk}".format(tk=ticker), start_date="2017-02-02",
                               authtoken="FLjC56RgKyq7-zAcTJ_x")
                x['Ticker'] = ticker

                if i == 0:
                    df = x
                    df.to_csv("{fd}/daily{tk}.csv".format(fd=fileDir, tk=ticker), encoding='utf-8')
                else:
                    df = pd.concat([df, x])
                    x.to_csv("{fd}/daily{tk}.csv".format(fd=fileDir, tk=ticker), encoding='utf-8')

            except:
                pass


def get_intraDay():
    def get_data(ticker, exchange):
        #url = "https://finance.google.com/finance/getprices?q={tk}&x={exch}&i=300&p=5d&f=d,c,o,h,l,v".format(tk = ticker, exch = exchange)
        #browser.get(url)
        #data = browser.find_element_by_tag_name('pre').text
        #x = np.array(pd.DataFrame([
                #line.split('\n') for line in data.split('\n\n')][0])[7:][0].apply(
                #lambda x: x.split(',')).tolist())
        
        x=np.array(pd.read_csv("http://finance.google.com/finance/getprices?q={tk}&x={exch}&i=300&p=5d&f=d,c,o,h,l,v".format(tk = ticker, exch = exchange),skiprows=7,header=None))
        date=[]
        for i in range(0,len(x)):
            if x[i][0][0]=='a':
                t= datetime.datetime.fromtimestamp(int(x[i][0].replace('a','')))
                date.append(t)
            else:
                date.append(t+datetime.timedelta(minutes =int(x[i][0])*5))
        data=pd.DataFrame(x,index=date)
        data.columns=['a','Open','High','Low','Close','Vol']

        return data

    if cName == 'DESKTOP-HOKP1GT':
        stocks = pd.read_excel("D:/OneDrive/Personal Research/Investing/Valuation.xlsm",sheet_name='Stock', skiprows=3)
    else:
        stocks = pd.read_csv("/home/benmo/Data/Valuation.csv")

    stocks = stocks.drop(stocks[(stocks['Country'] != 'USA')].index)
    stocks = stocks.drop(stocks[(stocks['Exchange'] != 'NYQ') & (stocks['Exchange'] != 'NMS')].index)


    todayDate = time.strptime(time.strftime("%d/%m/%Y"),'%d/%m/%Y')
    todayDateNum = time.mktime(todayDate)
    todayDateStr = time.strftime("%d_%m_%Y")


    fileDir = "/home/benmo/Data/IntraDay"

    j=0

    while j < 200:
        
        i = np.random.randint(0, stocks['Ticker'].size)
        exists = False
        
        for dayi in range(5):
            date_i = time.localtime(todayDateNum - dayi*60*60*24)
            if(((os.path.exists("{myDir}/{tk}/{dt}.csv".format(myDir=fileDir,tk=stocks['Ticker'][stocks.index[i]], dt="{d}_{m}_{y}".format(d=date_i.tm_mday,m=date_i.tm_mon,y=date_i.tm_year)))) | 
                    (os.path.exists("{myDir}/{tk}/{dt}.csv".format(myDir=fileDir,tk=stocks['Ticker'][stocks.index[i]], dt="0{d}_{m}_{y}".format(d=date_i.tm_mday,m=date_i.tm_mon,y=date_i.tm_year))))) |
                     ((os.path.exists("{myDir}/{tk}/{dt}.csv".format(myDir=fileDir,tk=stocks['Ticker'][stocks.index[i]], dt="0{d}_0{m}_{y}".format(d=date_i.tm_mday,m=date_i.tm_mon,y=date_i.tm_year))) |
                             os.path.exists("{myDir}/{tk}/{dt}.csv".format(myDir=fileDir,tk=stocks['Ticker'][stocks.index[i]], dt="{d}_0{m}_{y}".format(d=date_i.tm_mday,m=date_i.tm_mon,y=date_i.tm_year)))))):
                exists = True
                stocks = stocks.drop(stocks.index[i])           
                break
            
        if exists:
            pass
        else:
            if (stocks['Valid  URL (Y/N)'][stocks.index[i]] ==1) & (stocks['Exchange'][stocks.index[i]] == 'NYQ'):
                exch = 'NYSE'
            elif (stocks['Valid  URL (Y/N)'][stocks.index[i]] ==1) & (stocks['Exchange'][stocks.index[i]] == 'NMS'):
                exch = 'NASDAQ'
            else:
                pass
            try:
                data = get_data(stocks['Ticker'][stocks.index[i]], exch)

                try:
                    os.mkdir("{myDir}/{tk}".format(myDir=fileDir, tk=stocks['Ticker'][stocks.index[i]]))
                except:
                    pass

                data.to_csv("{myDir}/{tk}/{dt}.csv".format(myDir=fileDir,tk=stocks['Ticker'][stocks.index[i]], dt=todayDateStr), encoding='utf-8')
                stocks = stocks.drop(stocks.index[i])
                j = j + 1
                if stocks['Ticker'].size == 1:
                    break
        
            except:
                stocks = stocks.drop(stocks.index[i])
                if stocks['Ticker'].size == 1:
                    break
