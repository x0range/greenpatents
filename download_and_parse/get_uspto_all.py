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
import numpy as np
import gzip
from random import randint
from time import sleep

def wku_confirm_checksum(wku):
    pn = wku[:-1]
    apn = 0
    for i, pd in enumerate(list(reversed(pn))):
        apn += (i+2)*int(pd)
        #print(apn, i, pd)
    check = (11 - apn % 11) % 10 # This is an ISBN type mod 11 checksum
    #print(wku)
    try:
        assert check == int(wku[-1]), "WKU check digit does not match: WKU: {0:s} WKU Check digit: {1:1d} Computed check digit {2:1d}".format(wku, int(wku[-1]), check)
    except:
        #pdb.set_trace()
        #print("WKU check digit does not match: WKU: {0:s} WKU Check digit: {1:1d} Computed check digit {2:1d}".format(wku, int(wku[-1]), check))
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
    #print("Returning WKU: {0:s}".format(wku))
    return wku
    
def parse_patent_record_txt(filename):
    returndict = {}
    titledict = {}
    descriptiondict = {}
    claimsdict = {}
    #rfile = open(filename, "r")
    rfile = open(filename, "r", encoding="utf8", errors='ignore')
    wku = None
    previouswku = None
    title = None
    abstract = None
    description = ""
    claims = ""
    abstractopen = False
    abstractclosed = False
    descriptionopen = False
    descriptionclosed = False
    descriptionlineclosedwith = None
    claimsopen = False
    claimsclosed = False
    abstractpalopen = False
    long_abstract_error_thrown = False
    for line in rfile:
        #print(line)
        #print("!!!claimsclosed", claimsclosed, " claimsopen", claimsopen)
        #pdb.set_trace()
        if line[:4] in ["PATN", "WKU "]:
            """ Saving previous patent"""
            if wku is not None:                            
                #pdb.set_trace()
                returndict[wku] = abstract
                titledict[wku] = title
                descriptiondict[wku] = description
                claimsdict[wku] = claims
                previouswku = wku
                wku = None
                if line[:4] == "WKU ":
                    print("Something wrong: We must have missed the PATN statement. Continuing... ", file=sys.stderr)
            elif (title is not None) or (abstract is not None) or len(description) > 0 or len(claims) > 0:
                print("Patent dara without corresponding WKU detected, disregarding data", file=sys.stderr)

            """ Resetting data collection variables"""
            abstract = None
            title = None
            description = ""
            claims = ""
            abstractclosed = False
            descriptionclosed = False
            descriptionlineclosedwith = None
            claimsclosed = False
            abstractopen = False
            descriptionopen = False
            claimsopen = False
            long_abstract_error_thrown = False
            abstractpalopen = False
            
            """ Parsing WKU"""
            if line[:4] == "WKU ":
                wku_raw = line[4:]
                wku = parse_wku(wku_raw)
        elif (not abstractopen) and (not claimsopen) and (not descriptionopen):
            if line[:4] == "TTL ":
                if title is not None and previouswku[0] != "D": #design patents usually do not have an abstract
                    print("Something wrong: Found two titles for the same record", file=sys.stderr)
                title = line[4:].strip()
            elif line[:4] == "ABST":
                #pdb.set_trace()
                abstractopen = True  
            elif line[:4] == "CLMS":
                claimsopen = True
            elif line[:4] in ["BSUM", "DRWD", "DETD"]:
                descriptionopen = True                    
        elif (abstractopen) and (not claimsopen) and (not descriptionopen):
            try:
                assert not abstractclosed
            except:
                print("Something wrong here. Found a second abstract in the same patent. Replacing the first. This will probably result in problems.", file=sys.stderr)
                abstract = ""
                abstractclosed = False
            if line[:4] in ["PAL ", "PA1 ", "PA0 ", "PA2 ", "PA3 ", "PA4 ", "PA5 ", "PA6 ", "PA7 ", "PA8 ", "PA9 ", "TBL ", "EQU ", "PAR "]:
                line = line[4:]
                line = line.strip()
                if not abstractpalopen and abstract is None:
                    abstract = ""
                    abstractpalopen = True
                elif not abstractpalopen:
                    print("Something wrong here, this may be a second abstract in the same patent or so???", file=sys.stderr)
                abstract += line + " "
            elif line[0] not in [" ", "\n"]:            # New section should close the abstract
                nextsection = line.strip()
                try:
                    assert nextsection in ["BSUM", "PARN", "GOVT"], "Unexpected end of abstract section encountered: {0:s}".format(nextsection)
                except:
                    print("Unexpected end of abstract section encountered: {0:s}".format(nextsection))
                    #pdb.set_trace()
                abstractopen = False
                apstractclosed = True
                abstractpalopen = False
                if line[:4] == "CLMS":
                    claimsopen = True
                elif line[:4] in ["BSUM", "DRWD", "DETD"]:
                    descriptionopen = True                    
                if long_abstract_error_thrown:
                    print("Something wrong here, abstract {1:s} seeme excessively long: \n\n {0:s}\n\n\n\n".format(abstract, str(wku)), file=sys.stderr)
                    #print(wku)
                    #print(abstract)
            else:
                try:
                    assert abstractpalopen, "Unexpected abstract line encountered: {0:s}".format(line)
                except:
                    print("Unexpected abstract line encountered: {0:s}".format(line))
                    #pdb.set_trace()
                    if len(line.strip()) > 15:
                        abstractpalopen = True
                        abstract = ""
                if abstractpalopen:
                    line = line.strip()
                    try:
                        abstract += line + " "
                    except:
                        pdb.set_trace()
            if (abstract is not None) and (len(abstract)>3000) and (not long_abstract_error_thrown):
                long_abstract_error_thrown = True
                print("Something wrong here, abstract seeme excessively long: \n\n {0:s}\n\n\n\n".format(abstract), file=sys.stderr)
        elif (not abstractopen) and (not claimsopen) and (descriptionopen):
            #pdb.set_trace()
            try:
                assert not descriptionclosed
            except:
                print("Something wrong here. Found a second description in the same patent. First description was closed with ",
                      "\n{0:s}\nCurrently, description is \n{1:s}\n This will probably result in problems.".format(descriptionlineclosedwith, description), file=sys.stderr)
                #pdb.set_trace()
                #description = ""
                descriptionclosed = False
            if (line[:4] in ["PAL ", "PAC ", "PA1 ", "PA0 ", "PA2 ", "PA3 ", "PA4 ", "PA5 ", "PA6 ", "PA7 ", "PA8 ", "PA9 ", "TBL ", "EQU ", "PAR ", "FIG.", "FNT ", \
					"PAL\n", "PAC\n", "PA1\n", "PA0\n", "PA2\n", "PA3\n", "PA4\n", "PA5\n", "PA6\n", "PA7\n", "PA8\n", "PA9\n", "TBL\n", "EQU\n", "PAR\n", "FNT\n", "TBL3"]):# or (line[:3] in ["TBL"]):
                line = line[4:]
                line = line.strip()
                description += line + " "
            elif line[:4] in ["BSUM", "DRWD", "DETD"]:
                description += "\n\n"
            elif line[0] not in [" ", "\n"]:
                #print("Closing description with line: {0:s}".format(line))
                nextsection = line.strip()
                descriptionopen = False
                descriptionclosed = True
                descriptionlineclosedwith = line
                if line[:4] == "CLMS":
                    claimsopen = True
                elif line[:4] == "ABST":
                    abstractopen = True
            else:
                line = line.strip()
                description += line + " "
        elif (not abstractopen) and (claimsopen) and (not descriptionopen):
            #pdb.set_trace()
            try:
                assert not claimsclosed
            except:
                print("Something wrong here. Found a second set of claims in the same patent. This will probably result in problems.", file=sys.stderr)
                pdb.set_trace()
                claimsclosed = False
            if line[:4] in ["PAL ", "PAC ", "PA1 ", "PA0 ", "PA2 ", "PA3 ", "PA4 ", "PA5 ", "PA6 ", "PA7 ", "PA8 ", "PA9 ", "TBL ", "EQU ", "PAR "]:
                line = line[4:]
                line = line.strip()
                claims += line + " "
            elif line[:4] in ["NUM ", "STM "]:
                claims += "\n\n"
            elif line[0] not in [" ", "\n"]:
                #print("Closing claims with line: {0:s}".format(line))
                nextsection = line.strip()
                claimsopen = False
                claimsclosed = True
                if line[:4] in ["BSUM", "DRWD", "DETD"]:
                    descriptionopen = True
                elif line[:4] == "ABST":
                    abstractopen = True
            else:
                line = line.strip()
                claims += line + " "           
    
    rfile.close()
    
    # Saving last patent
    returndict[wku] = abstract
    titledict[wku] = title
    descriptiondict[wku] = description
    claimsdict[wku] = claims
    #pdb.set_trace()
    return returndict, titledict, descriptiondict, claimsdict

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

