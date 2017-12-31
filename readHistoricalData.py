#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 21:12:14 2017

@author: milad
"""

import time
from datetime import datetime, timedelta
import math
import browser as br   
import json
from Share import Price


class History():
    def __init__(self, symbol):
        self.baseurl = "https://finance.services.appex.bing.com/Market.svc/ChartDataV5?symbols={}&chartType=1y&isEOD=False&lang=en-US&isCS=true&isVol=true"
        # https://finance.services.appex.bing.com/Market.svc/ChartDataV5?symbols=200.1.ADS.FRA&chartType=1y&isEOD=False&lang=en-US&isCS=true
        self.symbol = symbol
        self.MSNLink = None
        self.data = None # year hostorical data
        self.today = None
        self.daysInfo = list()
        
    def crawl(self):
        # read the JSON file of the symbol
        # extract the MSNlink of the share
        MSNLink = "fi-200.1.ADS.FRA"
        # remove the fi- from the beginning of the symbol
        self.MSNLink = MSNLink[3:]
        # read historical data of a year
        self.yearHistory()
        self.getToday()
        self.eachDay()
        return
    
    def yearHistory(self):
        url_ = self.baseurl.format(self.MSNLink)
        response = br.url_request(url_)
        # convert bytes to string
        response = response.decode("utf-8")
        # format: "[{data}]"
        response = response[1: (len(response) - 1 )]
        response = response.replace("'", "\"")
        # convert string representing dict to dict object
        self.data = json.loads(response)
        return
    
    def getToday(self):
        time_ = self.data["utcFullRunTime"]
        # format: /Date(TIME)/
        # remove /Date( )/
        time_ = time_[6: ( len(time_) - 2 )]
        time_ = int(time_)
        if time_ > 100000000000:
            time_ = math.floor(time_ / 1000);
        # convert epoch time to human readable time
        time_ = time.strftime('%Y-%m-%d', time.localtime(time_))
        # convert to time object
        self.today = datetime.strptime(time_, '%Y-%m-%d')
        return
    
    def eachDay(self):
        days = self.data["Series"]
        for day in days:
            self.daysInfo.append( self.processDayInfo(day) )
        return
    
    def processDayInfo(self, day):
        # expected day = dict
        if type(day) is not dict:
            return Price()
        time = day.get("T", 0)
        if time == 0:
            return Price()
        price = Price()
        price.HighPrice = day.get("Hp", 0)
        price.LowPrice = day.get("Lp", 0)
        price.OpenPrice = day.get("Op", 0)
        price.ClosePrice = day.get("P", 0)
        price.Volume = day.get("V", 0)
        # convert time value from minutes to days
        time = time / 1440
        # calculate difference of today and time
        time = 365 - time
        # calculate time of day object based on today
        price.Date = self.today - timedelta( days = time )
        return price
        
h = History("A")
h.crawl()
print (type(h.daysInfo))

for day in h.daysInfo:
    print ("date: {} , OpenPrice: {}".format( day.Date, day.OpenPrice ))
