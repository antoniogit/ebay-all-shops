# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup, SoupStrainer
import distance

import httplib2
import requests
from urlparse import urlparse
from requests.exceptions import ConnectionError
import re
import sys
import csv
import requests as rq
import validators
import time
import csv
import random

import json
from urllib2 import Request, urlopen, URLError
# sys.setrecursionlimit(200)
reload(sys)
sys.setdefaultencoding('utf-8')

key = "AIzaSyDwF1dAKAPZEZpXlW57iPI8oRutmfnTC-E"
proxies_list = []
proxies = {}
shops = []

shopNames = []
urlsToVisit = []
proxies_list = []
proxies  = {}
currentUrl = ''
userAgent = ''
visitedShops = []

userAgentsList = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
]

def getProxies(fileName) :
    index = 0
    ifile = open(fileName, "rb")
    reader = csv.reader(ifile)

    for row in reader:
        if index >0 :
            proxies_list.append(row[0] + ":" + row[1])
        index += 1


def chooseProxies() :
    proxies = {
            'http': random.choice(proxies_list)
        }

def chooseUserAgent():
    userAgent = random.choice(userAgentsList)


# check if the proxy is good and reassign one untill a good one is found
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8,ro;q=0.6',
    'referer': 'https://www.google.co.uk/',
    'User-Agent': userAgent,
    'x-chrome-uma-enabled': '0',
}

def changeProxy(url):

    goodProxy = False
    tries = 0
    soupProxy = ''
    while goodProxy == False and tries <= 2:
        chooseProxies()
        try:
            tries += 1
            chooseUserAgent();
            r = requests.get(url, proxies=proxies, headers=headers, timeout=5)
            html = r.text
            soupProxy = BeautifulSoup(html)
            if len(soupProxy) > 0 :
                goodProxy = True
        except ConnectionError:
            goodProxy = False
        except TimeoutException, err:
            goodProxy = False
        except :
            goodProxy = False
            return soupProxy
    return soupProxy

def getShopDetails(ebayShopId, categoryLink, page) :
    homeUrl = "https://www.ebay.co.uk/usr/"
    homeUrlEnding = "?rt=nc"
    # time.sleep(2)
    shopUrl = homeUrl + ebayShopId + homeUrlEnding
    soupShop = changeProxy(shopUrl)
    top5SoldItems = soupShop.findAll('span', class_="price fl bold")
    soldItem1 = ''
    soldItem2 = ''
    soldItem3 = ''
    soldItem4 = ''
    soldItem5 = ''

    if top5SoldItems :
        if 0 < len(top5SoldItems) :
            soldItem1 = top5SoldItems[0].text
        if 1 < len(top5SoldItems) :
            soldItem2 = top5SoldItems[1].text
        if 2 < len(top5SoldItems) : 
            soldItem3 = top5SoldItems[2].text
        if 3 < len(top5SoldItems) : 
            soldItem4 = top5SoldItems[3].text
        if 4 < len(top5SoldItems) :
            soldItem5 = top5SoldItems[4].text

    sellerRatingIs = soupShop.findAll('i', class_="gspr redStar star")
    if sellerRatingIs :
        # get seller rating
        sellerRatingI = sellerRatingIs[0]
        rating = sellerRatingI['aria-label']

        # get business details
        businessDetailsRows = soupShop.findAll('div', class_="bsi_row")
        businessName = ''
        businessAddress = ''
        phone = ''
        email = ''
        
        if businessDetailsRows :

            for businessDetailsRow in businessDetailsRows:
                bsiLabels = businessDetailsRow.findAll('span', class_='bsi_cell_label')
                bsiLabel = bsiLabels[0]

                if "Business name:" in bsiLabel.text :
                    bsiCellValues = businessDetailsRow.findAll('span', class_='bsi_cell_value')
                    bsiCellValue = bsiCellValues[0]
                    businessName = bsiCellValue.text

                if "Address:" in bsiLabel.text :
                    bsiCellValues = businessDetailsRow.findAll('span', class_='bsi_cell_value')
                    bsiCellValue = bsiCellValues[0]
                    bsiCellValueAddresses = bsiCellValue.findAll('span', class_='bsi_cell_value_address')

                    for bsiCellValueAddress in bsiCellValueAddresses:
                        businessAddress += bsiCellValueAddress.text
                
                if "Phone:" in bsiLabel.text :
                    bsiCellValues = businessDetailsRow.findAll('span', class_='bsi_cell_value')
                    bsiCellValue = bsiCellValues[0]
                    phone = bsiCellValue.text

                if "Email:" in bsiLabel.text :
                    bsiCellValues = businessDetailsRow.findAll('span', class_='bsi_cell_value')
                    bsiCellValue = bsiCellValues[0]
                    email = bsiCellValue.text

        feedbackContainers = soupShop.findAll('div', class_='fl each')
        itemAsDescribedCount = ''
        itemAsDescribedRating = ''
        communicationCount = ''
        communicationRating = ''
        dispatchTimeCount = ''
        dispatchTimeRating = ''
        postageCount = ''
        postageRating = ''
        memberSince = ''

        if feedbackContainers :
            
            for feedbackContainer in feedbackContainers:
                feedbackTypes = feedbackContainer.findAll('span', class_='dsr_type')
                feedbackType = feedbackTypes[0]

                if "Item as described" in feedbackType.text:
                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='gspr icfdy rating_ov')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    itemAsDescribedRating = feedbackTypeRating['title']

                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='dsr_count bold fl')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    itemAsDescribedCount = feedbackTypeRating.text

                if "Communication" in feedbackType.text:
                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='gspr icfdy rating_ov')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    communicationRating = feedbackTypeRating['title']

                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='dsr_count bold fl')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    communicationCount = feedbackTypeRating.text

                if "Dispatch time" in feedbackType.text:
                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='gspr icfdy rating_ov')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    dispatchTimeRating = feedbackTypeRating['title']

                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='dsr_count bold fl')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    dispatchTimeCount = feedbackTypeRating.text

                if "Postage" in feedbackType.text:
                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='gspr icfdy rating_ov')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    postageRating = feedbackTypeRating['title']

                    feedbackTypeRatings = feedbackContainer.findAll('span', class_='dsr_count bold fl')
                    feedbackTypeRating  = feedbackTypeRatings[0]
                    postageCount = feedbackTypeRating.text

                memberInfos = soupShop.findAll('div', class_='mem_info')
                memberInfo = memberInfos[0]
                sinces = memberInfo.findAll('span', class_='info')
                since = sinces[0]
                memberSince = since.text

        # get postcode 
        postcodeEnd = businessAddress.find(" United Kingdom")
        partialLoc = businessAddress[0:postcodeEnd]
        middleSpaceIndex = partialLoc.rfind(" ", 0, len(partialLoc))
        trimmedLocationHalFPostCode = businessAddress[0:middleSpaceIndex]
        postcodeStart = trimmedLocationHalFPostCode.rfind(" ", 0, len(trimmedLocationHalFPostCode))
        postcode = businessAddress[postcodeStart:postcodeEnd]
        address = businessAddress[0: postcodeStart]

        print businessName
        print businessAddress
        print phone
        print email
        print rating
        print itemAsDescribedCount
        print itemAsDescribedRating
        print communicationCount
        print communicationRating
        print dispatchTimeCount
        print dispatchTimeRating
        print postageCount
        print postageRating
        print memberSince
        print categoryLink
        print "page --- " + str(page)
        print ""
        
        wr.writerow([shopUrl, businessName, phone, email, rating, businessAddress, postcode, itemAsDescribedCount, itemAsDescribedRating, communicationCount, communicationRating, dispatchTimeCount, dispatchTimeRating, postageCount, postageRating, soldItem1, soldItem2, soldItem3, soldItem4, soldItem5, memberSince, ebayShopId])             


