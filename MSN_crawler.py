#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 20:58:37 2017

@author: milad
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:33:20 2017

@author: Milad
"""

from enum import Enum
import BShelper as soup
import browser as br
import re

class Interval (Enum):
    lastYear = 0,
    allYears = 1,
    customeYear = 2, # format = 2017
    lastQuarter = 3,
    allQuarters = 4,
    customeQuarter = 5 # Format = 2017-Q1

class Financial_Info():
    def __init__(self, shareKey, interval = Interval.lastQuarter, customeInterval = None):
        self.Interval = interval
        self.customeInterval = customeInterval # in combination with Interval.custome[Year/Quarter]
        self.shareKey = shareKey # Format: fi-126.1.GOOGL.NAS
        self.Period = None # represents quarter report
        self.Revenue = None
        self.GrossProfit = None
        self.NetIncome = None
        self.Assets = None
        self.Liabilities = None
        self.Equity = None
        self.LiabilitiesAndEquity = None
        self.EPS = None
        self.NetProfitMargin  = None
        self.BookValue = None
        
    def crawl(self):
        if not self.validateInterval():
            print ("Invalid Interval input \n Please follow samples such as 2017 or 2017 Q1 to 2017 Q4")
            return
        self.incomeStatement()
        self.balanceSheet()
        self.analysis()
        return
        
    def validateInterval(self):
        # define paterns
        regex_year = r"^\d{4}$"
        regex_quarter = r"(^\d{4}) ([Q][1-4]$)" # Year Q[1-4]
        
        if self.Interval not in [Interval.customeQuarter, Interval.customeYear]:
            self.customeInterval = None
            return True
        
        if self.Interval == Interval.customeQuarter and re.search(regex_quarter, self.customeInterval):
            return True
        elif self.Interval == Interval.customeYear and re.search(regex_year, self.customeInterval):
            return True
        return False
    
    def incomeStatement(self):
        _page_source = self.navigation("income_statement")
        if _page_source == None:
            return
        # find index of the column contains desired interval
        _index = self.findColumnIndex( _page_source )
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _page_source )
        # extract Total revenue
        self.Revenue = self.extractUlLi( _block, _index, "Total Revenue" )
        # extract gross profit
        self.GrossProfit = self.extractUlLi(_block,  _index, "Gross Profit")
        # extract net income
        self.NetIncome = self.extractUlLi( _block, _index, "Net Income" )
        # extract basic eps
        self.EPS = self.extractUlLi( _block, _index, "Basic EPS" )
        return
        
    def balanceSheet(self):
        _page_source = self.navigation("balance_sheet")
        if _page_source == None:
            return
        # find index of the column contains desired interval
        _index = self.findColumnIndex( _page_source )
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _page_source )
        # extract Total assets
        self.Assets  = self.extractUlLi(_block, _index, "Total Assets")
        # extract Total liability
        self.Liabilities = self.extractUlLi(_block, _index, "Total Liabilities")
        # extract Total equity
        self.Equity = self.extractUlLi(_block, _index, "Total Equity")
        # extract Total liability and Equity
        self.LiabilitiesAndEquity = self.extractUlLi(_block, _index, "Total Liabilities and Equity")
        return
        
    def analysis(self):
        _page_source = self.navigation("analysis")
        if _page_source == None:
            return
        
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "stock-highlights-right-container"}, _page_source )
        # by default, the UL represents data in analysis part contains only 2 columns
        # and the index of LI which contains the data is always 1
        # extract bookvalue
        self.BookValue = self.extractUlLi(_block, 1, "Book Value/Share")
        # extract Net Profit MArgin
        self.NetProfitMargin = self.extractUlLi(_block, 1, "Net Profit Margin")
        return
    
    def navigation(self, key):
        if key == "income_statement":
            # call https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/annual/{shareKey}
            if self.Interval in [Interval.lastQuarter, Interval.allQuarters, Interval.customeQuarter]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/quarterly/"
            elif self.Interval in [Interval.lastYear, Interval.allYears, Interval.customeYear]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/annual/"
            else:
                return None
            _request = "{}{}".format(_url, self.shareKey)
            _pageSource = br.url_request(_request)
            return _pageSource

        elif key == "balance_sheet":
            # call https://www.msn.com/en-us/money/stockdetailsvnext/financials/balance_sheet/annual/{shareKey}
            if self.Interval in [Interval.lastQuarter, Interval.allQuarters, Interval.customeQuarter]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/balance_sheet/quarterly/"
            elif self.Interval in [Interval.lastYear, Interval.allYears, Interval.customeYear]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/balance_sheet/annual/"
            else:
                return None
            _request = "{}{}".format(_url, self.shareKey)
            _pageSource = br.url_request(_request)
            return _pageSource
        
        elif key == "analysis":
            # call https://www.msn.com/en-us/money/stockdetails/analysis/{shareKey}
            _request = "{}{}".format("https://www.msn.com/en-us/money/stockdetails/analysis/", self.shareKey)
            _pageSource = br.url_request(_request)
            return _pageSource
        
        return None

    def extractUlLi(self, block, index, indicator):
        # block: HTML element block
        # index of desired LI in each UL
        # The measure we are looking for
        # each UL contains information of only one indicator
        for _ultag in block.find_all("ul"):
            _LIs = _ultag.find_all("li")
            if len(_LIs) < index:
                continue
            # the first LI contains the indicator text
            if  indicator in _LIs[0].text.strip() :
                return _LIs[index].text.strip()
        return None
    
    def findColumnIndex(self, page_source):
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-rows"}, page_source )
        if self.Interval in [Interval.lastQuarter,  Interval.lastYear]:
            # extract the first UL element which contains all time intervals
            _intervals = _block.find_all("ul")[0]
            # return index of last element which is last quarter or last year
            _lastElemInx = len( _intervals.find_all("li") ) - 1
            return _lastElemInx 
        if self.Interval in [Interval.customeQuarter,  Interval.customeYear]:
            # extract the first UL element which contains all time intervals
            _intervals = _block.find_all("ul")[0]
            # find the p element which contains the desired interval
            _myInterval = _intervals.find("p", text = self.customeInterval)
            # find its immidiate parent which is a LI element
            while (True):
                _myInterval = _myInterval.parent
                if _myInterval.name == 'li':
                    break
            # return index of last element which is last quarter or last year
            _inx = ((_intervals.index(_myInterval) + 1) / 2) - 1
            return int(_inx)
        return -1
    
finObj = Financial_Info( "fi-126.1.GOOGL.NAS", Interval.customeYear, "2015" )
finObj.crawl()

print (finObj.NetIncome, finObj.Revenue, finObj.EPS, finObj.GrossProfit)
print (finObj.Assets, finObj.Equity, finObj.Liabilities, finObj.LiabilitiesAndEquity)
print (finObj.BookValue, finObj.NetProfitMargin)

#import cProfile
#import re
#import pstats
#cProfile.run('finObj.crawl()', 'restats')
#p = pstats.Stats('restats')
#p.strip_dirs().sort_stats(-1).print_stats()