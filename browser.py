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
    
class SeleniumHelper(webdriver):
    # Click on a ajax button which loads part of a page 
    def ajaxClick(self, browser, selector, elem, expectedElemID):
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
            
def cURL(url):
    _cmd = ' '.join(["curl"] + [url])
    # call the url using cURL from shell
    process = Popen(_cmd, stdout=PIPE, shell=True)
    out, err = process.communicate()
    # return page source 
    return out


class Crawl():
    def __init__(self, stockKey):
        self.key_ = stockKey
        
    def convertBlockToSoap(htmlBlock):
        return BeautifulSoup('<html>' + str(htmlBlock) + '</html>')

    
# define the webdriver
browser = webdriver.Firefox(executable_path=r'D:\Investment\billionaireFamily\resources\geckodriver.exe')

# page request
browser.get("http://www.msn.com/en-us/money/stockdetails/fi-126.1.AAPL.NAS") 
# soap contains the whole page
soap = BeautifulSoup(browser.page_source, 'html.parser')

####### Share Price ########
block = soap.find("div", {"class" : "precurrentvalue"})
# convert it to a soap object
block = BeautifulSoup( '<html>' + str(block) + '</html>')
Price_ = block.text.strip()
####### EPS , P/E #######
# extract a block of the page
block = soap.find("ul", {"class" : "today-trading-container"})
# convert it to a soap object
block = BeautifulSoup( '<html>' + str(block) + '</html>')
# find P/E ratio (EPS) ### Expected format P/E (EPS)
txt = block.find("p", { "title" : "P/E Ratio (EPS)" }).findNext('p').text
# Extract P/E
PE_ = txt[:txt.index("(")] 
# Extract EPS
EPS_ = txt[txt.index("(") + 1:txt.index(")")]

####### Navigate to the Financial tab ########
browser.find_element(By.LINK_TEXT, "Financials").click()
### DELAY ###
#try:
element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "financials-accordian-list")))
#finally:
    # DO THIS

#### Extract historical EPS ####
## Shift to Income statement
ul = browser.find_element_by_id("financials-accordian-list")
li = ul.find_elements_by_tag_name("li")
li[0].click() # Income Statement
## Annual history
ul = browser.find_element_by_id("financials-period-list")
li = ul.find_elements_by_tag_name("li")
li[0].click()
## update soap value
soap = BeautifulSoup(browser.page_source, 'html.parser')
## extract a block of the page and convert it to a soap object
block = convertBlockToSoap(soap.find("div", {"class" : "table-data-rows"}))
## search in unlisted list for historical EPS values
historical_eps = list()
flag = False
for ultag in block.find_all("ul"):
    for litag in ultag.find_all("li"):
        if "Basic EPS" in litag.text.strip():
            flag = True # values in this row have to be stored
            print ("Found")
            continue
        if flag:
            historical_eps.append(litag.text.strip())
    if flag:
        break

historical_eps = [float(x) for x in historical_eps]
ln = len(historical_eps)
Earnings_Growth_Rate = (historical_eps[ln - 1] / historical_eps[ln - 2]) -1 
PEG_ = PE_ / Earnings_Growth_Rate

browser.close()


