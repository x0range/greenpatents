""" Script for parsing USPTO patent data, collecting abstracts and titles. All formats, txt, sgm, xml.
        Sources:
                on sgm: http://www.wipo.int/export/sites/www/standards/en/pdf/03-32-01.pdf
                on xml: 
                on txt: https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/1976/PatentFullTextAPSDoc_GreenBook.pdf
                        http://kwanghui.com/patents/tablestructure-sep2003.pdf
                on WKUs in xml: http://palblog.fxpal.com/?p=3980
                on data in general: http://journals.plos.org/plosone/article/file?type=supplementary&id=info:doi/10.1371/journal.pone.0176310.s002
                                    https://github.com/JusteRaimbault/PatentsMining/blob/master/Models/DataCollection/parser.py
                data sources:   https://bulkdata.uspto.gov/
                                https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/{1976:2018}/
                on research metadata files (not used here): https://www.uspto.gov/sites/default/files/documents/USPTO_Patents_Assignment_Dataset_WP.pdf
                source research metadata files (not used here): https://bulkdata.uspto.gov/data/patent/assignment/economics/2017/
                on webscraping (kinda shallow, not really used): https://blog.hartleybrody.com/web-scraping-cheat-sheet/
        Also helpful (though this code does no longer work):
                https://github.com/WernerDJ/Patents-and-Lexical-diversity
                
    """

from zipfile import ZipFile
from bs4 import BeautifulSoup
import requests
import urllib
import os
import sys
import pickle
import datetime
import re
import pdb
import glob
from random import randint
from time import sleep

def wku_confirm_checksum(wku):
    pn = wku[:-1]
    apn = 0
    for i, pd in enumerate(list(reversed(pn))):
        apn += (i+2)*int(pd)
        #print(apn, i, pd)
    check = (11 - apn % 11) % 10 # This is an ISBN type mod 11 checksum
    try:
        assert check == int(wku[-1]), "WKU check digit does not match: WKU: {0:s} WKU Check digit: {1:1d} Computed check digit {2:1d}".format(wku, int(wku[-1]), check)
    except:
        #pdb.set_trace()
        print("WKU check digit does not match: WKU: {0:s} WKU Check digit: {1:1d} Computed check digit {2:1d}".format(wku, int(wku[-1]), check))
        #print("WKU check digit does not match: WKU: {0:s} WKU Check digit: {1:} Computed check digit {2:1d}".format(wku, wku[-1], check))
        pass
    
def parse_wku(wku_raw):
    # WKUs are listed as 9-character codes, e.g. "040001075", "040001610", "RE0290882", "D02428423", "PP0039993"
    #     <optional type code (RE, D, PP)> - 0 - <patent number (5, 6, or 7 digits)> - check digit
    # the patent number is either 7 digits (normal patents), or
    #                             {PP, RE} + 5 digits, or
    #                             D + 6 digits
    wku_raw = wku_raw.strip()                   # remove leading and trailing spaces
    if wku_raw[-1] == "&":                       # some early records falsely have checksum & instead of 0
        wku_raw = wku_raw[:-1] + "0"            #
    wku_sep = re.findall('\d+|\D+', wku_raw)    # separate letters and digits
    #wku_checksum = wku_raw[-1]                 # last digit is checksum
    wku_confirm_checksum(wku_sep[-1])
    try:
        assert wku_sep[-1][0] == "0", "Strange WKU encountered: {0:s}".format(wku_raw)
    except:
        print("Strange WKU encountered: {0:s}".format(wku_raw))
        pass
    if len(wku_sep) == 1:
        wku = wku_sep[0][1:-1]
    else:
        wku = wku_sep[0] + wku_sep[1][1:-1]
    return wku
    
