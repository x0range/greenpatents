
import pickle
import bisect
import pdb
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

def rm_leading_zeros(keylist):
    oldlen= -1
    newlen = len(keylist)
    while oldlen != newlen:
        oldlen = newlen
        keylist = [di[1:] if di[0]=="0" else di for di in keylist]
        newlen = len(keylist)
    return keylist

class CitationCurveSet():
    def __init__(self, voluntaryOnly="False"):
        """saving parameters"""
        self.voluntaryOnly = voluntaryOnly
        if self.voluntaryOnly:
            self.citationCurveFileName = "citation_curves_voluntary.pkl"
            self.citationListFileName = "received_citation_list_voluntary.pkl"
            self.citationCountFileName = "received_citation_count_voluntary.pkl"
            self.citationListFileNameCleaned = "received_citation_list_voluntary_cleaned.pkl" 
        else:
            self.citationCurveFileName = "citation_curves.pkl"
            self.citationListFileName = "received_citation_list.pkl"
            self.citationCountFileName = "received_citation_count.pkl"
            self.citationListFileNameCleaned = "received_citation_list_cleaned.pkl" 
        """loading datasets"""
        print("Loading citation lists...")
        if os.path.exists(self.citationListFileNameCleaned):
            to_be_cleaned = False
            with open(self.citationListFileNameCleaned, "rb") as rfile:
                self.received_citation_list = pickle.load(rfile)
        else:
            to_be_cleaned = True
            with open(self.citationListFileName, "rb") as rfile:
                self.received_citation_list = pickle.load(rfile)
        
        print("Loading dates lists...")
        self.pddf = pd.read_pickle("patents_dates_years.pkl")      # should have: "applied date", "granted date", "applied year", "granted year"
        
        """parsing citation curves"""
        self.separation = {}
        self.enddates = {}
        self.citation_curves = {}
        
        if to_be_cleaned:
            print("Done. Now removing unparsable elements: ")
            self.remove_unparsable()
        print("Done. Now parsing: ")
        self.parse_curves()
        print("Done.")
    
    def remove_unparsable(self):
        volunt_yes_no = {True: "_voluntary", False: ""}

        keys = self.received_citation_list.keys()
        print("   Keys acquired")
        difference = list(pd.Index(keys).difference(self.pddf.index))
        print("   Difference set acquired")
        #with open("received_citation_list_difference" + volunt_yes_no[self.voluntaryOnly] + ".pkl", "wb") as wfile:
        #    pickle.dump(difference, wfile, protocol=pickle.HIGHEST_PROTOCOL)

        """ dict comprehension literally takes forever, see other option below """
        #new_dict = {k: v for k, v in self.received_citation_list.items() if v not in difference}
        """ dict manipulation is quick """
        i_max = len(difference)
        for i, ckey in enumerate(difference):
            print("Parsed {0} out of {1}".format(i+1, i_max), end="\r")
            if ckey in self.received_citation_list:
                del self.received_citation_list[ckey]
        
        print("   New dict created. Saving...")
        with open("received_citation_list" + volunt_yes_no[self.voluntaryOnly] + "_cleaned.pkl", "wb") as wfile:
            pickle.dump(self.received_citation_list, wfile,  protocol=pickle.HIGHEST_PROTOCOL)
        
    def parse_curves(self):
        lastdate = max([pd.to_datetime(0) if len(rcc)==0 else rcc[-1] for _, rcc in self.received_citation_list.items()])
        i_max = len(self.received_citation_list.keys())
        for i, cckey in enumerate(self.received_citation_list.keys()):
            print("parsing {0} of {1}".format(i+1, i_max), end="\r")
            startdate = self.pddf["granted date"][cckey]
            ccurve = np.asarray([(date - startdate).days for date in self.received_citation_list[cckey]])
            self.citation_curves[cckey] = ccurve
            self.enddates[cckey] = (lastdate - startdate).days
        self.maxlen = max([pd.to_timedelta(0).days if len(cc)==0 else cc[-1] for _, cc in self.citation_curves.items()])
    
    def save_cc(self):
        print("Saving...")
        with open(self.citationCurveFileName, "wb") as wfile:
            pickle.dump([self.citation_curves, self.enddates], wfile, protocol=pickle.HIGHEST_PROTOCOL)
        print("Done.")
        
    def separate_group(self, memberIDs, criterion):
        print("Separating...")
        self.separation[criterion] = {}
        self.separation[criterion]["members"] = memberIDs
        non_memberIDs = [ID for ID in self.citation_curves.keys() if ID not in memberIDs]
        self.separation[criterion]["nonmembers"] = non_memberIDs
        print("Done.")

    def draw_citation_curve(self, criterion, quantile_low=0.25, quantile_high=0.75):
        print("Computing graphs")
        xs = np.arange(self.maxlen)
        mseries = {}
        mseries["members"] = [self.citation_curves[k] for k in self.separation[criterion]["members"] if k in self.citation_curves]
        mseries["nonmembers"] = [self.citation_curves[k] for k in self.separation[criterion]["nonmembers"] if k in self.citation_curves]
        member_median = self.get_citation_quantiles(mseries["members"], .5, xs)
        member_mean = self.get_citation_mean(mseries["members"], xs)
        member_low = self.get_citation_quantiles(mseries["members"], quantile_low, xs)
        member_high = self.get_citation_quantiles(mseries["members"], quantile_high, xs)
        nonmember_median = self.get_citation_quantiles(mseries["nonmembers"], .5, xs)
        nonmember_mean = self.get_citation_mean(mseries["nonmembers"], xs)
        nonmember_low = self.get_citation_quantiles(mseries["nonmembers"], quantile_low, xs)
        nonmember_high = self.get_citation_quantiles(mseries["nonmembers"], quantile_high, xs)
        print("Done.")

        # Plot and save
        print("Drawing...")
        color1, color2 = 'C2', 'C1'
        label1, label2 = 'green', 'non-green'
        if self.voluntaryOnly:
            outputfilename = "comp_citations_by_age_" + criterion + "voluntaryOnly.pdf"
        else:
            outputfilename = "comp_citations_by_age_" + criterion + ".pdf"
    
        fig = plt.figure()
        ax0 = fig.add_subplot(111)
        ax0.fill_between(xs, member_low, member_high, facecolor=color1, alpha=0.25)
        ax0.fill_between(xs, nonmember_low, nonmember_high, facecolor=color2, alpha=0.25)
        ax0.plot(xs, member_median, color=color1, label=label1)
        ax0.plot(xs, nonmenber_median, color=color2, label=label2)
        ax0.plot(xs, member_mean, dashes=[3, 3], color=color1, label=label1)
        ax0.plot(xs, nonmenber_mean, dashes=[3, 3], color=color2, label=label2)
        ax0.set_ylabel("# Citations")
        ax0.set_xlabel("Patent age")
        ax0.legend(loc='best')
        plt.savefig(outputfilename)
        #plt.show()
        print("Done.")

    def get_citation_quantiles(self, ser, quantile, xs):
        cq = np.asarray([np.quantile([bisect.bisect(s, x) for s in ser], quantile) for x in xs])
        return cq
        
    def get_citation_mean(self, ser, xs):
        cm = np.asarray([np.mean([bisect.bisect(s, x) for s in ser]) for x in xs])
        return cm

    def get_citation_mean(self, ser, xs):
        csd = np.asarray([np.std([bisect.bisect(s, x) for s in ser]) for x in xs])
        return csd
    
    def get_observation_numbers(self, keys, xs):
        #ends = [cc[-1] for key, cc in self.citation_curves.items() if key in keys]
        end_dates = [self.enddates[key] for key in keys]
        ends = list(end_dates)
        ends = ends.sort()
        return np.asarray([bisect.bisect_right(ends, x) for x in xs])

if __name__ == "__main__":
    for vol in [False, True]:
        print("Commencing voluntary={0}...".format(vol))
        """prepare citation curves and save"""
        CCS = CitationCurveSet(vol)    
        CCS.save_cc()
        
        """load greenness patterns"""
        selections = {}
        with open("detected_green_patents.pkl", "rb") as rfile:
            keyword_shapira = pd.read_pickle(rfile)
            selections["keyword_shapira"] = list(keyword_shapira.index)
        with open("patent_greenness_based_on_CPC_all.pkl", "rb") as rfile:
            CPC_df = pd.read_pickle(rfile)
            selections["GI_envtech"] = list(CPC_df[CPC_df['envtech']==True].index)
            selections["GI_IPC"] = list(CPC_df[CPC_df['IPCGI']==True].index)
        
        """draw central moments and dispersion for green and brown crossectional ensembles"""
        for separ in ["keyword_shapira", "GI_envtech", "GI_IPC"]:
            CCS.separate_group(selections[separ], separ)
            CCS.draw_citation_curve(separ)

    """Exit"""
    exit(0)


