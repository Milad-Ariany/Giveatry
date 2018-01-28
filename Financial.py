#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 11:10:43 2018

@author: milad
"""

from enum import Enum
import BShelper as soup
import browser as br
from threading import Thread
from tools import cast
import re

_columnShift_ = 0 # no shift
_columnIndex_ = 1 # the least column
_interval_ = None
_customeInterval_ = None # used in combination with Interval.custome[Year/Quarter]

class Interval (Enum):
    lastYear = 0,
    allYears = 1,
    customeYear = 2, # format = 2017
    lastQuarter = 3,
    allQuarters = 4,
    customeQuarter = 5 # Format = 2017 Q1
    
class FinancialInfo():
    def __init__(self, shareKey):
        self.shareKey = shareKey # fi.213.APPL.12
        self.Period = None # represents time frame
        self.Revenue = None
        self.CostofRevenue = None
        self.GrossProfit = None
        self.NetIncome = None
        self.Assets = None
        self.Liabilities = None
        self.Equity = None
        self.LiabilitiesAndEquity = None
        self.EPS = None
        self.DividendPerShare = None
        self.NetProfitMargin  = None # Net_Income / Revenue
    
    def crawl(self):
        if not self.validateInterval():
            print ("Invalid Interval input \n Please follow samples such as 2017 or 2017 Q1 to 2017 Q4")
            return
        
        processes = []
        processes.append( Thread(target=self.incomeStatement, args=()) )
        processes.append( Thread(target=self.balanceSheet, args=()) )
        processes.append( Thread(target=self.setPeriod, args=()) )
        for p in processes:
            p.start()
            
        for p in processes:
            p.join()
       
#        self.incomeStatement()
#        self.balanceSheet()
#        self.setPeriod()           
        return
    
    def validateInterval(self):
        global _customeInterval_
        global _interval_
        
        # define paterns
        regex_year = r"^\d{4}$"
        regex_quarter = r"(^\d{4}) ([Q][1-4]$)" # Year Q[1-4]

        if _interval_ not in [Interval.customeQuarter, Interval.customeYear]:
            return True

        if _interval_ == Interval.customeQuarter:
            return re.search(regex_quarter, _customeInterval_)
        elif _interval_ == Interval.customeYear:
            return re.search(regex_year, _customeInterval_)
        
    def setPeriod(self):
        global _customeInterval_ 
        
        _pageSource = self.navigation("income_statement")
        _soup = soup.Helper()
        # check if the data is available
        _error = _soup.elemSelector( "div", {"class": "error"}, _pageSource )
        if _error is not None:
            print ("Income statement is not available for {}".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        if self.findColumnIndex( _pageSource ) == None:
            return
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-rows"}, _pageSource )
        self.Period = self.extractUlLi(_block, "Values in Millions", "p")
        _customeInterval_ = self.Period
        return
    
    def incomeStatement(self):
        _pageSource = self.navigation("income_statement")
        _soup = soup.Helper()
        # check if the data is available
        _error = _soup.elemSelector( "div", {"class": "error"}, _pageSource )
        if _error is not None:
            print ("Income statement is not available for {}".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        if self.findColumnIndex( _pageSource ) == None:
            return
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _pageSource )
        # read the desired info
        self.Revenue = self.extractUlLi( _block, "Total Revenue" )
        self.CostofRevenue = self.extractUlLi( _block, "Cost of Revenue" )
        self.GrossProfit = self.extractUlLi( _block, "Gross Profit")
        self.NetIncome = self.extractUlLi( _block, "Net Income" )
        self.EPS = self.extractUlLi( _block, "Basic EPS" )
        self.DividendPerShare = self.extractUlLi( _block, "Dividend Per Share" )
        # calculate Net Profit Margin
        if self.NetIncome is None and self.Revenue is None:
            return
        _netIncome = cast( self.NetIncome.replace(',', ''), float, 0 )
        _revenue = cast( self.Revenue.replace(',', ''), float, 1 )
        self.NetProfitMargin = str( round( (_netIncome / max( _revenue, 1)) * 100, 2 ) )
        return
        
    def balanceSheet(self):
        _pageSource = self.navigation("balance_sheet")
        _soup = soup.Helper()
        # check if the data is available
        _error = _soup.elemSelector( "div", {"class": "error"}, _pageSource )
        if _error is not None:
            print ("Balance sheet is not available for {}".format( self.shareKey ), _error)
            return
        # find index of the column contains desired interval
        if self.findColumnIndex( _pageSource ) == None:
            return
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _pageSource )
        # extract desired values
        self.Assets  = self.extractUlLi(_block, "Total Assets")
        self.Liabilities = self.extractUlLi(_block, "Total Liabilities")
        self.Equity = self.extractUlLi(_block, "Total Equity")
        self.LiabilitiesAndEquity = self.extractUlLi(_block, "Total Liabilities and Equity")
        return
    
    def navigation(self, key):
        global _interval_
        
        if key == "income_statement":
            # call https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/annual/{shareKey}
            if _interval_ in [Interval.lastQuarter, Interval.allQuarters, Interval.customeQuarter]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/quarterly/"
            elif _interval_ in [Interval.lastYear, Interval.allYears, Interval.customeYear]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/annual/"
            else:
                return None
            _request = "{}{}".format(_url, self.shareKey)
            _pageSource = br.url_request(_request)
            return _pageSource

        elif key == "balance_sheet":
            # call https://www.msn.com/en-us/money/stockdetailsvnext/financials/balance_sheet/annual/{shareKey}
            if _interval_ in [Interval.lastQuarter, Interval.allQuarters, Interval.customeQuarter]:
                _url = "https://www.msn.com/en-us/money/stockdetailsvnext/financials/balance_sheet/quarterly/"
            elif _interval_ in [Interval.lastYear, Interval.allYears, Interval.customeYear]:
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
    
    def extractUlLi(self, block, indicator, elem = "li"):
        global _columnIndex_
        
        if _columnIndex_ < 1 or _columnIndex_ is None:
            return None
        # block: HTML element block
        # index of desired LI in each UL
        # The measure we are looking for
        # each UL contains information of only one indicator
        for _ultag in block.find_all("ul"):
            _elems = _ultag.find_all(elem)
            if len(_elems) < _columnIndex_:
                continue
            # the first LI contains the indicator text
            if  indicator.strip().lower() in _elems[0].text.strip().lower():
                return _elems[_columnIndex_].text.strip()
        return None
    
    def findColumnIndex(self, pageSource):
        # _columnShift_: to _columnShift_ the index
        global _columnShift_
        global _columnIndex_
        global _customeInterval_
        global _interval_
        
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-rows"}, pageSource )
        if _interval_ in [Interval.lastQuarter,  Interval.lastYear]:
            # extract the first UL element which contains all time intervals
            _intervals = _block.find_all("ul")[0]
            # return index of last element which is last quarter or last year
            _columnIndex_ = ( len( _intervals.find_all("li") ) - 1 ) + _columnShift_
            return _columnIndex_ 
        if _interval_ in [Interval.customeQuarter,  Interval.customeYear]:
            # extract the first UL element which contains all time intervals
            #if type(_block.find_all("ul")) is not list:
            #    print (_block.find_all("ul"))
            _intervals = _block.find_all("ul")[0]
            print ("intervals len" + str( len(_intervals)))
            # find the p element which contains the desired interval
            _myInterval = _intervals.find("p", text = _customeInterval_)
            if _myInterval is None:
                return None
            # find its immidiate parent which is a LI element
            while (True):
                _myInterval = _myInterval.parent
                if _myInterval.name == 'li':
                    break
            # return index of my interval
            _columnIndex_ = cast( (_intervals.index(_myInterval) - 1) / 2, int) + _columnShift_
            return _columnIndex_
        return None

class MultiFinancialInfo():
    def __init__(self, shareKey):
        self.shareKey = shareKey # Format: fi-126.1.GOOGL.NAS
        self.results = []
        
    def crawl(self):
        global _interval_
        global _columnShift_
        
        # grab info for the last year
        if _interval_ == Interval.allYears:
            _interval_ = Interval.lastYear
        elif _interval_ == Interval.allQuarters:
            _interval_ = Interval.lastQuarter
        
        while (True):
            financialObj = FinancialInfo( self.shareKey )
            financialObj.crawl()
            # if the produced object is empty it means all existing periods are covered
            if financialObj.__dict__ == FinancialInfo( self.shareKey ).__dict__:
                break
            self.results.append(financialObj)
            # shift one interval (year / quarter) back
            _columnShift_ = _columnShift_ - 1
        return