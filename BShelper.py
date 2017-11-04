#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 15:58:12 2017

@author: milad
"""
from bs4 import BeautifulSoup

class Helper(BeautifulSoup):
    
    def convertBlockToSoup(self, htmlBlock):
        return BeautifulSoup('<html>' + str(htmlBlock) + '</html>')
    
    def elemSelector(self, htmlElement, attributes, source):
        # htmlElement: type of HTML element which has to be selected
        # attributes <attribName: attribValue>: attributes ofan element with expected values
        # source: html source including <html></html> block
        _soup = BeautifulSoup(source, 'html.parser')
        # extract the html element using its attributes  
        #_soup.find(htmlElement, {"class" : className})
        _elem = _soup.find(htmlElement, attributes)
        # convert the block to a soup object
        _elem = self.convertBlockToSoup(_elem)
        return _elem
