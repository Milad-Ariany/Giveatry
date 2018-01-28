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
from PriceInfo import Price
import json
from enum import Enum
        
class Interval (Enum):
    lastYear = 0

class HistoricalPrices():
    def __init__(self, MSNLink, Interval = Interval.lastYear):
        self.interval = Interval
        self.MSNLink = MSNLink
        self.dataSource = None # hostorical data [ Prices ]
        self.prices = list()
        
    def crawl(self):
        # expected format of MSNLink: fi-xxx.xxxx.xxx
        # remove the fi- from the beginning of the symbol
        self.MSNLink = self.MSNLink[3:]
        # read historical data of a year
        self.yearHistory()
        self.eachDay( self.getToday() )
        return
    
    def yearHistory(self):
        baseUrl = "https://finance.services.appex.bing.com/Market.svc/ChartDataV5?symbols={}&chartType=1y&isEOD=False&lang=en-US&isCS=true&isVol=true"
        url_ = baseUrl.format(self.MSNLink)
        response = br.url_request(url_)
        # convert bytes to string
        response = response.decode("utf-8")
        # format: "[{data}]"
        response = response[1: (len(response) - 1 )]
        response = response.replace("'", "\"")
        # convert string representing dict to dict object
        self.dataSource = json.loads(response)
        return
    
    def getToday(self):
        time_ = self.dataSource["utcFullRunTime"]
        # format: /Date(TIME)/
        # remove /Date( )/
        time_ = time_[6: ( len(time_) - 2 )]
        time_ = int(time_)
        if time_ > 100000000000:
            time_ = math.floor(time_ / 1000);
        # convert epoch time to human readable time
        time_ = time.strftime('%Y-%m-%d', time.localtime(time_))
        # convert to time object
        _today = datetime.strptime(time_, '%Y-%m-%d')
        return _today

    def eachDay(self, today):
        data = self.dataSource["Series"]
        for dateOfDay in data:
            self.prices.append( self.processDayInfo(dateOfDay, today) )
        return
    
    def processDayInfo(self, data, today):
        # expected day = dict
        if type(data) is not dict:
            return Price()
        time = data.get("T", 0)
        if time == 0:
            return Price()
        priceObj = Price()
        priceObj.HighPrice = data.get("Hp", 0)
        priceObj.LowPrice = data.get("Lp", 0)
        priceObj.OpenPrice = data.get("Op", 0)
        priceObj.ClosePrice = data.get("P", 0)
        priceObj.Volume = data.get("V", 0)
        # convert time value from minutes to days
        time = time / 1440
        # calculate difference of today and time
        time = 365 - time
        # calculate time of day object based on today and extract the date
        priceObj.Date = str( today - timedelta( days = time ) )[:10]
        return priceObj
        
## TEST
#h = History("AAPL")
#h.crawl()