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
from Share import Financial, Price
import re
from threading import Thread
from tools import cast
from datetime import datetime
import tools

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
        processes.append( Thread(target=self.balanceSheet, args=(financialObj, )) )
        processes.append( Thread(target=self.setPeriod, args=(financialObj, )) )
        for p in processes:
            p.start()
            p.join()
        # if so far, no result is extracted out of balance sheet and income statement
        # then don't extract analysis info since it is period independent
        if financialObj.__dict__ == Financial().__dict__:
            return financialObj # an empty object
        self.analysis( financialObj )
        return financialObj

    def validateInterval(self):
        # define paterns
        regex_year = r"^\d{4}$"
        regex_quarter = r"(^\d{4}) ([Q][1-4]$)" # Year Q[1-4]

        if self.Interval not in [Interval.customeQuarter, Interval.customeYear]:
            return True

        if self.Interval == Interval.customeQuarter and re.search(regex_quarter, self.customeInterval):
            return True
        elif self.Interval == Interval.customeYear and re.search(regex_year, self.customeInterval):
            return True
        return False

    def setPeriod(self, financialObj):
        _page_source = self.navigation("income_statement")
        _soup = soup.Helper()
        # check if the data is available
        _error = _soup.elemSelector( "div", {"class": "error"}, _page_source )
        if _error is not None:
            print ("Income statement is not available for {}".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        if self.findColumnIndex( _page_source ) == None:
            return
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-rows"}, _page_source )
        financialObj.Period = self.extractUlLi(_block, "Values in Millions", "p")
        self.customeInterval = financialObj.Period
        return
    
    def incomeStatement(self, financialObj):
        _page_source = self.navigation("income_statement")
        _soup = soup.Helper()
        # check if the data is available
        _error = _soup.elemSelector( "div", {"class": "error"}, _page_source )
        if _error is not None:
            print ("Income statement is not available for {}".format( self.shareKey ))
            return
        # find index of the column contains desired interval
        if self.findColumnIndex( _page_source ) == None:
            return
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
        _netIncome = cast( financialObj.NetIncome.replace(',', ''), float, 0 )
        _revenue = cast( financialObj.Revenue.replace(',', ''), float, 1 )
        financialObj.NetProfitMargin = str( round( (_netIncome / max( _revenue, 1)) * 100, 2 ) )
        return
        
    def balanceSheet(self, financialObj):
        _page_source = self.navigation("balance_sheet")
        _soup = soup.Helper()
        # check if the data is available
        _error = _soup.elemSelector( "div", {"class": "error"}, _page_source )
        if _error is not None:
            print ("Balance sheet is not available for {}".format( self.shareKey ), _error)
            return
        # find index of the column contains desired interval
        if self.findColumnIndex( _page_source ) == None:
            return
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, _page_source )
        # extract desired values
        financialObj.Assets  = self.extractUlLi(_block, "Total Assets")
        financialObj.Liabilities = self.extractUlLi(_block, "Total Liabilities")
        financialObj.Equity = self.extractUlLi(_block, "Total Equity")
        financialObj.LiabilitiesAndEquity = self.extractUlLi(_block, "Total Liabilities and Equity")
        return
        
    def analysis(self, financialObj):
        _page_source = self.navigation("analysis")
        # represents the current Interval which has to be crawled
        if self.customeInterval == None:
            print( "The expected period is not set" )
            return 
        # analsis info is period independent, therefore this data has to be
        # set only for the proper period
        if self.isLastInterval() == False:
            return
        # the current date lies in the financial period which has been captured
        # so the analysis info belongs to this time period
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "stock-highlights-right-container"}, _page_source )
        # by default, the UL represents data in analysis part contains only 2 columns
        # and the index of LI which contains the data is always 1
        self.columnIndex = 1
        # read desired values
        financialObj.BookValue = self.extractUlLi(_block, "Book Value/Share")
        financialObj.ReturnonCapital = self.extractUlLi(_block, "Return on Capital")
        financialObj.EPSEstimate = self.extractUlLi(_block, "EPS Estimate")
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
    
    def isLastInterval(self):
        # reported quarterly or yearly data belong to the last quarter or year
        _currentDate = datetime.today()
        if self.Interval in [Interval.lastQuarter, Interval.allQuarters, Interval.customeQuarter]:
            # customeInterval represents the current interval which is selected
            # check if the selected quarter is maximum 3 month older than the current date
            # means is the last interval
            _year = self.customeInterval[:4]
            _quarter = self.customeInterval[4:].strip()
            if _quarter.lower() == "q1":
                return str(_currentDate.year) == _year and _currentDate.month - 3 <= 6
            elif _quarter.lower() == "q2":
                return str(_currentDate.year) == _year and _currentDate.month - 6 <= 6
            elif _quarter.lower() == "q3":
                return str(_currentDate.year - 1) == _year and _currentDate.month - 9 <= 6
            elif _quarter.lower() == "q4":
                return str(_currentDate.year - 1) == _year and 12 - _currentDate.month  >= 6
        else:
            return str(_currentDate.year - 1) == self.customeInterval
        
    def timeLiesInPeriod(self, date = None):
        # expected date format: Year-Month-Day or Year-Month-Day hh:mm:ss
        if type( date ) == str:
            if len( date ) >= 10:
                date = date[:10]
                date = tools.cast( date, datetime, None, "%Y-%m-%d" )
            elif len( date ) < 10:
                print ("Date format is incorrect. Follow Year-Month-Day hh:mm:ss")
                return False
        # check the result of above operation if the conversion returns None
        if type( date ) != datetime or date == None:
            print ("Date format is either None or incorrect")
            return False
        # I expect that the date param is type of datetime
        if self.Interval in [Interval.allYears, Interval.customeYear, Interval.lastYear]:
            return str(date.year) == self.customeInterval
        # check if the date lies in the quarter
        # quarter format: Year Qx 
        _year = self.customeInterval[:4]
        _quarter = self.customeInterval[4:].strip()
        if str(date.year) != _year:
            return False
        if _quarter.lower() == "q1":
            return date.month in [1, 2, 3]
        elif _quarter.lower() == "q2":
            return date.month in [4, 5, 6]
        elif _quarter.lower() == "q3":
            return date.month in [7, 8, 9]
        elif _quarter.lower() == "q4":
            return date.month in [10, 11, 12]