def parse_patent_record_txt(filename):
    returndict = {}
    titledict = {}
    #rfile = open(filename, "r")
    rfile = open(filename, "r", encoding="utf8", errors='ignore')
    wku = None
    previouswku = None
    title = None
    abstract = None
    abstractopen = False
    palopen = False
    for line in rfile:
        if not abstractopen:
            if line[:4] == "WKU ":
                if wku is not None:
                    returndict[wku] = abstract
                    previouswku = wku
                wku_raw = line[4:]
                wku = parse_wku(wku_raw)
            elif line[:4] == "TTL ":
                if title is not None and previouswku[0] != "D": #design patents usually do not have an abstract
                    print("Something wrong: Found two titles for the same record", file=sys.stderr)
                title = line[4:].strip()
            elif line[:4] == "ABST":
                #pdb.set_trace()
                abstractopen = True                
        else:
            if line[:4] in ["PAL ", "PA1 ", "PA0 ", "PA2 ", "PA3 ", "PA4 ", "PA5 ", "PA6 ", "PA7 ", "PA8 ", "PA9 ", "TBL ", "EQU ", "PAR "]:
                line = line[4:]
                line = line.strip()
                if not palopen and abstract is None:
                    abstract = ""
                    palopen = True
                elif not palopen:
                    print("Something wrong here, this may be a second abstract in the same patent or so???", file=sys.stderr)
                abstract += line + " "
            elif line[0] not in [" ", "\n"]:
                nextsection = line.strip()
                try:
                    assert nextsection in ["BSUM", "PARN", "GOVT"], "Unexpected end of abstract section encountered: {0:s}".format(nextsection)
                except:
                    print("Unexpected end of abstract section encountered: {0:s}".format(nextsection))
                    pass
                try:
                    assert wku is not None, "None type WKU detected, disregarding abstract"
                    returndict[wku] = abstract
                except:
                    print("None type WKU detected, disregarding abstract")
                    pass
                try:
                    assert (wku is not None) and (title is not None), "None type WKU or title detected, disregarding abstract"
                    titledict[wku] = title
                except:
                    print("None type WKU detected, disregarding abstract")
                    pass
                wku = None
                abstract = None
                title = None
                abstractopen = False
                palopen = False
            else:
                try:
                    assert palopen, "Unexpected abstract line encountered: {0:s}".format(line)
                except:
                    print("Unexpected abstract line encountered: {0:s}".format(line))
                    if len(line.strip()) > 15:
                        palopen = True
                        abstract = ""
                if palopen:
                    line = line.strip()
                    try:
                        abstract += line + " "
                    except:
                        pdb.set_trace()
    rfile.close()
    return returndict, titledict

def xml_get_abstract(soup):
    try:
        abstract = soup.find("us-patent-grant").find("abstract").text
    except:
        abstract = None
    return abstract

def xml_get_wku(soup):
    try:
        wku = soup.find("us-patent-grant").find("document-id").find("doc-number").text
    except:
        wku = None
    return wku

def xml_get_title(soup):
    try:
        title = soup.find("us-patent-grant").find("invention-title").text
    except:
        title = None
    return title

def parse_single_xml_patent(xml_block):
    soup = BeautifulSoup(xml_block, "xml")
    wku = xml_get_wku(soup)
    title = xml_get_title(soup)
    if wku is not None:
        abstract = xml_get_abstract(soup)
    else:
        abstract = None
    return wku, title, abstract

def parse_patent_record_xml(filename):
    returndict = {}
    titledict = {}
    rfile = open(filename, "r", encoding="utf8", errors='ignore')
    xmlopen = False
    xmlblock = ""
    for line in rfile:
        if line[:6] == "<?xml ":
            if xmlopen:             # new xml block
                wku, title, abstract = parse_single_xml_patent(xmlblock)
                if wku is not None:
                    returndict[wku] = abstract
                    if title is not None:
                        titledict[wku] = title
                xmlblock = ""
                xmlopen = False
            xmlopen = True
            xmlblock += line
        else:
            xmlblock += line
        #pfile =  open("ipg050419.xml",'r')
    wku, title, abstract = parse_single_xml_patent(xmlblock)
    if wku is not None:
        returndict[wku] = abstract
        if title is not None:
            titledict[wku] = title
    rfile.close()
    return returndict, titledict

