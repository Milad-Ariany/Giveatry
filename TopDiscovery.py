#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: milad
"""

import BShelper as soup
import browser as br
from Share import Share
from Share import MarketPlace
import json
from threading import Thread
import datetime

class Worldwide():
    def __init__(self):
        self.DOMAIN = "https://tradingeconomics.com/"
        self.RESULT = dict() # <shareSymbol, shareObj>
        self.soup = soup.Helper()
        return
                
    def crawl(self):
        # build the initial url and load it
        _pageSource = self.loadURL("stocks")
        # collect url of each market in a list
        _marketURLs = list()
        # read each market
        _block = self.soup.convertToSoup( _pageSource )
        for _table in _block.find_all( "table" ):
            # read the current table and collect the market links 
            for _a in _table.find_all( 'a', href=True ):
                _marketURLs.append( _a["href"] )
        # devide the main list to chunks to apply parallelization
        _chunksize = 20
        _chunks = [_marketURLs[ x:x + _chunksize ] for x in range(0, len (_marketURLs), _chunksize)]
        # process chunks in parallel
        processes = []
        for _chk in _chunks:
            processes.append(Thread(target=self.readShareInfo, args=(_chk, )))
            # start the new thread
            processes[ len (processes) -1 ].start()
        for p in processes:
            p.join()
        #self.readShareInfo(_marketURLs)
        return
   
    def loadURL(self, url = ""):
        # generate the url using the paginSize and pageNum params
        _url = self.DOMAIN + url
        return br.url_request(_url)
   
    def readShareInfo(self, urls):
        # iterate over share urls
        print ( "I started with %s" % ( len(urls) ) )
        i = datetime.datetime.now()
        for _url in urls:
            _pageSource = self.loadURL( _url )
            print ( datetime.datetime.now() - i)
            i = datetime.datetime.now()
            self.renderTable( _pageSource )
        print ( "I finished" )
        return
    
    def renderTable(self, _pageSource):
        _block = self.soup.convertToSoup( _pageSource )
        for _table in _block.find_all( "table" ):
            # select the table which contains companies infos
            if "Components" in str(_table):
                # read the current table and collect the company infos
                for _tr in _table.find_all( 'tr' ):
                    if _tr.find( 'td' ):
                        _shareObj = Share()
                        _shareObj.Symbol = _tr.find_all('td')[0].text.strip()
                        _shareObj.CompanyName = _tr.find_all('td')[1].text.strip()
                        self.RESULT[ _shareObj.Symbol ] = _shareObj
                        
obj = Worldwide()
obj.crawl()