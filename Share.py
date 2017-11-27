#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 20:08:11 2017

@author: milad
"""
 
from enum import Enum

class MarketPlace (Enum):
    Xetra = 0

class Share():
    def __init__(self, symbol=None):
        self.SYMBOL = symbol
        self.SECTOR = None # Tech, Industry, ...
        self.COMPANYNAME = None
        self.COUNTRY = None
        self.MARKET = None
        self.ISIN = None
        self.OPENINGPRICE = None
        self.OPENINGDATE = None
        self.MSNSYMBOL = None
        
    def resolveSymbolCountry(self):
        if self.MARKET == MarketPlace.Xetra:
            self.MSNSYMBOL = "fi-200.1.{}.FRA".format(self.SYMBOL)
        else:
            print ( "NOT GERMANY {} {}".format(self.SYMBOL, self.COUNTRY) )
        return