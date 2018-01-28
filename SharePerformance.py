#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:29:53 2018

@author: milad
"""

import tools
import browser as br
import BShelper as soup
from PriceInfo import Price
import Financial

class Performance():
    def __init__(self, shareKey):
        self.shareKey = shareKey
        self.ForwardPE = None # analysis page
        self.PEG = None
        self.PBV = None # Price book value
        self.ReturnonCapital = None
        self.BookValue = None
        self.EPSEstimate = None
        self.PPEBV = None
        self.PriceInfo = None
        self.FinancialInfo = None # [ Financial Objects ]
        
    def navigation(self):
        _url = "https://www.msn.com/en-us/money/stockdetails/analysis/"
        _request = "{}{}".format(_url, self.shareKey)
        _pageSource = br.url_request(_request)
        return _pageSource
    
    def crawl(self):
        self.analysis()
        self.setPriceInfo()
        self.setFinancialInfo()
        self.setPBV()
        self.setPPEBV()
        return
        
    def analysis(self):
        _pageSource = self.navigation()        
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "stock-highlights-right-container"}, _pageSource )
        # read desired values
        self.BookValue = self.extractUlLi(_block, "Book Value/Share")
        self.ReturnonCapital = self.extractUlLi(_block, "Return on Capital")
        self.EPSEstimate = self.extractUlLi(_block, "EPS Estimate")
        self.PEG = self.extractUlLi(_block, "PEG")
        self.ForwardPE = self.extractUlLi(_block, "Forward P/E")
        return
    
    def extractUlLi(self, block, indicator, elem = "li"):
        # block: HTML element block
        # index of desired LI in each UL
        # The measure we are looking for
        # each UL contains information of only one indicator
        for _ultag in block.find_all("ul"):
            _elems = _ultag.find_all(elem)
            if len( _elems ) == 0:
                continue
            # the first LI contains the indicator text
            if  indicator.strip().lower() in _elems[0].text.strip().lower():
                return _elems[1].text.strip()
        return None
    
    def setFinancialInfo(self):
        # set global vars
        Financial._interval_ = Financial.Interval.allYears
        # crawl financial info
        financialObjs = Financial.MultiFinancialInfo( self.shareKey )   
        financialObjs.crawl()
        # set financial info
        self.FinancialInfo = financialObjs.results
        return
    
    def setPriceInfo(self):
        # crawl price related info
        priceObj = Price( self.shareKey )
        priceObj.crawl()
        # set price info
        self.PriceInfo = priceObj
        return
    
    def setPBV(self):
        if self.BookValue == None:
            return
        self.PBV = round( (tools.cast( self.PriceInfo.Price, float, 0 ) / tools.cast( self.BookValue, float, 1 )) , 2)
        return
    
    def setPPEBV(self):
        self.PPEBV = round( tools.cast( self.PBV, float, 0) * tools.cast( self.PriceInfo.PE, float, 0) )

    def setPEG(self):
        return
    
    def setForwardPE():
        return