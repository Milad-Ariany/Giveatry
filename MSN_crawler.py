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
from Share import Financial
import re
from threading import Thread

class Interval (Enum):
    lastYear = 0,
    allYears = 1,
    customeYear = 2, # format = 2017
    lastQuarter = 3,
    allQuarters = 4,
    customeQuarter = 5 # Format = 2017 Q1

class Financial_Info():
    def __init__(self, shareKey, interval = Interval.lastQuarter, customeInterval = None):
        self.Interval = interval
        self.customeInterval = customeInterval # in combination with Interval.custome[Year/Quarter]
        self.shareKey = shareKey # Format: fi-126.1.GOOGL.NAS
        self.shift = 0
        self.columnIndex = 1 # the least column
        
    def crawl(self):
        if not self.validateInterval():
            print ("Invalid Interval input \n Please follow samples such as 2017 or 2017 Q1 to 2017 Q4")
            return
        if self.Interval in [Interval.allQuarters, Interval.allYears]:
            return self.multiplePeriods()
        else:
            return self.singlePeriod()
    
    def multiplePeriods(self):
        result = []
        if self.Interval == Interval.allYears:
            self.Interval = Interval.lastYear
        elif self.Interval == Interval.allQuarters:
            self.Interval = Interval.lastQuarter
        
        while (True):
            financialObj = self.singlePeriod()
            # if the produced object is empty it means all existing periods are covered
            if financialObj.__dict__ == Financial().__dict__:
                break
            result.append(financialObj)
            # check the previous info
            self.shift -= 1
        return result
        
    def singlePeriod(self):
        financialObj = Financial()
        processes = []
        processes.append( Thread(target=self.incomeStatement, args=(financialObj, )) )
        #_page_source = self.incomeStatement( financialObj )
        processes.append( Thread(target=self.balanceSheet, args=(financialObj, )) )
        #self.balanceSheet( financialObj )
        for p in processes:
            p.start()
            p.join()
        # if so far, no result is extracted out of balance sheet and income statement
        # then don't extract analysis info since it is period independent
        if financialObj.__dict__ == Financial().__dict__:
            return financialObj # an empty object
        processes = []
        processes.append( Thread(target=self.analysis, args=(financialObj, )) )
        # self.analysis( financialObj )
        processes.append( Thread(target=self.setPeriod, args=(financialObj, )) )
        # self.setPeriod( _page_source, financialObj )
        for p in processes:
            p.start()
            p.join()
        return financialObj

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
    
    def setPeriod(self, financialObj):
        _page_source = self.navigation("income_statement")
        if _page_source == None:
            print ("Income statement source page for {} is not loaded correctly".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        self.findColumnIndex( _page_source )
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-rows"}, _page_source )
        financialObj.Period  = self.extractUlLi(_block, "Values in Millions", "p")
        return
    
    def incomeStatement(self, financialObj):
        _page_source = self.navigation("income_statement")
        if _page_source == None:
            print ("Income statement source page for {} is not loaded correctly".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        self.findColumnIndex( _page_source )
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _page_source )
        # read the desired info
        financialObj.Revenue = self.extractUlLi( _block, "Total Revenue" )
        financialObj.CostofRevenue = self.extractUlLi( _block, "Cost of Revenue" )
        financialObj.GrossProfit = self.extractUlLi( _block, "Gross Profit")
        financialObj.NetIncome = self.extractUlLi( _block, "Net Income" )
        financialObj.EPS = self.extractUlLi( _block, "Basic EPS" )
        financialObj.DividendPerShare = self.extractUlLi( _block, "Dividend Per Share" )
        # calculate Net Profit Margin
        if financialObj.NetIncome is None and financialObj.Revenue is None:
            return
        _netIncome = float( financialObj.NetIncome.replace(',', '') )
        _revenue = float( financialObj.Revenue.replace(',', '') )
        financialObj.NetProfitMargin = round( (_netIncome / _revenue) * 100, 2 )
        return
        
    def balanceSheet(self, financialObj):
        _page_source = self.navigation("balance_sheet")
        if _page_source == None:
            print ("Balance sheet source page for {} is not loaded correctly".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        self.findColumnIndex( _page_source )
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _page_source )
        # extract desired values
        financialObj.Assets  = self.extractUlLi(_block, "Total Assets")
        financialObj.Liabilities = self.extractUlLi(_block, "Total Liabilities")
        financialObj.Equity = self.extractUlLi(_block, "Total Equity")
        financialObj.LiabilitiesAndEquity = self.extractUlLi(_block, "Total Liabilities and Equity")
        return
        
    def analysis(self, financialObj):
        _page_source = self.navigation("analysis")
        if _page_source == None:
            print ("Analysis source page for {} is not loaded correctly".format( self.shareKey ))
            return
        
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "stock-highlights-right-container"}, _page_source )
        # by default, the UL represents data in analysis part contains only 2 columns
        # and the index of LI which contains the data is always 1
        self.columnIndex = 1
        # read desired values
        financialObj.BookValue = self.extractUlLi(_block, "Book Value/Share")
        financialObj.ReturnonCapital = self.extractUlLi(_block, "Return on Capital")
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

    def extractUlLi(self, block, indicator, elem = "li"):
        if self.columnIndex < 1 or self.columnIndex is None:
            return None
        # block: HTML element block
        # index of desired LI in each UL
        # The measure we are looking for
        # each UL contains information of only one indicator
        for _ultag in block.find_all("ul"):
            _elems = _ultag.find_all(elem)
            if len(_elems) < self.columnIndex:
                continue
            # the first LI contains the indicator text
            if  indicator.strip().lower() in _elems[0].text.strip().lower():
                return _elems[self.columnIndex].text.strip()
        return None
    
    def findColumnIndex(self, page_source):
        # shift: to shift the index
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-rows"}, page_source )
        if self.Interval in [Interval.lastQuarter,  Interval.lastYear]:
            # extract the first UL element which contains all time intervals
            _intervals = _block.find_all("ul")[0]
            # return index of last element which is last quarter or last year
            self.columnIndex = ( len( _intervals.find_all("li") ) -  1 ) + self.shift
            return self.columnIndex 
        if self.Interval in [Interval.customeQuarter,  Interval.customeYear]:
            # extract the first UL element which contains all time intervals
            if type(_block.find_all("ul")) is not list:
                print (_block.find_all("ul"))
            _intervals = _block.find_all("ul")[0]
            # find the p element which contains the desired interval
            _myInterval = _intervals.find("p", text = self.customeInterval)
            if _myInterval is None:
                return None
            # find its immidiate parent which is a LI element
            while (True):
                _myInterval = _myInterval.parent
                if _myInterval.name == 'li':
                    break
            # return index of last element which is last quarter or last year
            self.columnIndex = ((_intervals.index(_myInterval) + 1) / 2) + self.shift
            return self.columnIndex
        return None

# https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/quarterly/fi-126.1.GOOGL.NAS
find = Financial_Info( "fi-213.1.ADS.ETR", Interval.allYears, "2017 Q1" )
finObj = find.crawl()

if type(finObj) is list:
    for obj in finObj:
        print (obj.__dict__)
        print ("-----")
else:
    print (finObj.__dict__)

#import cProfile
#import re
#import pstats
#cProfile.run('finObj.crawl()', 'restats')
#p = pstats.Stats('restats')
#p.strip_dirs().sort_stats(-1).print_stats()