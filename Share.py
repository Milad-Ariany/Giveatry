#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 20:08:11 2017

@author: milad
"""
 
from enum import Enum

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
        
class MarketBasedInfo():
    def __init__(self):
        self.Market = None
        self.Currency = None
        self.MSNLink = None
        self.QuarterBasedFinancialInfo = None # = Financial Object
        
class Financial():
    def __init__(self):
        self.Period = None # either Annual or Quarter
        self.Quarter = None # represents quarter report
        self.Year = None # represents annual report
        self.Revenue = None
        self.Gross_Profit = None
        self.Net_Income = None
        self.Assets = None
        self.Liabilities = None
        self.Equity = None
        self.Liabilities_and_Equity = None
        self.EPS = None
        self.Net_Profit_Margin = None
        self.BookValue = None
        
class Price():
    def __init__(self):
        self.Date = None
        self.OpenPrice = None
        self.ClosePrice = None
        self.HighPrice = None
        self.LowPrice = None
        self.Volume = None
        self.PE = None
        self.ForwardPE = None
        self.PEG = None