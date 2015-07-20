'''
Created on Jul 18, 2015


@author: gogqou


get SF rent prices from Zillow
import the zpids
then for each zpid get html info from webpage

'''
import numpy as np
import re
import requests
import bs4
import csv
class Listing(object):
    def __init__(self, ListingURL):
        self.URL = 'http://www.zillow.com'+ListingURL
        self.include = True
####################################################################
                                                                  ##
def getURLs(first_page_URL):
    Q1 = '13&rect=-122465930,37725821,-122377610,37786555'
    Q2 = '12&rect=-122556181,37755854,-122366667,37828293'
    Q3 = '13&rect=-122516056,37747846,-122422843,37808563'
    Q4 = '11&rect=-122490521,37780483,-122167798,38022942'
    fullLinks = getListingLinks(first_page_URL, Q1)
    fullLinks.update(getListingLinks(first_page_URL, Q2))
    fullLinks.update(getListingLinks(first_page_URL, Q3))
    fullLinks.update(getListingLinks(first_page_URL, Q4))
    return fullLinks

def write_dict_to_file(dictionary):
    with open('listingURLs.txt', 'w') as fp:
        for p in dictionary.keys():
            fp.write(p + '\n')
    '''
    with open ('wvtc_data.txt', 'w') as fp:
    for p in main_dic.items():
        fp.write("%s:%s\n" % p)
        '''
    return 1
def read_dict_from_file(filename):
    with open(filename,'r') as fp:
        fileList = [x.strip() for x in fp.readlines()] 
    return fileList
                                                                  
def makeListtoDict (List):
    listDict = {}
    for item in List:
        listDict[item] = Listing(item) #making it a listing object with URL
    return listDict

def writeDicttocsv(dictionary, filename):
    fp = open(filename, 'wb')
    a = csv.writer(fp)
    for v in dictionary.itervalues():
        if v.include is True:
            a.writerow([v.price, v.DescriptorLen, v.beds, v.baths, v.sqft])
    fp.close()
    return 1
                                                                  ##
####################################################################

####################################################################
                                                                  ##      
def getListingLinks(first_URL, addon):
    linksDict = {}
    r = requests.get(first_URL.format(addOn = addon, pagenumber = 1))
    result = r.json()
    totalpages = result['list']['numPages']
    print totalpages
    currentPage = 0
    while currentPage < totalpages and currentPage<20:
        pageResult, currentPage = parseWebPage(currentPage + 1, first_URL, addon)
        print currentPage
        pageSoup = bs4.BeautifulSoup(pageResult['list']['listHTML'], 'lxml')
        for link in bs4.BeautifulSoup(pageResult['list']['listHTML'], 'lxml', parse_only=bs4.SoupStrainer('a')):
            if link.has_attr('href') and 'myzillow' not in link['href']:
                #print link['href']
                linksDict[link['href']] = Listing(link['href'])
    print len(linksDict)
    return linksDict

def parseWebPage(pageNum, baseURL, addon):
    URL = baseURL.format(addOn = addon, pagenumber = pageNum)
    r = requests.get(URL)
    pageResult =  r.json()
    currentPage =  pageResult['list']['page']
    return pageResult, currentPage
                                                                  ##
####################################################################

####################################################################
                                                                  ##

def getListingAttribs(linksdict):
    for key, value in linksdict.iteritems():
        linksdict[key]=fetchListingPage(value)
    return linksdict
def fetchListingPage(Listing):
    listingPage = requests.get(Listing.URL, allow_redirects=False)
    #print Listing.URL
    Listing.fullpageData = bs4.BeautifulSoup(listingPage.text, 'lxml')
    Listing.Facts = Listing.fullpageData.find_all('ul', {"class": 'zsg-list_square zsg-lg-1-3 zsg-md-1-2 zsg-sm-1-1' })
    descriptor = Listing.fullpageData.find_all('div',{"class": 'notranslate' })
    if len(descriptor)>0:
        Listing.Descriptor = descriptor[0]
        Listing.DescriptorLen = len(Listing.Descriptor)
    else:
        Listing.include = False
        Listing.DescriptorLen = ''
        #print 'no descriptor'
    priceLabel = Listing.fullpageData.find_all('div',{"class":'main-row home-summary-row'})
    if len(priceLabel)>0:
        Listing.priceLabel = priceLabel[0].text   
        #print itemText.find('span', id = re.compile(r'\$[0-9,]+'))
        price_temp = re.split('/', Listing.priceLabel)[0]
        price = price_temp.replace(',', '')
        Listing.price = price.replace('$', '')
    else:
        Listing.priceLabel = ''
        Listing.price = ''
    BBS = Listing.fullpageData.find_all('span', class_ = 'addr_bbs')
    if len(BBS)>0:
        if 'Studio' in BBS[0].text:
            Listing.beds = 0
        else:
            Listing.beds = re.split('bed', BBS[0].text)[0]
        if '-' in BBS[1].text:
            Listing.baths = ''
        else:
            Listing.baths = re.split('bath', BBS[1].text)[0]
        if '-' in BBS[2].text:
            Listing.sqft = ''
        else:
            Listing.sqft = re.split('sqft', BBS[2].text)[0]
            Listing.sqft=Listing.sqft.replace(',', '')
        
    else:
        Listing.include = False
        Listing.baths = ''
        Listing.sqft = ''
        Listing.beds = ''
        #print 'no BBS descriptors'
    print Listing.price, Listing.beds, Listing.baths, Listing.sqft, Listing.DescriptorLen
    return Listing
                                                                  ##
####################################################################

####################################################################
                                                                  ##
                                                                  ##                                                                  
def rentAnalysis():
    ##~used below once to write a txt file with listing URLs~##
    ##~after first run, just read from file for quicker access~##
    #first_page_URL = 'http://www.zillow.com/search/GetResults.htm?spt=homes&status=000010&lt=000000&ht=011000&pr=,&mp=,&bd=0%2C&ba=0%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom={addOn}&p={pagenumber}&sort=days&search=maplist&disp=1&listright=true&isMapSearch=1&zoom=13' 
    #linksDict = getURLs(first_page_URL)
    #write_dict_to_file(linksDict)
    
    #read from URLs txt file to populate a dictionary of Listing objects
    listingList = read_dict_from_file ('listingURLs.txt')
    listingDict=makeListtoDict(listingList)
    populated_Listings = getListingAttribs(listingDict)
    writeDicttocsv(populated_Listings, 'Listing_stats.csv')
    return 1
if __name__ == '__main__':
    rentAnalysis()
####################################################################