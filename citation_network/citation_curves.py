
import pickle
import bisect
import pdb
import numpy as np

# read pkl citation curves
# read file w years

class CitationCurveSet():
    def __init__(self, voluntaryOnly="False"):
        self.voluntaryOnly = voluntaryOnly
        if self.voluntaryOnly:
            self.citationCurveFileName = "citation_curves_voluntary.pkl"
            self.citationListFileName = "received_citation_list_voluntary.pkl"
            self.citationCountFileName = "received_citation_count_voluntary.pkl"
        else:
            self.citationCurveFileName = "citation_curves.pkl"
            self.citationListFileName = "received_citation_list.pkl"
            self.citationCountFileName = "received_citation_count.pkl"

        with open(citationListFileName, "rb") as rfile:
            self.received_citation_list = pickle.load(rfile)
        
        self.pddf = pd.read_pickle("patents_dates_years.pkl")      # should have: "applied date", "granted date", "applied year", "granted year"
        self.separation = {}
        self.enddated = {}
        
    def parse_curves(self):
        lastdate = max([rcc[-1] for _, rcc in self.received_citation_list.items()])
        for cckey in self.received_citation_list.keys():
            startdate = self.pddf["granted data"][cckey]
            ccurve = np.asarray([date - startdate for date in self.received_citation_list[cckey]])
            self.citation_curves[cckey] = ccurve
            self.enddates[cckey] = lastdate - startdate
        self.maxlen = max([cc[-1] for _, cc in self.citation_curves.items()])
    
    def save_cc(self):
        with open(self.citationCurveFileName, "wb") as wfile:
            pickle.dump([self.citation_curves, self.enddates], wfile, protocol=pickle.HIGHEST_PROTOCOL)
        
    def separate_group(self, memberIDs, criterion):
        self.separation[criterion] = {}
        self.separation[criterion]["members"] = memberIDs
        non_memberIDs = [ID for ID in self.citation_curves.keys() if ID not in memberIDs]
        self.separation[criterion]["nonmembers"] = non_memberIDs

    def draw_citation_curve(self, criterion, quantile_low=0.25, quantile_high=0.75):
        xs = np.arange(self.maxlen)
        mseries = {}
        mseries["members"] = [self.citation_curves[k] for k in self.separation[criterion]["members"]]
        mseries["nonmembers"] = [self.citation_curves[k] for k in self.separation[criterion]["nonmembers"]]
        member_median = self.get_citation_quantiles(mseries["members"], .5, xs)
        member_mean = self.get_citation_mean(mseries["members"], xs)
        member_low = self.get_citation_quantiles(mseries["members"], quantile_low, xs)
        member_high = self.get_citation_quantiles(mseries["members"], quantile_high, xs)
        nonmember_median = self.get_citation_quantiles(mseries["nonmembers"], .5, xs)
        nonmember_mean = self.get_citation_mean(mseries["nonmembers"], xs)
        nonmember_low = self.get_citation_quantiles(mseries["nonmembers"], quantile_low, xs)
        nonmember_high = self.get_citation_quantiles(mseries["nonmembers"], quantile_high, xs)

        # Plot and save
        color1, color2 = 'C2', 'C1'
        label1, label2 = 'green', 'brown'
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
        plt.show()

    def get_citation_quantiles(ser, quantile, xs):
        cq = np.asarray([np.quantile([bisect.bisect(s, x) for s in ser], quantile) for x in xs])
        return cq
        
    def get_citation_mean(ser, xs):
        cm = np.asarray([np.mean([bisect.bisect(s, x) for s in ser]) for x in xs])
        pass cm

    def get_citation_mean(ser, xs):
        csd = np.asarray([np.std([bisect.bisect(s, x) for s in ser]) for x in xs])
        pass csd
    
    def get_observation_numbers(keys, xs):
        #ends = [cc[-1] for key, cc in self.citation_curves.items() if key in keys]
        end_dates = [self.enddates[key] for key in keys]
        ends = list(end_dates)
        ends = ends.sort()
        return np.asarray([bisect.bisect_right(ends, x) for x in xs])

if __name__ == "__main__":
    for vol in [False, True]:
        """prepare citation curves and save"""
        CCS = CitationCurveSet(vol)    
        CCS.save()
        
        """load greenness patterns"""
        selections = {}
        with open("detected_green_patents.pkl", "rb") as rfile:
            keyword_shapira = pd.read_pickle(df, rfile)
            selections["keyword_shapira"] = list(keyword_shapira.index)
        with open("patent_greenness_based_on_CPC_combined.pkl", "rb") as rfile:
            CPC_df = pd.read_pickle(df, rfile)
            selections["GI_envtech"] = list(CPC_df[CPC_df['envtech']==True].index)
            selections["GI_IPC"] = list(CPC_df[CPC_df['IPCGI']==True].index)
        
        """draw central moments and dispersion for green and brown crossectional ensembles"""
        for separ in ["keyword_shapira", "GI_envtech", "GI_IPC"]:
            CCS.separate_group(selections[separ], separ)
            CCS.draw_citation_curve(separ)

    """Exit"""
    exit(0)


"""This pint should never be reached; here are some remaining notes to get this to work"""
raise SystemExit

## notes

{[np.asarray([12, 34, 35,37,98,104]),
 np.asarray([21, 34, 51,77,198,304]),
 np.asarray([2, 33, 35,37,99,224]),
 np.asarray([1, 34, 51,77,198,304]),
 np.asarray([9, 34, 35,37,98,304]),
 np.asarray([21, 34, 51,77,198,304]),
 np.asarray([12, 34, 35,39,98,104]),
 np.asarray([1, 34, 55,77,198,304]),
 np.asarray([12, 34, 35,37,98,104]),
 np.asarray([21, 44, 51,77,198,304]),
 np.asarray([12, 34, 35,37,98,104]),
 np.asarray([1, 34, 51,77,198,304])]
 }
 
 -> averages: take sums, divide by # observations
 
 1. get series of observations; 
     - ser = [end_series - x for x in startdates]
     - ser = ser.sort()
     - xs = list(range(len(ser)+1))
     - [bisect.bisect_right(ser, x) for x in xs]
 
 2. get sum of all members:
     - join lists
     - sort
     - xs = list(range(len(ser)+1))
     - [bisect.bisect_right(ser, x) for x in xs]
 
 3. divide by num obs for every timestep
 
 -> median:
    - have observation number list
    - identify quantile observation for each time  quant*num_obs    r       idx
                                                    0.5   10        5       5
                                                    0.5   11        5.5     5
                                                    0.5   12        6       6
                                                    0.5   13        6.5     6
    # get lowest 
     
 -> std:
     np.stdev([bisect.bisect(s, x) for s in ser])


 -> quantiles:
     np.quantile([bisect.bisect(s, x) for s in ser], quantile)
     
>>> np.std([bisect.bisect(s, 35) for s in axx])
0.6400954789890507
>>> np.mean([bisect.bisect(s, 35) for s in axx])
2.4166666666666665
>>> np.median([bisect.bisect(s, 35) for s in axx])
2.5
>>> np.quantile([bisect.bisect(s, 35) for s in axx], .5)
2.5
