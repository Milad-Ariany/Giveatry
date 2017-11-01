#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 20:53:11 2017

@author: milad
"""

from bs4 import BeautifulSoup
import _thread
from subprocess import PIPE, Popen
            
class SoapHelper():
    # conver a HTML code block to a beautifulsoap object
    def convertBlockToSoap(self, htmlBlock):
        return BeautifulSoup('<html>' + str(htmlBlock) + '</html>')

class Share():
    def __init__(self, symbol):
        self.SYMBOL = symbol
        self.SECTOR = None # Tech, Industry, ...
        self.COMPANYNAME = None
        self.COUNTRY = None
        self.ISIN = None
        self.OPENINGPRICE = None
        self.OPENINGDATE = None      
        
class ShareDiscovery():
    def __init__(self):
        # self.BR = browser
        self.DOMAIN = "http://www.xetra.com/"
        self.BASEURL = "xetra-en/instruments/shares/listing-and-introduction/1533230!search?hitsPerPage={}&pageNum={}"
        self.PAGESIZE = 50
        self.PAGENUM = 0
        self.PAGINGLENGTH = 0
        self.RESULT = dict() # <shareSymbol, shareObj>
        return
        
    def loadURL(self):
        # load a page using the paginSize and pageNum params
        _url = self.DOMAIN + self.BASEURL
        self.BR.get(_url.format(self.PAGESIZE, self.PAGENUM))
        return
    
    def loadcURL(self):
        # generate the url using the paginSize and pageNum params
        _url = self.DOMAIN + self.BASEURL
        return browse(_url.format(self.PAGESIZE, self.PAGENUM))
        
    def readPagingLength(self, pageSource):
        # read the pagination section which is represented as a ul HTML element
        # with nav-page class name
        _block = self.blockSelector("ul", "nav-page", pageSource)
        # expected format
        # <ul>
        # <li> <button value="page number"> 
        # ...
        # </ul>
        _max = 0
        _pageNum = 0
        # find the biggest paging number
        for _li in _block.find_all( "li" ):
            _btn = _li.find( "button" )
            if _btn is not None:
                _pageNum = cast(_btn["value"], int, 0)
                if _pageNum > _max:
                    _max = _pageNum
                
        self.PAGINGLENGTH = _max
        print ( "Paging length is {}".format( self.PAGINGLENGTH ) )
        return
        
    def crawl(self):
        # build the initial url and load it
        _pageSource = self.loadcURL()
        # How many pages are there
        self.readPagingLength(_pageSource)
        # collect url of each share in a list
        _shareURLs = list()
        # read each page
        for i in range(self.PAGINGLENGTH):
            # which page
            self.PAGENUM = i
            # load page
            _pageSource = self.loadcURL()
            # read the current page and select the table which is represented 
            # as a ol HTML element with search-result class name
            _block = self.blockSelector("ol", "search-results", _pageSource)
            # collect all urls in the list and add them to the main list
            _shareURLs += self.readList(_block)
            # call the next pages in a loop and repeat the above process
        
        print ( "Number of elements is {}".format(len(_shareURLs)) )
        # devide the main list to sublist to apply parallelization
        # self.readShareInfo(_shareURLs)
        _chunks = [_shareURLs[ x:x + 100 ] for x in range(0, len( _shareURLs ), 100)]
        # process each chunk in a seprated browser
        for _chk in _chunks:
            _thread.start_new_thread( self.readShareInfo, ( _chk, ))
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
        
    def blockSelector(self, htmlElement, className, pageSource = None):
        if pageSource is None:
            pageSource = self.BR.page_source
        # element: type of HTML element which has to be selected
        # className: class name of the specified HTML element
        _soap = BeautifulSoup(pageSource, 'html.parser')
        ## extract a block of the page and convert it to a soap object
        _block = SoapHelper().convertBlockToSoap(_soap.find(htmlElement, {"class" : className}))
        return _block
    
    def readShareInfo(self, urls):
        print ( "Started" )
        #browser = BrowseHelper().initialize()
        # iterate over share urls
        urls = urls[ :3 ]
        for _url in urls:
            _url = self.DOMAIN + _url
            # open the url and convert it to a soup object
            #browser.get(_url)
            _pageSource = browse(_url)
            # expected structure
            # <dl class="list-tradable-details">
            # <dt> lable </dt>
            # <dd> value </dd>
            shareObj = self.Idonknow(_pageSource)
            self.RESULT[ shareObj.SYMBOL ] = shareObj
            
        print ( "I am finished" )
        return
    
    def Idonknow(self, pageSource):
        shareObj = Share(None)
        
        if pageSource is None:
            return shareObj
        
        # find company name which is laid in <h2 class="main-titel"> COMPANY <h2>
        shareObj.COMPANYNAME = BeautifulSoup(pageSource, "html.parser").find("h2", {"class" : "main-title"}).get_text()
        
        # Other info is structed as
        # <dl class="list-tradable-details">
        # <dt> lable </dt>
        # <dd> value </dd>
        _block = self.blockSelector("dl", "list-tradable-details", pageSource)
        # read each pare of label and values
        for _dt in _block.find_all( "dt" ):
            if "sector" in _dt.get_text().lower():
                # find the next dd element which stores the value
                _dd = _dt.find_next_sibling("dd")
                shareObj.SECTOR = _dd.get_text()
                continue
            elif "country" in _dt.get_text().lower():
                # find the next dd element which stores the value
                _dd = _dt.find_next_sibling("dd")
                shareObj.COUNTRY = _dd.get_text()
                continue
            elif "symbol" in _dt.get_text().lower():
                # find the next dd element which stores the value
                _dd = _dt.find_next_sibling("dd")
                shareObj.SYMBOL= _dd.get_text()
                continue
            elif "isin" in _dt.get_text().lower():
                # find the next dd element which stores the value
                _dd = _dt.find_next_sibling("dd")
                shareObj.ISIN = _dd.get_text()
                continue
            elif "first trading day" in _dt.get_text().lower():
                # find the next dd element which stores the value
                _dd = _dt.find_next_sibling("dd")
                shareObj.OPENINGDATE = _dd.get_text()
                continue
            elif "first price" in _dt.get_text().lower():
                # find the next dd element which stores the value
                _dd = _dt.find_next_sibling("dd")
                shareObj.OPENINGPRICE = _dd.get_text()
                
        return shareObj

def cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        print ( "Error in casting {} to {}".format(val, to_type) )
        return default

def browse(url):
    _cmd = ' '.join(["curl"] + [url])
    # call the url using cURL from shell
    process = Popen(_cmd, stdout=PIPE, shell=True)
    out, err = process.communicate()
    # return page source 
    return out
    
discoveryObj = ShareDiscovery()
discoveryObj.crawl()
# print ( len(discoveryObj.RESULT) )

