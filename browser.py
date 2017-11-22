# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 12:28:56 2017

@author: Milad
"""

 
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from subprocess import PIPE, Popen


class BrowserActions(Enum):
    click = 0
    
class Selector(Enum):
    ID = 0,
    Class = 1
    
class SeleniumHelper():
    # Click on a ajax button which loads part of a page 
    def ajaxClick(self, browser, selector, button, expectedElemID):
        # browser: Firefox webdriver
        # selector: Enum which specifies how to select an element in a page
        # button: the button which has to be pushed
        # expectedElemID: a html element which we expect to be discovered after ajax is loaded
        returnObj = None
        try:
            # click the ajax button
            button.click()
            if selector == Selector.ID:
                # wait for 20secs that the ajax is loaded
                # or until the expected element which is result of ajax load is shown up
                returnObj = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, expectedElemID)))
            elif selector == Selector.Class:
                returnObj = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, expectedElemID)))
        finally:
            return returnObj

    def initialize(self):
       return webdriver.Firefox(executable_path=r'/home/milad/billionaireFamily/resources/geckodriver')
            
def cURL(url):
    _cmd = ' '.join(["curl"] + [url])
    # call the url using cURL from shell
    process = Popen(_cmd, stdout=PIPE, shell=True)
    out, err = process.communicate()
    # return page source 
    return out