# main:
# get proxies from the csv file
# getProxies("US Proxy List.csv")
getProxies("cool-proxy.net - all http.csv")

with open('ebayResults.csv', 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(["Website URL", "Company Name", "Phone Number", "Email", "Overall Rating", "Address", "Postal Code",
                "Item As Described Count", "Item As Described Rating", "Communication Count", "Communication Rating", "Dispatch Time Count", "Dispatch Time Rating",
                "Postage Count", "Postage Rating", "Item 1 Price", "Item 2 Price", "Item 3 Price", "Item 4 Price",  "Item 5 Price", "Member Since", "Ebay ShopId", "Imported to Hubspot?"])

    hasPages = True
    currentPage = 1
    startPage = 24

    while hasPages:
        if currentPage >= startPage:
            categoryUrl = 'https://www.ebay.co.uk/b/Home-Decor-Items/10033/bn_1839832?LH_BIN=1&LH_PrefLoc=99&LH_SellerWithStore=1&rt=nc&_fspt=1&_pgn=' + str(currentPage) + '&_sadis=15&_sop=12&_stpos=WC1H0AA&_udlo=3'
            soup = changeProxy(categoryUrl)
            pageItems = soup.findAll('a', class_ = 's-item__link')

            # get the biggest next page number on this page 
            pagination = soup.findAll('li', class_ = 'ebayui-pagination__li ')
            lastLi = pagination[-1]
            lastLinks = lastLi.findAll('a')
            lastLink = lastLinks[0]
            biggestPageNumber = lastLink.text

            # get each product on the current page
            if pageItems:
                for pageItem in pageItems:
                    sellerUrl = pageItem['href']
                    itemSellerSoup = changeProxy(sellerUrl)
                    shopIds = itemSellerSoup.findAll('span', class_='mbg-nw')

                    if shopIds:
                        shopId = shopIds[0].text
                        if shopId not in visitedShops :
                            visitedShops.append(shopId)
                            getShopDetails(shopId, categoryUrl, currentPage)

            if currentPage >= int(biggestPageNumber) :
                hasPages = False

        currentPage +=1