class Price_Info():
    def __init__(self, shareKey):
        self.shareKey = shareKey
    
    def crawl(self):
        _pageSource = self.navigation()
        priceObj = Price()
        # read desired values
        priceObj.Volume = self.extractUlLi(_pageSource, "Volume")
        
        yearRange = self.extractUlLi(_pageSource, "52Wk") # Expected format Low-high
        if '-' in yearRange:
            priceObj.YearHigh = tools.cast( yearRange.split('-')[1].strip(), float)
            priceObj.YearLow = tools.cast( yearRange.split('-')[0].strip(), float )
            
        PE_EPS = self.extractUlLi(_pageSource, "P/E") # expected format P/E (EPS)
        if '(' in PE_EPS:
            priceObj.PE = tools.cast( PE_EPS.split('(')[0].strip(), float )
            priceObj.EPS = tools.cast( PE_EPS.split('(')[1].replace(')', '').strip(), float )
        
        priceObj.Price = self.readPrice( _pageSource )
        return priceObj
        
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
            # the first LI contains the indicator text
            if  indicator.strip().lower() in _elems[0].text.strip().lower():
                return _elems[1].text.strip()
        return None
    
    def readPrice(self, pageSource):
        _soup = soup.Helper()
        _block = _soup.convertToSoup( pageSource )
        _priceElem = _block.find( "span", {"class": "currentval"})
        return tools.cast( _priceElem.text, float )
        
# https://www.msn.com/en-us/money/stockdetailsvnext/financials/income_statement/quarterly/fi-126.1.GOOGL.NAS

## TEST
#find = Financial_Info( "fi-213.1.ADS.ETR", Interval.allQuarters, "2017 Q1" )
#finObj = find.crawl()
#if type(finObj) is list:
#    for obj in finObj:
#        print (obj.__dict__)
#        print ("-----")
#else:
#    print (finObj.__dict__)

#import cProfile
#import re
#import pstats
#cProfile.run('finObj.crawl()', 'restats')
#p = pstats.Stats('restats')
#p.strip_dirs().sort_stats(-1).print_stats()