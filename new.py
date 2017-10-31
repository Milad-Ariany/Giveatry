# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:33:20 2017

@author: Milad
"""

from enum import Enum
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Period (Enum):
    Annual = 0,
    Quarter = 1

class Selector(Enum):
    ID = 0,
    Class = 1
    
class BrowseHelper():
    def click(self, browser, selector, elem, expectedElemID):
        returnObj = None
        try:
            elem.click()
            if selector == Selector.ID:
                returnObj = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, expectedElemID)))
            elif selector == Selector.Class:
                returnObj = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, expectedElemID)))
        finally:
            return returnObj

    def initialize(self):
        return webdriver.Firefox(executable_path=r'/home/milad/billionaireFamily/resources/geckodriver')
            
class SoapHelper():    
    def convertBlockToSoap(self, htmlBlock):
        return BeautifulSoup('<html>' + str(htmlBlock) + '</html>')

class Financial_Info():
    def __init__(self, browser, period, shareKey):
        self.br = browser
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
        if key in ["Revenue", "GrossProfit", "NetIncome", "Assets", "Liabilities", "LiabilitiesAndEquity", "Equity", "EPS"]:
            # navigate to the http://www.msn.com/en-us/money/stockdetails/financials/
            if "financials" not in self.br.current_url:
                BrowseHelper().click(self.br, Selector.ID,
                                     self.br.find_element(By.LINK_TEXT, "Financials"),
                                     "income_statement_text"
                                     )
            ## inner navigation
            # Income statement tab
            if key in ["Revenue", "GrossProfit", "NetIncome", "EPS"]:
                if self.br.find_element_by_id("financials-accordian-list").find_element_by_class_name("active").text.strip().lower() == "income statement":
                    return
                ## Shift to Income statement
                BrowseHelper().click(self.br, Selector.ID,
                                    self.br.find_element_by_id("financials-accordian-list").find_elements_by_tag_name("li")[0],
                                    "barchartcontainerid_Revenue"
                                    )
                return
            # Balance sheet tab
            elif key in ["Assets", "Liabilities", "LiabilitiesAndEquity", "Equity"]:
                if self.br.find_element_by_id("financials-accordian-list").find_element_by_class_name("active").text.strip().lower() == "balance sheet":
                    return
                ## Shift to Balance Sheet
                BrowseHelper().click(self.br, Selector.ID,
                                    self.br.find_element_by_id("financials-accordian-list").find_elements_by_tag_name("li")[1],
                                    "barchartcontainerid_TotalAssets"
                                    )
                return
        elif key in ["NetProfitMargin", "BookValue"]:
            # navigate to the http://www.msn.com/en-us/money/stockdetails/analysis/
            if "analysis" not in self.br.current_url:
                BrowseHelper().click(self.br, Selector.Class, 
                                     self.br.find_element(By.LINK_TEXT, "Analysis"),
                                     "key-ratios-tabs"
                                     )
            ## inner navigation
            #Key statistics tab
            if self.br.find_element_by_class_name("key-ratios-tabs").find_element_by_class_name("active").text.strip().lower() == "key statistics":
                return
            BrowseHelper().click(self.br, Selector.Class,
                                    self.br.find_element_by_class_name("key-ratios-tabs").find_elements_by_tag_name("li")[0],
                                    "keystatistics"
                                    )
            return
        return

    def extractUlLi(self, block, indicator):
        rec = list()
        found = False
        output = list()
        for ultag in block.find_all("ul"):
            for litag in ultag.find_all("li"):
                # if the first li value equals the indicator
                if not found and indicator not in litag.text.strip():
                    rec.append(litag.text.strip())
                    break # next ul
                elif not found:
                    found = True
                    continue # next li
                output.append(litag.text.strip())
            if found: # leave the loops
                break
        if len(output) == 0:
            output.append(None)
            print (rec)
        return output
        
    def blockSelector(self, className):
        soap = BeautifulSoup(self.br.page_source, 'html.parser')
        ## extract a block of the page and convert it to a soap object
        block = SoapHelper().convertBlockToSoap(soap.find("div", {"class" : className}))
        return block
        
    def setRevenue(self):
        self.navigation("Revenue")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Total Revenue")
        self.Revenue = ls[len(ls) - 1] # keep the last record
        return
    
    def setGrossProfit(self):
        self.navigation("GrossProfit")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Gross Profit")
        self.GrossProfit = ls[len(ls) - 1] # keep the last record
        return
    
    def setNetIncome(self):
        self.navigation("NetIncome")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Net Income")
        self.NetIncome = ls[len(ls) - 1] # keep the last record
        return
    
    def setEPS(self):
        self.navigation("EPS")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Basic EPS")
        self.EPS = ls[len(ls) - 1] # keep the last record
        return
        
    def setAssets(self):
        self.navigation("Assets")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Total Assets")
        self.Assets = ls[len(ls) - 1] # keep the last record
        return
    
    def setLiabilities(self):
        self.navigation("Liabilities")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Total Liabilities")
        self.Liabilities = ls[len(ls) - 1] # keep the last record
        return
    
    def setEquity(self):
        self.navigation("Equity")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Total Equity")
        self.Equity = ls[len(ls) - 1] # keep the last record
        return
        
    def setLiabilitiesAndEquity(self):
        self.navigation("LiabilitiesAndEquity")
        block = self.blockSelector("table-data-rows")
        ls = self.extractUlLi(block, "Total Liabilities and Equity")
        self.LiabilitiesAndEquity = ls[len(ls) - 1] # keep the last record
        return
        
    def setBookValue(self):
        self.navigation("BookValue")
        block = self.blockSelector("stock-highlights-right-container")
        ls = self.extractUlLi(block, "Book Value/Share")
        self.BookValue = ls[len(ls) - 1] # keep the last record
        return
                
    def setNetProfitMargin(self):
        self.navigation("NetProfitMargin")
        block = self.blockSelector("stock-highlights-left-container")
        ls = self.extractUlLi(block, "Net Profit Margin")
        self.NetProfitMargin = ls[len(ls) - 1] # keep the last record
        return
    
# define the webdriver
browser = BrowseHelper().initialize()

# page request
#browser.get("http://www.msn.com/en-us/money/stockdetails/fi-126.1.GOOGL.NAS")
finObj = Financial_Info(browser, "Per", "fi-126.1.GOOGL.NAS")
finObj.crawl()

print (finObj.NetIncome, finObj.Revenue, finObj.EPS, finObj.GrossProfit)
print (finObj.Assets, finObj.Equity, finObj.Liabilities, finObj.LiabilitiesAndEquity)
print (finObj.BookValue, finObj.NetProfitMargin)


#http://www.xetra.com/xetra-en/instruments/shares/listing-and-introduction
# http://www.msn.com/en-us/money/stockdetails/fi-200.1.{symbol}.FRA


#el = browser.find_element_by_class_name("key-ratios-tabs")
#print el.find_element_by_class_name("active").text.lower()
#print el.getAttribute("class")
#
#import cProfile
#import re
#import pstats
#cProfile.run('finObj.crawl()', 'restats')
#p = pstats.Stats('restats')
#p.strip_dirs().sort_stats(-1).print_stats()
