import pickle
import pdb, sys
import pandas as pd
import numpy as np
import multiprocessing as mp
import os
import zipfile
import itertools

def line_generator_from_zipfile(filename, zipfilename, start=0, stop=None):
    """Generator function. Opens filename and creates a generator that returns the relevant
       lines one by one (ignoring those starting with "#" 
        Arguments:
            zipfilename - string - zip file name
            filename - string - path inside zipfile
        Returns generator"""
    with zipfile.ZipFile(zipfilename) as zfile:
        with zfile.open(filename, "r") as rfile:
            for line in itertools.islice(rfile, start, stop):
                line = line.decode("UTF-8")
                line = line.replace("\n", "")
                yield line

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
    def __init__(self, input_tupel, app_save_filename = "parse_year_applicationdates.pkl"):
        start, stop = input_tupel
        self.applicationdates = {}
        self.pddf = pd.DataFrame(columns=["applied date", "granted date", "applied year", "granted year"])   
        if os.path.exists("parse_year_applicationdates.pkl"):
            print("Applicationdates file found. Loading...")
            with open(app_save_filename, "rb") as rfile:
                self.applicationdates = pickle.load(rfile)
        else:
            print("No applicationdates file found. Parsing applications...")
            self.parse_applications()
            print("Done. Saving...")
            with open(app_save_filename, "wb") as wfile:
                pickle.dump(self.applicationdates, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        print("Done.\nParsing patents")
        if start is not None:
            self.parse_patents(start, stop)
        print("All done.")
    
    def get_pddf(self):
        return self.pddf
    
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

    def parse_patents(self, start, stop):
        i = 0
        print("Starting chunk {0:7d}-{1:7d}".format(start, stop))
        for line in line_generator_from_zipfile("data/20180528/bulk-downloads/patent.tsv", zipfilename="patent.tsv.zip", start=start, stop=stop):
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
            #print("line {0:9d}".format(i), end="\r")

    def save(self, filename="patents_dates_years.pkl"):
        print("Saving")
        self.pddf.to_pickle(filename)
    
class WriterThread():
    def __init__(self, filename="patents_dates_years.pkl"):
        self.pddf = pd.DataFrame(columns=["applied date", "granted date", "applied year", "granted year"])   
        self.filename = filename
        
    def run(self, queue):
        while True:
            try:
                queueitem = queue.get(block = False)
                if isinstance(queueitem, pd.DataFrame):
                    #print("Loading")
                    #pddf = load_pickle(self.filename)                    
                    print("Appending {} rows".format(len(queueitem)))
                    self.pddf = self.pddf.append(queueitem)
                    print("...now total {} rows".format(len(self.pddf)))
                    print("Saving")
                    self.pddf.to_pickle(self.filename)
                elif queueitem[0] == "TERMINATE":
                    break
            except:
                pass

class MultiProcesser():
    def __init__(self, thread_number=14):
        
        """Prepare queues"""
        startstoplist = zip(list(np.arange(1, 6647700, 100000)), list(np.arange(1, 6647700, 100000))[1:] + [6647700])
        startstoplist = zip(list(np.arange(1, 6647, 1000)), list(np.arange(1, 6647, 1000))[1:] + [6647])
        self.mpM = mp.Manager()
        self.input_queue = self.mpM.Queue()
        self.output_queue = self.mpM.Queue()
        for startstop in startstoplist: 
            self.input_queue.put(startstop)

        """Setup processes"""
        if thread_number > mp.cpu_count():
            thread_number = mp.cpu_count() - 2

        self.procs_list = [mp.Process(target=self.run_year_parse_process) for i in range(thread_number)]
        WT = WriterThread()
        self.write_proc = mp.Process(target = WT.run, args = (self.output_queue,))
        
        """Setup files"""
        Y = YearParser((None, None))
        Y.save()
    
    def run_year_parse_process(self):
        while True:
            try:
                input_tuple = self.input_queue.get(block = False)
                Y = YearParser(input_tuple)
                self.output_queue.put(Y.get_pddf())
            except Exception as e:
                print(e)
                print("Queue exhausted, terminating")
                break                        

    def run_processes(self):
            
        for i, proc in enumerate(self.procs_list):
            proc.start()
            print("Started thread {}".format(i))
    
        self.write_proc.start()
        
        for i, proc in enumerate(self.procs_list):
            proc.join()
            print("Joined thread {}".format(i))
        
        self.output_queue.put(("TERMINATE",))
        self.write_proc.join()
        
    
if __name__ == "__main__":
    MP = MultiProcesser()
    MP.run_processes()