def sgm_get_abstract_manual(xml_block):
    sgmblockc = xml_block.split("\n")
    sdoabopen = False
    sdoabblock = ""
    for line in sgmblockc:
        if sdoabopen:
            if "</SDOAB>" in line:
                sdoabopen = False
                line = line.split("</SDOAB>")[0] + "</SDOAB>"
            sdoabblock += line
        elif "<SDOAB>" in line:
            sdoabopen = True
            line = line.split("<SDOAB>")[0] + "<SDOAB>"
            sdoabblock += line
    soup2 = BeautifulSoup(sdoabblock, "xml")
    abstract = soup2.find("SDOAB").text
    return abstract

def sgm_get_abstract(soup, xml_block):
    try:
        abstract = soup.find("SDOAB").text
        if len(abstract) > 2000:
            abstract = sgm_get_abstract_manual(xml_block)
    except:
        abstract = None
    return abstract

def sgm_get_wku(soup):
    try:
        wku = soup.find("B110").find("DNUM").text
    except:
        wku = None
    return wku

def sgm_get_title(soup):
    try:
        title = soup.find("B540").text
    except:
        title = None
    return title

def parse_single_sgm_patent(sgm_xml_block):
    soup = BeautifulSoup(sgm_xml_block, "xml")
    wku = sgm_get_wku(soup)
    title = sgm_get_title(soup)
    #if "1262" in wku:
    #    abstract = sgm_get_abstract(soup, xml_block, True)
    #    pdb.set_trace()
    if wku is not None:
        abstract = sgm_get_abstract(soup, sgm_xml_block)
    else:
        abstract = None
    return wku, title, abstract

def parse_patent_record_sgm(filename):
    returndict = {}
    titledict = {}
    rfile = open(filename, "r", encoding="utf8", errors='ignore')
    xmlopen = False
    xmlblock = ""
    for line in rfile:
        if line[:8] == "<PATDOC ":
            if xmlopen:             # new sgm quasi-xml block
                wku, title, abstract = parse_single_sgm_patent(xmlblock)
                if wku is not None:
                    returndict[wku] = abstract
                    if title is not None:
                        titledict[wku] = title
                xmlblock = ""
                xmlopen = False
            xmlopen = True
            xmlblock += line
        else:
            xmlblock += line
    wku, title, abstract = parse_single_sgm_patent(xmlblock)
    if wku is not None:
        returndict[wku] = abstract
        if title is not None:
            titledict[wku] = title
    rfile.close()
    return returndict, titledict

def test_parse_filetype(filename, fileform):
    markers = {"txt": "WKU ", "sgm": "<PATDOC ", "xml": "<us-patent-grant "}
    return markers[fileform] in open(filename, encoding="utf8", errors='ignore').read()
    
    
def parse_patent_record_xmlsgm(filename, types):
    parsefunctions = {"txt": parse_patent_record_txt, "sgm": parse_patent_record_sgm, "xml": parse_patent_record_xml}
    for fileform in types:
        #print(fileform, test_parse_filetype(filename, fileform))
        #pdb.set_trace()
        if test_parse_filetype(filename, fileform):
            parsefunction = parsefunctions[fileform]
            #print(fileform, parsefunction)
            return parsefunction(filename)
    assert False, "File type not recognized for file {0:s}. It is none of: {1:s}".format(filename, str(types))

def parse_file(filename):
    if filename[-4:] == ".txt":
        return parse_patent_record_txt(filename)
    elif filename[-4:] in [".xml", ".XML"]:
        return parse_patent_record_xmlsgm(filename, ["xml", "sgm"])
    elif filename[-4:] in [".sgm", ".SGM"] or filename[-5:] == ".SGML":
        return parse_patent_record_xmlsgm(filename, ["sgm", "xml"])
    else:
        assert False, "File could not be identified: {0:s}".format(filename)
        
    
def get_urls_year(year):
    urls = []
    names = []
    url = "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/" + year + "/"
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    for link in soup.find_all('a'):
        fname = link.get('href')
        full_url = url + fname
        if full_url.endswith('.zip'):
            urls.append(full_url)
            names.append(fname)
    return urls, names

