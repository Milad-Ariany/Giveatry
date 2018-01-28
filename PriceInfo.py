#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:28:35 2018

@author: milad
"""

import tools
import browser as br
import BShelper as soup

class Price():
    def __init__(self, shareKey):
        self.shareKey = shareKey
        self.Price = None
        self.YearHigh = None # 52 week range
        self.YearLow = None # 52 week range
        self.Volume = None
        self.EPS = None
        self.PE = None
    
    def crawl(self):
        _pageSource = self.navigation()
        # read desired values
        self.Volume = self.extractUlLi(_pageSource, "Volume")
        
        yearRange = self.extractUlLi(_pageSource, "52Wk") # Expected format Low-high
        if '-' in yearRange:
            self.YearHigh = tools.cast( yearRange.split('-')[1].strip(), float)
            self.YearLow = tools.cast( yearRange.split('-')[0].strip(), float )
            
        PE_EPS = self.extractUlLi(_pageSource, "P/E") # expected format P/E (EPS)
        if '(' in PE_EPS:
            self.PE = tools.cast( PE_EPS.split('(')[0].strip(), float )
            self.EPS = tools.cast( PE_EPS.split('(')[1].replace(')', '').strip(), float )
        
        self.Price = self.readPrice( _pageSource )
        return
        
    def navigation(self):
        _url = "https://www.msn.com/en-us/money/stockdetails/"
        _request = "{}{}".format(_url, self.shareKey)
        _pageSource = br.url_request(_request)
        return _pageSource
    
    def extractUlLi(self, pageSource, indicator, elem = "span"):
        # block: UL HTML element block
        _soup = soup.Helper()
        _block = _soup.elemSelector( "ul", {"class": "today-trading-container"}, pageSource)
        # The measure we are looking for
        for _litag in _block.find_all("li"):
            _elems = _litag.find_all(elem)
            if len( _elems ) == 0:
                continue
            # the first LI contains the indicator text
            if  indicator.strip().lower() in _elems[0].text.strip().lower():
                return _elems[1].text.strip()
        return None
    
    def readPrice(self, pageSource):
        _soup = soup.Helper()
        _block = _soup.convertToSoup( pageSource )
        _priceElem = _block.find( "span", {"class": "currentval"})
        return tools.cast( _priceElem.text, float )