def xml_get_description(soup):
    try:
        d = soup.find("us-patent-grant").find("description")
        # TODO: remove UTF8 codes (&#x2019; etc)                    # automatically
        # TODO: remove MATHS->math, table-> table, figref??         # Done
        #d = ???
        _ = [tag.extract() for tag in d(['table', 'maths'])]        # Cannot deal with '?in-line-formulae'
        d = d.text
    except:
        d = None
    return d

def xml_get_claims(soup):
    try:
        cl = soup.find("us-patent-grant").find("claims").text
    except:
        cl = None
    return cl

def parse_single_xml_patent(xml_block):
    soup = BeautifulSoup(xml_block, "xml")
    wku = xml_get_wku(soup)
    if wku is not None:
        abstract = xml_get_abstract(soup)
        title = xml_get_title(soup)
        description = xml_get_description(soup)
        claims = xml_get_claims(soup)
        #if np.random.random() < 0.002:
        #    pdb.set_trace()
    else:
        abstract = None
        title = None
        description = None
        claims = None
    return wku, title, abstract, description, claims

def parse_patent_record_xml(filename):
    returndict = {}
    titledict = {}
    descriptiondict = {}
    claimsdict = {}
    rfile = open(filename, "r", encoding="utf8", errors='ignore')
    xmlopen = False
    xmlblock = ""
    for line in rfile:
        if line[:6] == "<?xml ":
            if xmlopen:             # new xml block
                wku, title, abstract, description, claims = parse_single_xml_patent(xmlblock)
                if wku is not None:
                    returndict[wku] = abstract
                    titledict[wku] = title
                    descriptiondict[wku] = description
                    claimsdict[wku] = claims
                xmlblock = ""
                xmlopen = False
            xmlopen = True
            xmlblock += line
        else:
            xmlblock += line
        #pfile =  open("ipg050419.xml",'r')
    wku, title, abstract, description, claims = parse_single_xml_patent(xmlblock)
    if wku is not None:
        returndict[wku] = abstract
        titledict[wku] = title
        descriptiondict[wku] = description
        claimsdict[wku] = claims
    rfile.close()
    return returndict, titledict, descriptiondict, claimsdict

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

