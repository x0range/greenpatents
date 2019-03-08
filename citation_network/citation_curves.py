""" Script to create citation curves for different sets of green and non-green patents
  I.e.: conditional on having at least one citation, how many citations is a patent 
        expected to have at each age?"""

""" module imports"""
import pickle
import pdb
import numpy as np
import pandas as pd
import os
import matplotlib
import scipy.sparse as sp

""" Set to non-GUI environment before importing pyplot"""
matplotlib.use('Agg')
import matplotlib.pyplot as plt

""" auxiliary functions"""

def rm_leading_zeros(keylist):
    """ Function to remove leading zeros from list of strings (such as patent IDs)
     Arguments: keylist: list of strings
     Returns: list of strings"""
    oldlen= -1
    newlen = len(keylist)
    while oldlen != newlen:
        oldlen = newlen
        keylist = [di.strip()[1:] if di.strip()[0]=="0" else di.strip() for di in keylist]
        newlen = len(keylist)
    return keylist

def split_list(in_list, members):
    """ Function to create bool lists of members and non-members depending in the presence
        of elements in a second list.
       This may be used to divide a list of patent IDs into green and non-green ones
        with the help of a list of green patent IDs.
       The resulting bool lists can be used to split matrices etc. (as long as these 
       follow the same order of elements)
     Arguments:
       in_list: list of strings: Input list
       members: list of strings: List of member strings
     Returns:
       tuple of list of bools: member indicator list and non-member indicator list
       These lists have the same length as (in_list)"""
    mlist = []
    nmlist = []
    maxidx = len(in_list)
    for idx, ile in enumerate(in_list):
        print("Done {0:7d} / {1:7d}".format(idx, maxidx), end="\r")
        if ile in members:
            mlist.append(True)
            nmlist.append(False)
        else:
            mlist.append(False)
            nmlist.append(True)
    mlist = np.asarray(mlist)
    nmlist = np.asarray(nmlist)
    return mlist, nmlist

""" class definitions"""

""" Citation curve set class: Defines a set of citation curves including patent IDs, separations
    in green and non-green etc etc."""
