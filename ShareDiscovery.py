#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 20:53:11 2017

@author: milad
"""


from enum import Enum
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import _thread

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
    # conver a HTML code block to a beautifulsoap object
    def convertBlockToSoap(self, htmlBlock):
        return BeautifulSoup('<html>' + str(htmlBlock) + '</html>')

class share():
    def __init__(self, symbol):
        self._symbol = symbol
        self.sector = None # Tech, Industry, ...
        self._companyName = None # company Name
        self._isin = None
        self._openingPrice = None
        self._openingDate = None      
        
class shareDiscovery():
    def __init__(self, browser):
        self.BR = browser
        self.DOMAIN = "http://www.xetra.com/"
        self.BASEURL = "xetra-en/instruments/shares/listing-and-introduction/1533230!search?hitsPerPage={}&pageNum={}"
        self.PAGESIZE = 50
        self.PAGENUM = 0
        self.PAGINGLENGTH = 0
        self.loadURL()
        self.readPagingLength()
        return
        
    def loadURL(self):
        # load a page using the paginSize and pageNum params
        _url = self.DOMAIN + self.BASEURL
        self.BR.get(_url.format(self.PAGESIZE, self.PAGENUM))
        return
        
    def nextPage(self):
        self.PAGENUM += 1
        self.loadURL()
        return
    
    def readPagingLength(self):
        # read the pagination section which is represented as a ul HTML element
        # with nav-page class name
        _block = self.blockSelector("ul", "nav-page")
        # expected format
        # <ul>
        # <li> <button value="page number"> 
        # ...
        # </ul>
        _max = 0
        _num = 0
        # find the biggest paging number
        for _li in _block.find_all( "li" ):
            _btn = _li.find( "button" )
            if _btn is not None:
                _num = _btn["value"]
            if int(_num) > _max:
                _max = int(_num)
                
        self.PAGINGLENGTH = _max
        print (self.PAGINGLENGTH)
        return
        
    def crawl(self):
        # find paging length
        
        # collect url of each share in a list
        _shareURLs = list()
        # read the current page and select the table which is represented 
        # as a ol HTML element with search-result class name
        _block = self.blockSelector("ol", "search-results")
        # collect all urls in the list and add them to the main list
        _shareURLs += self.readList(_block)
        # call the next pages in a loop and repeat the above process
        for i in range(self.PAGINGLENGTH):
            self.nextPage()
            _block = self.blockSelector("ol", "search-results")
            _shareURLs += self.readList(_block)
        
        print (len(_shareURLs))
        # open the url of each share to collect more information about that
        return
    
    def readList(self, block):
        # the expected structure:
        # <ol> <li></li> <li></li> ... </ol>
        # each li represents an individual share
        
        # return all href values in the list
        _hrefList = list()
        for _li in block.find_all( "li" ):
            # collect the href value of the links
            for _a in _li.find_all( 'a', href=True ):
                _hrefList.append( _a["href"] )
        
        return _hrefList
        
    def blockSelector(self, htmlElement, className):
        # element: type of HTML element which has to be selected
        # className: class name of the specified HTML element
        _soap = BeautifulSoup(self.BR.page_source, 'html.parser')
        ## extract a block of the page and convert it to a soap object
        _block = SoapHelper().convertBlockToSoap(_soap.find(htmlElement, {"class" : className}))
        return _block
    
def tmp1(a1):
    print (a1)    
# define the webdriver
browser = BrowseHelper().initialize()
discoveryObj = shareDiscovery(browser)
print (discoveryObj.PAGINGLENGTH)
discoveryObj.crawl()