def sgm_get_description(soup):                    
    try:
        # If this fails because of recursion depth try sys.setrecursionlimit(10000) # default is 1000
        d = soup.find("SDODE")
        _ = [tag.extract() for tag in d(['SDOCL', 'THEAD', 'TBODY', 'math', 'EMI'])]
        d = d.text
    except:
        d = None
    return d

def sgm_get_claims(soup):
    try:
        cl = soup.find("CL").text
    except:
        cl = None
    return cl

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
    #if "1262" in wku:
    #    abstract = sgm_get_abstract(soup, xml_block, True)
    #    pdb.set_trace()
    if wku is not None:
        abstract = sgm_get_abstract(soup, sgm_xml_block)
        title = sgm_get_title(soup)
        claims = sgm_get_claims(soup)
        description = sgm_get_description(soup)
        #if np.random.random() < 0.0003:
        #    pdb.set_trace()
    else:
        abstract = None
        title = None
        description = None
        claims = None
    return wku, title, abstract, description, claims

def parse_patent_record_sgm(filename):
    returndict = {}
    titledict = {}
    descriptiondict = {}
    claimsdict = {}
    rfile = open(filename, "r", encoding="utf8", errors='ignore')
    xmlopen = False
    xmlblock = ""
    for line in rfile:
        if line[:8] == "<PATDOC ":
            if xmlopen:             # new sgm quasi-xml block
                wku, title, abstract, description, claims = parse_single_sgm_patent(xmlblock)
                if wku is not None:
                    returndict[wku] = abstract
                    titledict[wku] = title
                    descriptiondict[wku] = description
                    claimsdict[wku] = claims
                xmlblock = ""
                xmlopen = False
            xmlopen = True
            xmlblock += line
        else:
            xmlblock += line
    wku, title, abstract, description, claims = parse_single_sgm_patent(xmlblock)
    if wku is not None:
        returndict[wku] = abstract
        titledict[wku] = title
        descriptiondict[wku] = description
        claimsdict[wku] = claims
    rfile.close()
    return returndict, titledict, descriptiondict, claimsdict

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

