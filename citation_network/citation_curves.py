
import pickle
#import bisect
#import pdb
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import scipy.sparse as sp

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
            self.citationCurveTLenFileName = "citation_curves_total_lengths_voluntary.pkl"
            self.citationCurveMatrixFileName = "citation_curves_voluntary.npz"
            self.citationCurveMatrixKeysFileName = "citation_curves_voluntary_keys.pkl"
        else:
            self.citationCurveFileName = "citation_curves.pkl"
            self.citationCurveTLenFileName = "citation_curves_total_lengths.pkl"
            self.citationCurveMatrixFileName = "citation_curves.npz"
            self.citationCurveMatrixKeysFileName = "citation_curves_keys.pkl"
                            
        self.separation = {}
        
        if os.path.exists(self.citationCurveMatrixFileName):
            print("Data sets found. Loading... ")
            assert os.path.exists(self.citationCurveTLenFileName)
            assert os.path.exists(self.citationCurveMatrixKeysFileName)
            with open(self.citationCurveTLenFileName, "rb") as rfile:
                self.tlen = pickle.load(rfile)
            with open(self.citationCurveMatrixKeysFileName, "rb") as rfile:
                self.tlen = pickle.load(rfile)
            self.citation_curve_matrix = sp.sparse.load_npz(self.citationCurveMatrixFileName) 

        else:
            
            print("Loading citation lists...")
            assert os.path.exists(self.citationCurveFileName)
            with open(self.citationCurveFileName, "rb") as rfile:
                self.citation_curves = pickle.load(rfile)

            print("Loading dates lists...")
            self.pddf = pd.read_pickle("patents_dates_years.pkl")      # should have: "applied date", "granted date", "applied year", "granted year"
            
            print("Removing empty entries from citation curves...")
            for key in self.citation_curves.keys():
                if len(self.citation_curves[key]) == 0:
                    del self.citation_curves[key]
            
            print("Obtaining keys...")
            self.citation_curves_keys = np.asarray(list(self.citation_curves.keys()))
            print("Cleaning and sorting dates list...")
            self.pddf = self.pddf.loc[self.citation_curves_keys]
            self.pddf = self.pddf.loc[self.pddf["granted date"].notnull()]
            self.pddf = self.pddf.sort_values(by=["granted date"], ascending=False)
            print("Obtaining cleaned keys...")
            self.citation_curves_keys = np.asarray(self.pddf.index)
            
            print("Populating citation curve length records...")
            last_granted_date = max(pddf["granted date"])
            self.tlen = np.asarray([td.days for td in (last_granted_date - pddf["granted date"])])
            self.maxlen = lax(self.tlen)
            
            print("Converting citation curves into sparse matrix...")
            self.citation_curve_matrix = None
            self.populate_citation_curve_matrix()
            
            print("Freeing memory...")
            del self.citation_curves
            
            print("Saving citation curves as sparse matrix and saving associated records...")
            sp.sparse.save_npz(self.citationCurveMatrixFileName, self.citation_curve_matrix)
            with open(self.citationCurveMatrixKeysFileName, "wb") as wfile:
                pickle.dump(self.citation_curves_keys, wfile, protocol=pickle.HIGHEST_PROTOCOL)
            with open(self.citationCurveTLenFileName, "wb") as wfile:
                pickle.dump(self.tlen, wfile, protocol=pickle.HIGHEST_PROTOCOL)
                
        assert self.citation_curve_matrix[0] == len(self.tlen) == len(self.citation_curves_keys)
        print("Sanity check succeeded. All set up.")
    
    def populate_citation_curve_matrix(self):
        self.citation_curve_matrix = sp.dok_matrix((len(self.citation_curve_matrix), self.maxlen), dtype=np.int8)
        for idx, key in enumerate(self.citation_curves_keys):
            times = self.citation_curves[key]
            inttimes =  [td.days for td in times]
            self.citation_curve_matrix[idx, inttimes] = 1

        self.citation_curve_matrix = self.citation_curve_matrix.tocsr()
        
    
    def draw_citation_curve(self, criterion, memberIDs, quantile_low=0.25, quantile_high=0.75):
        print("Computing graphs")
        xs = np.arange(self.maxlen)

        # separate matrix
        mseries = {}
        tlens = {}
        sep_true_false = np.in1d(self.citation_curves_keys, memberIDs)   # gives bool list
        selection_members = np.where(sep_true_false)[0]
        selection_nonmembers = np.where(sep_true_false == False)[0]
        mseries["members"] = self.citation_curve_matrix[selection_members]
        mseries["nonmembers"] = self.citation_curve_matrix[selection_nonmembers]
        tlens["members"] = self.tlen[selection_members]
        tlens["nonmembers"] = self.tlen[selection_nonmembers]
        
        # compute moments
        member_mean, member_std, (member_low, member_median, member_high) = get_csr_quantiles_and_mean(
                                                                    mseries["members"], 
                                                                    tlens["members"], 
                                                                    [0.25, 0.5, 0.75], 
                                                                    xs)
        nonmember_mean, nonmember_std, (nonmember_low, nonmember_median, nonmember_high) = get_csr_quantiles_and_mean(
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
        ax0.plot(xs, nonmenber_median, color=color2, label=label2)
        ax0.plot(xs, member_mean, dashes=[3, 3], color=color1, label=label1)
        ax0.plot(xs, nonmenber_mean, dashes=[3, 3], color=color2, label=label2)
        ax0.set_ylabel("# Citations")
        ax0.set_xlabel("Patent age")
        ax0.legend(loc='best')
        plt.savefig(outputfilename)
        #plt.show()
        print("Done.")

    def get_csr_quantiles_and_mean(self, csr_matx, tlen_matx, quantiles, xs):
        qs = {q: [] for q in quantiles}
        means = []
        stds = []
        for x in xs:
            # sum matrix to right
            alive = np.argmax(tlen_matx > x)
            rowsums = citation_curve_matrix_csr[self.alive:,:x].sum(axis=1) # submatrix with rows > index(first alive at time x) and columns < (index x)
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
        return means, stds, qs

    
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
            selections["keyword_shapira"] = list(keyword_shapira.index)
        with open("patent_greenness_based_on_CPC_all.pkl", "rb") as rfile:
            CPC_df = pd.read_pickle(rfile)
            selections["GI_envtech"] = list(CPC_df[CPC_df['envtech']==True].index)
            selections["GI_IPC"] = list(CPC_df[CPC_df['IPCGI']==True].index)
        
        """draw central moments and dispersion for green and brown crossectional ensembles"""
        for separ in ["keyword_shapira", "GI_envtech", "GI_IPC"]:
            CCS.draw_citation_curve(separ, selections[separ])

    """Exit"""
    exit(0)


