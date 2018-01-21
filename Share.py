#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 20:08:11 2017

@author: milad
"""
 
from enum import Enum
import tools
import datetime
import re

class MarketPlace (Enum):
    Austria = 0 # fi-194.1.VOW.WBO
    Australia = 1 # fi-146.1.{}.ASX
    Xetra = 2 # fi-213.1.{}.ETR
    Germany = 3 # fi-200.1.{}.FRA
    France = 4 # fi-160.1.{}.PAR
    Spain = 5 # fi-199.1.{}.MCE
    Britain = 6 # fi-151.1.{}.LON       

class Period (Enum):
    Annual = 0,
    Quarter = 1

class Share():
    def __init__(self, symbol=None):
        self.Symbol = symbol
        self.Sector = None # Tech, Industry, ...
        self.CompanyName = None
        self.Country = None
        self.ISIN = None
        self.OpeningPrice = None
        self.OpeningDate = None
        self.WKN = None
        self.MarketBasedInfo = [] # [  Market based info Objects ]

class MarketBasedInfo():
    def __init__(self):
        self.Market = None
        self.Country = None
        self.Currency = None
        self.MSNLink = None
        self.FinancialInfo = [] # [ Financial Objects ]
        self.Pricing = [] # [ Price objects ]

class Financial():
    def __init__(self):
        self.Period = None # represents quarter report
        self.Revenue = None
        self.CostofRevenue = None
        self.GrossProfit = None
        self.NetIncome = None
        self.Assets = None
        self.Liabilities = None
        self.Equity = None
        self.LiabilitiesAndEquity = None
        self.EPS = None
        self.EPSEstimate = None # analysis page
        self.DividendPerShare = None
        self.NetProfitMargin  = None # Net_Income / Revenue
        self.BookValue = None
        self.ReturnonCapital = None

class Price():
    def __init__(self):
        # self.Date = None
        # self.OpenPrice = None
        # self.ClosePrice = None
        self.Price = None
        self.YearHigh = None # 52 week range
        self.YearLow = None # 52 week range
        self.Volume = None
        self.EPS = None
        self.PE = None
        self.ForwardPE = None # analysis page
        self.PEG = None
        self.PBV = None # Price book value
        # self.LowPriceBookValue = None # should be calculated
        
    def calculatePriceBookValue(self, financialObjs):
        # expected format = [ financial objects ] or a single financial Object
        if type(financialObjs) == Financial:
            financialObjs = [ financialObjs ]
        if type(financialObjs) != list:
            return
        
        for finObj in financialObjs:
            if self.isMyFinancialReport( finObj ):
                self.PBV = round( (self.Price / finObj.BookValue) , 2)
                return
        return
    
    def isMyFinancialReport(self, financialObj):
        # reported quarterly or yearly data belong to the last quarter or year
        _myDate = tools.cast( self.Date, datetime )
        if type(_myDate) != datetime:
            print ("Date format is incorrect")
            return False
                # define paterns
        regex_quarter = r"(^\d{4}) ([Q][1-4]$)" # Year Q[1-4]
        if re.search(regex_quarter, financialObj.Period):
            # check if the financial report is maximum 3 month older than the price date
            _year = financialObj.Period[:4]
            _quarter = financialObj.Period[4:].strip()
            if _quarter.lower() == "q1":
                return str(_myDate.year) == _year and _myDate.month - 3 <= 6
            elif _quarter.lower() == "q2":
                return str(_myDate.year) == _year and _myDate.month - 6 <= 6
            elif _quarter.lower() == "q3":
                return str(_myDate.year - 1) == _year and _myDate.month - 9 <= 6
            elif _quarter.lower() == "q4":
                return str(_myDate.year - 1) == _year and 12 - _myDate.month  >= 6
        return False