def pickle_abstract_n_title(cname, abstract_dict, title_dict, descr_dict, claims_dict):                # TODO: Add saving text and claims dict
    """parse file names"""
    dir_end = cname.rfind("/") + 1
    gzpickle_filename_abstract = cname[:dir_end] + "abstracts/abstracts_" + cname[dir_end:-4] + ".pkl.gz"
    gzpickle_filename_title = cname[:dir_end] + "titles/titles_" + cname[dir_end:-4] + ".pkl.gz"
    gzpickle_filename_description = cname[:dir_end] + "descriptions/descriptions_" + cname[dir_end:-4] + ".pkl.gz"
    gzpickle_filename_claims = cname[:dir_end] + "claims/claims_" + cname[dir_end:-4] + ".pkl.gz"
    for to_be_pickled, gzpickle_filename in [(abstract_dict, gzpickle_filename_abstract), \
                                           (title_dict, gzpickle_filename_title), \
                                           (descr_dict, gzpickle_filename_description), \
                                           (claims_dict, gzpickle_filename_claims)]:
        if os.path.isfile(gzpickle_filename):
            datestring = datetime.date.strftime(datetime.datetime.now(),"-%d-%m-%Y-at-%H-%M-%S")
            newname = gzpickle_filename.split(".")[0] + datestring + "." + gzpickle_filename.split(".")[1] + "." + gzpickle_filename.split(".")[2]
            os.rename(gzpickle_filename, newname)
        #with open(pickle_filename, 'wb') as outputfile:
        #    pickle.dump(to_be_pickled, outputfile, pickle.HIGHEST_PROTOCOL)
        with gzip.GzipFile(gzpickle_filename, 'w') as outputfile:
            pickle.dump(to_be_pickled, outputfile, pickle.HIGHEST_PROTOCOL)
        #
        # To reload, do:
        #with gzip.GzipFile(gzpickle_filename, 'r') as gzf:
        #    reloaded = pickle.load(gzf)


def download_n_parse_year(year, start=None, raw_file_directory="/mnt/usb4/datalake_patents_eco"):
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
        abstract_dict, title_dict, description_dict, claims_dict = parse_file(files_extracted[0])
        pdb.set_trace()
        # rm extracted file
        os.remove(files_extracted[0])
        os.system("mv {0:s} {1:s}/ > /dev/null 2>&1".format(names[i], raw_file_directory))
        # save pickle
        name = names[i]
        pickle_abstract_n_title(name, abstract_dict, title_dict, description_dict, claims_dict)
        
def reread_files(names, raw_file_directory="/mnt/usb4/datalake_patents_eco", work_directory="/mnt/usb2/GreenPatentsProject/raw_data/work/"):
    os.chdir(work_directory)
    for i in range(len(names)):
        print("    Rereading and parsing item {0:2d}: {1:s}".format(i, names[i]))
        os.system("cp {1:s}/{0:s} ./ > /dev/null 2>&1".format(names[i], raw_file_directory))
        with ZipFile(names[i], 'r') as zip:
            files_extracted = zip.namelist()
            try:
                assert len(files_extracted)==1, "Zip {0:s} contains more than one file: ".format(names[i])
            except:
                print("Zip {0:s} contains more than one file: ".format(names[i]))
                print(files_extracted)
            zip.extract(files_extracted[0])
        #os.remove(names[i])
        abstract_dict, title_dict, description_dict, claims_dict = parse_file(files_extracted[0])
        os.remove(files_extracted[0])
        #save as pickle
        name = names[i]
        pickle_abstract_n_title(name, abstract_dict, title_dict, description_dict, claims_dict)
        

# main entry point
if __name__ == "__main__":
    
    """Define range of years and file to start with. range(1976, 2019) and start=None is all files all years"""
    years = list(range(1976, 2019))
    start = None
    #years = list(range(1990, 2019))
    #start = "pftaps19900612_wk24.zip"
    #years = list(range(2016, 2019))
    #start = "ipg160830.zip"
    years = []        # downloading off
    
    """Already downloaded files can be reread by calling reread_files()"""
    #files = ["pftaps19761228_wk52.zip", "pg010102.zip", "pg010109.zip", "pg010911.zip", "pg020108.zip", "pg020212.zip", "pg020402.zip", "ipg160112.zip", "pftaps20010102_wk01.zip"]
    raw_file_directory = "/mnt/usb2/GreenPatentsProject/raw_data/PatentsRaw"
    #raw_file_directory = "/mnt/usb2/GreenPatentsProject/raw_data/PatentsRaw2/testunpack"
    files = glob.glob("{0:s}/*.zip".format(raw_file_directory))#[2:]
    files = glob.glob("{0:s}/p*.zip".format(raw_file_directory))#[2:]
    print(files)
    #pdb.set_trace()
    #files = []
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