def pickle_abstract_n_title(cname, abstract_dict, title_dict):
        pickle_filename_abstract = "abstracts_" + cname[:-4] + ".pkl"
        pickle_filename_title = "titles_" + cname[:-4] + ".pkl"
        for to_be_pickled, pickle_filename in [(abstract_dict, pickle_filename_abstract), (title_dict, pickle_filename_title)]:
            if os.path.isfile(pickle_filename):
                datestring = datetime.date.strftime(datetime.datetime.now(),"-%d-%m-%Y-at-%H-%M-%S")
                newname = pickle_filename.split(".")[0] + datestring + pickle_filename.split(".")[0]
                os.rename(pickle_filename, newname)
            with open(pickle_filename, 'wb') as outputfile:
                pickle.dump(to_be_pickled, outputfile, pickle.HIGHEST_PROTOCOL)
    
def download_n_parse_year(year, start=None):
    urls, names = get_urls_year(year) 
    ## 3 
    #urls = urls[2:3]
    #names = names[2:3]
    #print(urls, names)  
    if start is not None:
        nameidx = names.index(start)        #correct?
        names = names[nameidx:]
        urls = urls[nameidx:]
    #print(year, urls[0])         
    #raise SystemExit
    for i, url in enumerate(urls):
        ## 2  PASSED
        print("    Fetching and parsing item {0:2d}: {1:s}".format(i, url))
        #if False:
        sleep(randint(4, 32))     # random wait
        urllib.request.urlretrieve(url, names[i])
        with ZipFile(names[i], 'r') as zip:
            files_extracted = zip.namelist()
            try:
                assert len(files_extracted)==1, "Zip {0:s} contains more than one file: ".format(names[i])
            except:
                print("Zip {0:s} contains more than one file: ".format(names[i]))
                print(files_extracted)
            zip.extract(files_extracted[0])
        ## 2 PASSED
        #files_extracted = ["pftaps19760120_wk03.txt"]
        #names = ["pftaps19760120_wk03.zip"]
        #i = 0
        #if True:
        # parse 
        abstract_dict, title_dict = parse_file(files_extracted[0])
        # rm extracted file
        os.remove(files_extracted[0])
        os.system("mv {0:s} /mnt/usb4/datalake_patents_eco/ > /dev/null 2>&1".format(names[i]))
        # save pickle
        name = names[i]
        pickle_abstract_n_title(name, abstract_dict, title_dict)
        
def reread_files(names):
    for i in range(len(names)):
        print("    Rereading and parsing item {0:2d}: {1:s}".format(i, names[i]))
        os.system("cp /mnt/usb4/datalake_patents_eco/{0:s} ./ > /dev/null 2>&1".format(names[i]))
        with ZipFile(names[i], 'r') as zip:
            files_extracted = zip.namelist()
            try:
                assert len(files_extracted)==1, "Zip {0:s} contains more than one file: ".format(names[i])
            except:
                print("Zip {0:s} contains more than one file: ".format(names[i]))
                print(files_extracted)
            zip.extract(files_extracted[0])
        #os.remove(names[i])
        abstract_dict, title_dict = parse_file(files_extracted[0])
        os.remove(files_extracted[0])
        #save as pickle
        name = names[i]
        pickle_abstract_n_title(name, abstract_dict, title_dict)
        

# main entry point
if __name__ == "__main__":
    
    """Define range of years and file to start with. range(1976, 2019) and start=None is all files all years"""
    years = list(range(1976, 2019))
    start = None
    #years = list(range(1990, 2019))
    #start = "pftaps19900612_wk24.zip"
    #years = list(range(2016, 2019))
    #start = "ipg160830.zip"
    
    """Already downloaded files can be reread by calling reread_files()"""
    #files = ["pftaps19761228_wk52.zip", "pg010102.zip", "pg010109.zip", "pg010911.zip", "pg020108.zip", "pg020212.zip", "pg020402.zip", "ipg160112.zip", "pftaps20010102_wk01.zip"]
    files = glob.glob("*.zip")
    files = []
    reread_files(files)
    #exit(0)
    
    """Download, parse, and save"""
    for year in years:
        print("Commencing year {0:d}".format(year))
        download_n_parse_year(str(year), start=start)
        start = None
    
    """To just test the parse_file() function with a single file"""
    #files_extracted = ["pg020521.XML"]
    #abstract_dict, titles_dict = parse_file(files_extracted[0])
    #pdb.set_trace()