class CitationCurveSet():
    def __init__(self, voluntaryOnly="False"):
        """Constructor function.
            Arguments:
                voluntaryOnly: bool, Indicator whether complete citation set or only the set of 
                               citations by the applicant should be used
           Returns: Class instance"""

        """save parameters"""
        self.voluntaryOnly = voluntaryOnly
        if self.voluntaryOnly:
            self.citationCurveFileName = "citation_curves_voluntary.pkl"
            self.citationCurveTLenFileName = "citation_curves_total_lengths_voluntary.pkl"
            self.citationCurveMatrixFileName = "citation_curves_voluntary.npz"
            self.citationCurveMatrixKeysFileName = "citation_curves_voluntary_keys.pkl"
            self.separationBoolFilePrefix = "citation_curves_voluntary_separation_bool"
        else:
            self.citationCurveFileName = "citation_curves.pkl"
            self.citationCurveTLenFileName = "citation_curves_total_lengths.pkl"
            self.citationCurveMatrixFileName = "citation_curves.npz"
            self.citationCurveMatrixKeysFileName = "citation_curves_keys.pkl"
            self.separationBoolFilePrefix = "citation_curves_separation_bool"
                            
        self.separation = {}
        
        if os.path.exists(self.citationCurveMatrixFileName):
            print("Data sets found. Loading... ")
            assert os.path.exists(self.citationCurveTLenFileName)
            assert os.path.exists(self.citationCurveMatrixKeysFileName)
            with open(self.citationCurveTLenFileName, "rb") as rfile:
                self.tlen = pickle.load(rfile)
            self.maxlen = max(self.tlen)
            with open(self.citationCurveMatrixKeysFileName, "rb") as rfile:
                self.citation_curves_keys = pickle.load(rfile)
            self.citation_curve_matrix = sp.load_npz(self.citationCurveMatrixFileName) 
            
        else:
            print("Loading citation lists...")
            assert os.path.exists(self.citationCurveFileName)
            with open(self.citationCurveFileName, "rb") as rfile:
                self.citation_curves = pickle.load(rfile)

            print("Loading dates lists...")
            pddf = pd.read_pickle("patents_dates_years.pkl")      # should have: "applied date", "granted date", "applied year", "granted year"
            
            print("Removing empty entries from citation curves...")
            for key in np.asarray(list(self.citation_curves.keys())):
                if len(self.citation_curves[key]) == 0:
                    del self.citation_curves[key]
            
            print("Obtaining keys...")
            self.citation_curves_keys = np.asarray(list(self.citation_curves.keys()))
            print("Cleaning and sorting dates list...")
            pddf = pddf.loc[self.citation_curves_keys]
            pddf = pddf.loc[pddf["granted date"].notnull()]
            pddf = pddf.sort_values(by=["granted date"], ascending=False)
            print("Obtaining cleaned keys...")
            self.citation_curves_keys = np.asarray(pddf.index)
            
            print("Populating citation curve length records...")
            #last_granted_date = max(pddf["granted date"])
            last_possible_citation_date = pd.to_datetime("2018-09-01")                                  # this is about when we downloaded the citation file
            self.tlen = np.asarray([td.days for td in (last_possible_citation_date - pddf["granted date"])])
            self.maxlen = max(self.tlen)
            
            print("Converting citation curves into sparse matrix...")
            self.citation_curve_matrix = None
            self.populate_citation_curve_matrix()
            
            print("Freeing memory...")
            del self.citation_curves
            
            print("Saving citation curves as sparse matrix and saving associated records...")
            sp.save_npz(self.citationCurveMatrixFileName, self.citation_curve_matrix)
            with open(self.citationCurveMatrixKeysFileName, "wb") as wfile:
                pickle.dump(self.citation_curves_keys, wfile, protocol=pickle.HIGHEST_PROTOCOL)
            with open(self.citationCurveTLenFileName, "wb") as wfile:
                pickle.dump(self.tlen, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        
        assert self.citation_curve_matrix.shape[0] == len(self.tlen) == len(self.citation_curves_keys)
        print("Sanity check succeeded. All set up.")
    
    def populate_citation_curve_matrix(self):
        """Function to transform citation curves in dict fromat into csr sparse matrix.
                The sparse matrix lists the number of new citation by days of age of the patent.
                Summing over rows up to a certain column will thus conveniently give the number of citations on that day.
                The matrix is sorted by ages of the patents (i.e. inversely by length of life so far). Consequently
                subsetting the rows allows to get the subset of patents alive in the dataset after a certain day of life.
            Arguments: None
            Resturns None"""
        self.citation_curve_matrix = sp.dok_matrix((len(self.citation_curves_keys), self.maxlen+1), dtype=np.int8)
        maxidx = len(self.citation_curves_keys)
        for idx, key in enumerate(self.citation_curves_keys):
            print("Done {0:7d} / {1:7d}".format(idx, maxidx), end="\r")
            times = self.citation_curves[key]
            inttimes = [td.days for td in times]
            unique_inttimes, count_inttimes = np.unique(inttimes, return_index=True)
            duplicates = np.setdiff1d(np.arange(len(inttimes)), count_inttimes)
            try:
                self.citation_curve_matrix[idx, unique_inttimes] = 1
                for dup in duplicates:
                    self.citation_curve_matrix[idx, dup] += 1
            except:
                print("\nFailed at: self.citation_curve_matrix[idx, inttimes] = 1")
                pdb.set_trace()

        self.citation_curve_matrix = self.citation_curve_matrix.tocsr()
        
    
    def draw_citation_curve(self, criterion, memberIDs, quantile_low=0.25, quantile_high=0.75):
        """Function for drawing representative member and non-member citation curves using a particular criterion.
            Arguments:
                criterion: string           - criterion name
                memberIDs: list of strings  - list of member patent IDs
                quantile_low: float         - lower bound of inter quantile range
                quantile_high: float         - upper bound of inter quantile range
            Returns: None"""
        print("Computing graphs for " + criterion)
        xs = np.arange(0, self.maxlen, 150)
        
        """ separate matrix"""
        mseries = {}
        tlens = {}
        separationBoolFile = self.separationBoolFilePrefix + "_" + criterion + ".pkl"
        if os.path.exists(separationBoolFile):
            print("   ...separation file found")
            print("   ...loading separation matrix")
            with open(separationBoolFile, "rb") as rfile:
               (selection_members, selection_nonmembers) = pickle.load(rfile)
            
        else:
            print("   ...no separation file found")
            print("   ...computing separation")
            selection_members, selection_nonmembers = split_list(self.citation_curves_keys, memberIDs)
            with open(separationBoolFile, "wb") as wfile:
                pickle.dump((selection_members, selection_nonmembers), wfile, protocol=pickle.HIGHEST_PROTOCOL)
            
        #sep_true_false = np.in1d(self.citation_curves_keys, memberIDs)   # gives bool list
        #selection_members = np.where(sep_true_false)[0]
        #selection_nonmembers = np.where(sep_true_false == False)[0]
        print("   ...separating matrix")
        mseries["members"] = self.citation_curve_matrix[selection_members]
        mseries["nonmembers"] = self.citation_curve_matrix[selection_nonmembers]
        tlens["members"] = self.tlen[selection_members]
        tlens["nonmembers"] = self.tlen[selection_nonmembers]
        
        # compute moments
        print("   ...computing moments")
        member_mean, member_std, (member_low, member_median, member_high) = self.get_csr_quantiles_and_mean(
                                                                    mseries["members"], 
                                                                    tlens["members"], 
                                                                    [0.25, 0.5, 0.75], 
                                                                    xs)
        nonmember_mean, nonmember_std, (nonmember_low, nonmember_median, nonmember_high) = self.get_csr_quantiles_and_mean(
                                                                    mseries["nonmembers"], 
                                                                    tlens["nonmembers"], 
                                                                    [0.25, 0.5, 0.75], 
                                                                    xs)
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
        ax0.plot(xs, nonmember_median, color=color2, label=label2)
        ax0.plot(xs, member_mean, dashes=[3, 3], color=color1, label=label1)
        ax0.plot(xs, nonmember_mean, dashes=[3, 3], color=color2, label=label2)
        ax0.set_ylabel("# Citations")
        ax0.set_xlabel("Patent age")
        ax0.legend(loc='best')
        plt.savefig(outputfilename)
        #plt.show()
        print("Done.")

    def get_csr_quantiles_and_mean(self, csr_matx, tlen_matx, quantiles, xs):
        """Function to compute quantiles and mean and standard deviation from citation curve csr matrix.
            Arguments:
                csr_matrix: scipy csr sparse matrix     - the citation curve matrix, lines (patents) sorted by age
                tlen_matx: numpy array                  - list of patent ages sorted in the same way as the matrix
                quantiles: list of float                - quantiles to be computed
                xs: numpy array                         - x values of the resulting curve
            Returns: tuple of
                means: numpy array          - means
                stds: numpy array           - standard deviations
                qs: tuple of numpy arrays   - quantiles
            """
        qs = {q: [] for q in quantiles}
        means = []
        stds = []
        maxxs = len(xs)
        for idx, x in enumerate(xs):
            print("Computed {0:4d}/{1:4d}".format(idx,maxxs), end="\r")
            # sum matrix to right
            alive = np.argmax(tlen_matx > x)
            rowsums = self.citation_curve_matrix[alive:,:x].sum(axis=1) # submatrix with rows > index(first alive at time x) and columns < (index x)
            # compute quantiles over this
            for q in quantiles:
                qs[q].append(np.quantile(rowsums, q))
            means.append(np.mean(rowsums))        
            stds.append(np.std(rowsums))        
        # transform qs and means to ndarray
        for key in qs.keys():
            qs[key] = np.asarray(qs[key])
        means = np.asarray(means)
        stds = np.asarray(stds)
        return means, stds, qs.values()

    
    #def get_observation_numbers(self, keys, xs):
    #    #ends = [cc[-1] for key, cc in self.citation_curves.items() if key in keys]
    #    end_dates = [self.enddates[key] for key in keys]
    #    ends = list(end_dates)
    #    ends = ends.sort()
    #    return np.asarray([bisect.bisect_right(ends, x) for x in xs])

if __name__ == "__main__":
    for vol in [False, True]:
        print("Commencing voluntary={0}...".format(vol))
        """prepare citation curves and save"""
        CCS = CitationCurveSet(vol)    
        
        """load greenness patterns"""
        selections = {}
        with open("detected_green_patents.pkl", "rb") as rfile:
            keyword_shapira = pd.read_pickle(rfile)
            selections["keyword_shapira"] = rm_leading_zeros(list(keyword_shapira.index))
        with open("patent_greenness_based_on_CPC_all.pkl", "rb") as rfile:
            CPC_df = pd.read_pickle(rfile)
            selections["GI_envtech"] = rm_leading_zeros(list(CPC_df[CPC_df['envtech']==True].index))
            selections["GI_IPC"] = rm_leading_zeros(list(CPC_df[CPC_df['IPCGI']==True].index))
        
        """draw central moments and dispersion for green and brown crossectional ensembles"""
        for separ in ["GI_envtech", "GI_IPC", "keyword_shapira"]:
            CCS.draw_citation_curve(separ, selections[separ])

    """Exit"""
    exit(0)


