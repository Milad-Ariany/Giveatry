# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:33:20 2017

@author: Milad
"""

from enum import Enum
import BShelper as soup
from browser import SeleniumHelper
from browser import Selector
from selenium.webdriver.common.by import By

class Period (Enum):
    Annual = 0,
    Quarter = 1
         
class Financial_Info():
    def __init__(self, browser, period, shareKey):
        self.br = browser # selenium web browser
        self.period = period
        self.shareKey = shareKey
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
        self.loadURL()
    
    def loadURL(self):
        self.br.get("{}{}".format("http://www.msn.com/en-us/money/stockdetails/", self.shareKey))
        return
        
    def crawl(self):
        self.setRevenue()
        self.setNetIncome()
        self.setGrossProfit()
        self.setEPS()
        self.setAssets()
        self.setLiabilities()
        self.setEquity()
        self.setLiabilitiesAndEquity()
        self.setBookValue()  
        self.setNetProfitMargin()
        return
        
    def navigation(self, key):
        _selenium = SeleniumHelper()
        
        if key in ["Revenue", "GrossProfit", "NetIncome", "Assets", "Liabilities", "LiabilitiesAndEquity", "Equity", "EPS"]:
            # Check if the url is correct
            # else navigate to # navigate to the http://www.msn.com/en-us/money/stockdetails/financials/
            # by clicking on "Finanacials" ajax button
            if "financials" not in self.br.current_url:
                _selenium.ajaxClick(self.br, Selector.ID,
                                    self.br.find_element(By.LINK_TEXT, "Financials"),
                                    "income_statement_text"
                                    )
            ## inner navigation
            # Income statement tab
            if key in ["Revenue", "GrossProfit", "NetIncome", "EPS"]:
                if self.br.find_element_by_id("financials-accordian-list").find_element_by_class_name("active").text.strip().lower() == "income statement":
                    return
                ## Shift to Income statement
                _selenium.ajaxClick(self.br, Selector.ID,
                                    self.br.find_element_by_id("financials-accordian-list").find_elements_by_tag_name("li")[0],
                                    "barchartcontainerid_Revenue"
                                    )
                return
            # Balance sheet tab
            elif key in ["Assets", "Liabilities", "LiabilitiesAndEquity", "Equity"]:
                if self.br.find_element_by_id("financials-accordian-list").find_element_by_class_name("active").text.strip().lower() == "balance sheet":
                    return
                ## Shift to Balance Sheet
                _selenium.ajaxClick(self.br, Selector.ID,
                                    self.br.find_element_by_id("financials-accordian-list").find_elements_by_tag_name("li")[1],
                                    "barchartcontainerid_TotalAssets"
                                    )
                return
        elif key in ["NetProfitMargin", "BookValue"]:
            # navigate to the http://www.msn.com/en-us/money/stockdetails/analysis/
            if "analysis" not in self.br.current_url:
                _selenium.ajaxClick(self.br, Selector.Class, 
                                     self.br.find_element(By.LINK_TEXT, "Analysis"),
                                     "key-ratios-tabs"
                                     )
            ## inner navigation
            #Key statistics tab
            if self.br.find_element_by_class_name("key-ratios-tabs").find_element_by_class_name("active").text.strip().lower() == "key statistics":
                return
            _selenium.ajaxClick(self.br, Selector.Class,
                                    self.br.find_element_by_class_name("key-ratios-tabs").find_elements_by_tag_name("li")[0],
                                    "keystatistics"
                                    )
            return
        return

    def extractUlLi(self, block, indicator):
        _rec = list()
        _found = False
        _output = list()
        for _ultag in block.find_all("ul"):
            for _litag in _ultag.find_all("li"):
                # if the first li value equals the indicator
                if not _found and indicator not in _litag.text.strip():
                    _rec.append(_litag.text.strip())
                    break # next ul
                elif not _found:
                    _found = True
                    continue # next li
                _output.append(_litag.text.strip())
            if _found: # leave the loops
                break
        if len(_output) == 0:
            _output.append(None)
            print (_rec)
        return _output
        
    def setRevenue(self):
        self.navigation("Revenue")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Total Revenue")
        self.Revenue = _ls[ len(_ls) - 1 ] # keep the last record
        return
    
    def setGrossProfit(self):
        self.navigation("GrossProfit")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Gross Profit")
        self.GrossProfit = _ls[ len(_ls) - 1 ] # keep the last record
        return
    
    def setNetIncome(self):
        self.navigation("NetIncome")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi( _block, "Net Income" )
        self.NetIncome = _ls[ len(_ls) - 1 ] # keep the last record
        return
    
    def setEPS(self):
        self.navigation( "EPS" )
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi( _block, "Basic EPS" )
        self.EPS = _ls[ len(_ls) - 1 ] # keep the last record
        return
        
    def setAssets(self):
        self.navigation("Assets")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Total Assets")
        self.Assets = _ls[ len(_ls) - 1 ] # keep the last record
        return
    
    def setLiabilities(self):
        self.navigation("Liabilities")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Total Liabilities")
        self.Liabilities = _ls[ len(_ls) - 1 ] # keep the last record
        return
    
    def setEquity(self):
        self.navigation("Equity")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Total Equity")
        self.Equity = _ls[ len(_ls) - 1 ] # keep the last record
        return
        
    def setLiabilitiesAndEquity(self):
        self.navigation("LiabilitiesAndEquity")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "table-data-rows"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Total Liabilities and Equity")
        self.LiabilitiesAndEquity = _ls[ len(_ls) - 1 ] # keep the last record
        return
        
    def setBookValue(self):
        self.navigation("BookValue")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "stock-highlights-right-container"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Book Value/Share")
        self.BookValue = _ls[ len(_ls) - 1 ] # keep the last record
        return

    def setNetProfitMargin(self):
        self.navigation("NetProfitMargin")
        _soup = soup.Helper()
        _block = _soup.elemSelector( "div", {"class": "stock-highlights-left-container"}, self.br.page_source )
        _ls = self.extractUlLi(_block, "Net Profit Margin")
        self.NetProfitMargin = _ls[ len(_ls) - 1 ] # keep the last record
        return
    
# page request
#browser.get("http://www.msn.com/en-us/money/stockdetails/fi-126.1.GOOGL.NAS")
finObj = Financial_Info(SeleniumHelper().initialize(), "Per", "fi-126.1.GOOGL.NAS")
finObj.crawl()

print (finObj.NetIncome, finObj.Revenue, finObj.EPS, finObj.GrossProfit)
print (finObj.Assets, finObj.Equity, finObj.Liabilities, finObj.LiabilitiesAndEquity)
print (finObj.BookValue, finObj.NetProfitMargin)


# http://www.msn.com/en-us/money/stockdetails/fi-200.1.{symbol}.FRA

#
#import cProfile
#import re
#import pstats
#cProfile.run('finObj.crawl()', 'restats')
#p = pstats.Stats('restats')
#p.strip_dirs().sort_stats(-1).print_stats()
