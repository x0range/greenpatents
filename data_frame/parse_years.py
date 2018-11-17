import pickle
import pdb, sys
import pandas as pd
import numpy as np


def line_generator_from_file(filename):
    """Generator function. Opens filename and creates a generator that returns the relevant
       lines one by one (ignoring those starting with "#" 
        Arguments:
            filename - string - file name
        Returns generator"""
    with open(filename, "r") as rfile:
        _ = rfile.readline()
        for line in rfile:
            line = line.replace("\n", "")
            yield line

def correct_date_year(datestring):
    print("\nCorrecting: " + datestring + " to: ", end="")
    weird_typos = {"1298-06-25": "1982-06-25", "8198-04-05": "1982-04-05", "1096-01-18": "1986-01-18"}
    if datestring in weird_typos:
        datestring = weird_typos[datestring]
    if datestring[:2] == "91":
        datestring = "19" + datestring[2:]
    if datestring[0] == "1" and datestring[1] == "0" and int(datestring[2]) > 1:
        datestring = "19" + datestring[2:]
    if datestring[0] in ["0", "2", "3", "4", "5", "6", "7", "8", "9"] and datestring[1] == "9":
        datestring = "1" + datestring[1:]
    if datestring[0] == "1" and datestring[1] in ["0", "1", "2", "3", "4", "5", "6", "7"] and datestring[2] in ["7", "8", "9"]:
        datestring = "19" + datestring[2:]
    print(datestring)
    return datestring

class YearParser():
    def __init__(self):
        self.applicationdates = {}
        self.pddf = pd.DataFrame(columns=["applied date", "granted date", "applied year", "granted year"])   
        print("Parsing applications")
        self.parse_applications()
        print("All done.\nParsing patents")
        self.parse_patents()
        print("All done.")
    
    def parse_applications(self):
        i = 0 
        for line in line_generator_from_file("application.tsv"):
            elementi = line.split("\t")
            patID, date = elementi[1], elementi[5]
            if date[-2:] == "00":
                date = date[:-2] + "01"
            if date == "0000-00-01":
                """About 10 applications carry an invalid zero date. The publication search at the
                   USPTO http://appft.uspto.gov/netahtml/PTO/srchnum.html does not find these either. 
                   We could infer the correct date from the dates of the application numbers before
                   and after, but dates are not always in order, so it is better to drop these."""
                date = np.nan
            elif int(date[:4]) < 1800 or int(date[:4]) > 2020:
                date = correct_date_year(date)
            applydate = pd.to_datetime(date)
            self.applicationdates[patID] = applydate
            i += 1
            print("line {0:9d}".format(i), end="\r")

    def parse_patents(self):
        i = 0
        for line in line_generator_from_file("patent.tsv"):
            elementi = line.split("\t")
            patID, date = elementi[0], elementi[4]
            #print(patID, date)
            if date[-2:] == "00":
                date = date[:-2] + "01"
            #if date == "0000-00-01":
            #    date = np.nan
            #elif int(date[:4]) < 1800 or int(date[:4]) > 2020:
            if int(date[:4]) < 1800 or int(date[:4]) > 2020:
                try:
                    date = correct_date_year(date)
                except:
                    print(sys.exc_info())
                    pdb.set_trace()
            grantdate = pd.to_datetime(date)
            applydate = self.applicationdates[patID]
            applyyear = applydate.year
            grantyear = grantdate.year
            self.pddf.loc[patID] = [applydate, grantdate, applyyear, grantyear]
            i += 1
            print("line {0:9d}".format(i), end="\r")
    
    def save(self, filename="patents_dates_years.pkl"):
        print("Saving")
        self.pddf.to_pickle(filename)

if __name__ == "__main__":
    Y = YearParser()
    Y.save()
    
