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
from matplotlib import gridspec

""" Set to non-GUI environment before importing pyplot"""
matplotlib.use('Agg')
import matplotlib.pyplot as plt

""" auxiliary functions"""

def rm_leading_zeros(keylist):
    """ Function to remove leading zeros and spaces from list of strings (such as patent IDs)
     Arguments: keylist: list of strings
     Returns: list of strings"""
    keylist = [di.strip() for di in keylist]
    maxlen = np.max([len(di) for di in keylist])
    for i in range(maxlen - 1):
        keylist = [di[1:] if di[0]=="0" else di for di in keylist]
        newlen = len(keylist)
    return keylist


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
        self.patentYearDataframeFile = "patents_dates_years.pkl"
        if self.voluntaryOnly:
            self.citationCurveFileName = "citation_curves_voluntary.pkl"
            self.citationCurveTLenFileName = "citation_curves_total_lengths_voluntary.pkl"
            self.citationCurveMatrixFileName = "citation_curves_voluntary.npz"
            self.citationCurveMatrixKeysFileName = "citation_curves_voluntary_keys.pkl"
            self.separationGreenFile = "citation_curves_voluntary_separation_green.pkl"
            self.separationClassFile = "citation_curves_voluntary_separation_class.pkl"
            self.separationYearFile = "citation_curves_voluntary_separation_year.pkl"
        else:
            self.citationCurveFileName = "citation_curves.pkl"
            self.citationCurveTLenFileName = "citation_curves_total_lengths.pkl"
            self.citationCurveMatrixFileName = "citation_curves.npz"
            self.citationCurveMatrixKeysFileName = "citation_curves_keys.pkl"
            self.separationGreenFile = "citation_curves_separation_green.pkl"
            self.separationClassFile = "citation_curves_separation_class.pkl"
            self.separationYearFile = "citation_curves_separation_year.pkl"
                            
        self.green_separation = None
        self.year_separation = None
        self.class_separation = None

        
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
            pddf = pd.read_pickle(self.patentYearDataframeFile)      # should have: "applied date", "granted date", "applied year", "granted year"
            
            print("Removing empty entries from citation curves...")
            for key in np.asarray(list(self.citation_curves.keys())):
                if len(self.citation_curves[key]) == 0:
                    del self.citation_curves[key]
            
            print("Obtaining keys...")
            self.citation_curves_keys = np.asarray(list(self.citation_curves.keys()))
            print("Cleaning and sorting dates list...")
            #pddf = pddf.loc[self.citation_curves_keys]
            #pddf = pddf.loc[pddf["granted date"].notnull()]
            pddf = pddf.reindex(self.citation_curves_keys)
            pddf = pddf.reindex(pddf["granted date"].notnull())
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
        
    def populate_class_separation(self, cpc_matrix_file="patent_classification_matrix_all.npz", cpc_keys_file="patent_classification_matrix_node_keys7.pkl"):
        """Method for populating separation of patents (citation curves) by patent CPC classes.
           The method populates the variable self.class_separation as a pandas dataframe with bool indicators of whether
                the patent belongs to a each of the CPC sections. This can easily be extended to classes by using
                    categs = np.unique([k[:2] for k in cpc_keys[2]])
                instead of
                    categs = np.unique([k[0] for k in cpc_keys[2]])
            Arguments:
                cpc_matrix_file: str    -   filename of patent classification matrix
                cpc_keys_file:  str     -   filename of pickle file containing keys for patent classification matrix
            Returns None."""
        if os.path.exists(self.separationClassFile):
            """Do not recreate if the separation exists"""
            with open(self.separationClassFile, "rb") as rfile:
                self.class_separation = pd.read_pickle(rfile)
        else:
            """Load matrix"""
            cpc = sp.load_npz(cpc_matrix_file)
            with open(cpc_keys_file, "rb") as rfile:
                cpc_keys = pickle.load(rfile)
            
            """Define categories"""
            categs = np.unique([k[0] for k in cpc_keys[2]])     # sections
            #categs = np.unique([k[:2] for k in cpc_keys[2]])    # classes
            #categs = np.unique(cpc_keys[2])                     # subclasses
            
            """Create and populate data frame"""
            cpc_df = pd.DataFrame(index=rm_leading_zeros(cpc_keys[0]))
            
            for cat in categs:
                columns = np.where(np.array([k[0] for k in cpc_keys[2]])==cat)[0]
                sum_columns = cpc[:,columns].sum(axis=1)
                cat_presence = np.array(sum_columns) > 0
                cpc_df[cat] = cat_presence
            
            """Select correct subset in correct order"""
            #self.class_separation = cpc_df.loc[self.citation_curves_keys]      # deprecated
            self.class_separation = cpc_df.reindex(self.citation_curves_keys)
            
            """Fill NA entries as False (not belonging to this category)"""
            for cat in categs:
                self.class_separation[cat].fillna(False,inplace=True)
            
            """Save"""
            self.class_separation.to_pickle(self.separationClassFile)
        
    def populate_green_separation(self, keyword_greenness_file="detected_green_patents.pkl", cpc_greenness_file="patent_greenness_based_on_CPC_all.pkl"):
        """Method for populating separation of patents (citation curves) by patent greenness indicators.
           The method populates the variable self.green_separation as a pandas dataframe with bool indicators of whether
                the patent belongs to a each of the green patent selections: the GIs by envtech and IPC, as well as 
                keyword-based selection.
                Keyword based currently only has shapira et al. Could and should be extended, using a list of files instead.
            Arguments:
                keyword_greenness_file: str     -   filename of keyword based (based on Shapira et al.) identification
                cpc_greenness_file:  str        -   filename of CPC class based identifications
            Returns None."""
        if os.path.exists(self.separationGreenFile):
            """Do not recreate if the separation exists"""
            with open(self.separationGreenFile, "rb") as rfile:
                self.green_separation = pd.read_pickle(rfile)
        else:
            """CPC class based"""
            with open(cpc_greenness_file, "rb") as rfile:
                """Load data frame"""
                CPC_df = pd.read_pickle(rfile)
                CPC_df.index = rm_leading_zeros(CPC_df.index)
            """Select correct IDs in correct order"""
            self.green_separation = CPC_df.reindex(self.citation_curves_keys)
            
            """Keyword based"""
            with open(keyword_greenness_file, "rb") as rfile:
                """Load data frame"""
                keyword_shapira = pd.read_pickle(rfile)
                keyword_shapira.index = rm_leading_zeros(keyword_shapira.index)
                """Remove pattern match information, only keep index (all rows were positive identifications)"""
                keyword_shapira["keyword_shapira"] = True
                keyword_shapira = keyword_shapira[["keyword_shapira"]]
            """Remove duplicate rows"""                     # TODO: why are there duplicate rows??
            keyword_shapira = keyword_shapira[~keyword_shapira.index.duplicated(keep='first')]
            """Select correct IDs in correct order"""
            keyword_shapira = keyword_shapira.reindex(self.citation_curves_keys)
            """Fill NA as False. (All present IDs are True.)"""
            keyword_shapira["keyword_shapira"].fillna(False,inplace=True)    #TODO: colname
            
            """Attach keyword based to dataframe"""
            self.green_separation["keyword_shapira"] = keyword_shapira["keyword_shapira"]
            
            """Save"""
            self.green_separation.to_pickle(self.separationGreenFile)
    
    def populate_year_separation(self):
        """Method for populating separation of patents (citation curves) by granted years.
           The method populates the variable self.year_separation as a pandas dataframe with bool indicators of the
                year the patent was granted.
            Arguments: None.
            Returns None."""
        if os.path.exists(self.separationYearFile):
            """Do not recreate if the separation exists"""
            with open(self.separationYearFile, "rb") as rfile:
                self.year_separation = pd.read_pickle(rfile)
        else:
            """Load patent year dataframe"""
            pddf = pd.read_pickle(self.patentYearDataframeFile)      # should have: "applied date", "granted date", "applied year", "granted year"
            #                                                        # TODO: Are the leading zeros already removed here?
            
            """Select categories"""
            categs = np.unique(np.asarray(pddf["granted year"]))
            
            """Apply bool colums"""
            for cat in categs:
                pddf[str(cat)] = pddf["granted year"]==cat
            
            """Reduce dataframe to the bool columns for the years only"""
            pddf = pddf[[str(cat) for cat in categs]]

            """Select correct IDs in correct order"""
            #self.year_separation = pddf.loc[self.citation_curves_keys]     # deprecated
            self.year_separation = pddf.reindex(self.citation_curves_keys)
            
            """Save"""
            self.year_separation.to_pickle(self.separationYearFile)

    def separate_set(self, separ, criterion, class_sep=None, year_sep=None):
        """Function to separate sets of patents by greenness and additional categories.
            Arguments:
                criterion: string           - criterion name
                class_sep: None or str      - CPC class category to be selected (if None, select all)
                year_sep: None or str       - Granted year category to be selected (if None, select all)
                quantile_low: float         - lower bound of inter quantile range
                quantile_high: float        - upper bound of inter quantile range
            Returns: 
                numpy ndarray of bool       - selection of members (marked True)
                numpy ndarray of bool       - selection of non-members (members market False, others True)
                string                      - criterion name for selection, for use in output file name
            """
        """Separation by green tech membership"""
        selection_members = self.green_separation[criterion]==True
        selection_nonmembers = self.green_separation[criterion]==False
        criterion_name = criterion
        
        """Add separation by other categories logically"""
        if class_sep is not None:
            selection_members = selection_members & self.class_separation[class_sep]
            selection_nonmembers = selection_nonmembers & self.class_separation[class_sep]
            criterion_name += "_class_" + class_sep
        if year_sep is not None:
            selection_members = selection_members & self.year_separation[year_sep]
            selection_nonmembers = selection_nonmembers & self.year_separation[year_sep]
            criterion_name += "_" + year_sep 

        """Typecast from pandas to numpy bool type (otherwise the sparse matrix separation below fails)"""
        selection_members = np.asarray(selection_members)
        selection_nonmembers = np.asarray(selection_nonmembers)
        
        return selection_members, selection_nonmembers, criterion_name

    def draw_citation_curve(self, criterion, class_sep=None, year_sep=None, quantile_low=0.25, quantile_high=0.75):
        """Function for drawing representative member and non-member citation curves using a particular criterion.
            Arguments:
                criterion: string           - criterion name
                class_sep: None or str      - CPC class category to be selected (if None, select all)
                year_sep: None or str       - Granted year category to be selected (if None, select all)
                quantile_low: float         - lower bound of inter quantile range
                quantile_high: float        - upper bound of inter quantile range
            Returns: None"""
        print("Computing graphs for " + criterion + " class " + str(class_sep) + " year " + str(year_sep))
        xs = np.arange(0, self.maxlen, 150)
        mseries = {}
        tlens = {}
        
        """ separate matrix"""
        selection_members, selection_nonmembers, criterion_name = self.separate_set(criterion = criterion,
                                                                                class_sep = class_sep, 
                                                                                year_sep = year_sep)

        print("   ...separating matrix")
        #pdb.set_trace()
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
        if member_mean is not None and nonmember_mean is not None:
            if self.voluntaryOnly:
                outputfilename = "comp_citations_by_age_" + criterion_name + "_voluntaryOnly.pdf"
            else:
                outputfilename = "comp_citations_by_age_" + criterion_name + ".pdf"
            self.draw_time_development(labels = ['green', 'non-green'],
                                       colors = ['C2', 'C1'],
                                       means = [member_mean, nonmember_mean],
                                       medians = [member_median, nonmember_median],
                                       iqr_high = [member_high, nonmember_high],
                                       iqr_low = [member_low, nonmember_low],
                                       xs = xs,
                                       xlabel = "Patent age",
                                       ylabel = "# Citations",
                                       outputfilename = outputfilename)

    def draw_time_development(self, labels, colors, means, medians, iqr_high, iqr_low, xs, xlabel, ylabel, outputfilename):
        """Function to draw time development curves with mean, median, IQR
            Arguments:
                labels: list of str         - curve labels
                colors: list of str         - curve colors
                means: list of 1-d numpy    - mean time series
                medians: list of 1-d numpy  - median time series
                iqr_high:                   - upper end of interquantile range time series
                iqr_low:                    - lower end of interquantile range time series
                xs: 1-d numpy               - times (x-axis value series)
                xlabel: str                 - X axis label
                ylabel: str                 - Y axis label
                outputfilename: str         - output file name
            Returns None.
            """
        assert len(labels) == len(colors) == len(means) == len(medians) == len (iqr_high) == len(iqr_low)
        print("Drawing...")
        fig = plt.figure()
        ax0 = fig.add_subplot(111)
        for i in range(len(labels)):
            ax0.fill_between(xs, iqr_low[i], iqr_high[i], facecolor=colors[i], alpha=0.25)
            ax0.plot(xs, medians[i], color=colors[i], label=labels[i])
            ax0.plot(xs, means[i], dashes=[3, 3], color=colors[i])
        ax0.set_ylabel(ylabel)
        ax0.set_xlabel(xlabel)
        ax0.legend(loc='best')
        plt.savefig(outputfilename)
        #plt.show()
        print("Done.")

    def get_csr_quantiles_and_mean(self, csr_matx, tlen_matx, quantiles, xs):
        """Function to compute quantiles and mean and standard deviation from citation curve csr matrix.
            Arguments:
                csr_matx: scipy csr sparse matrix     - the citation curve matrix, lines (patents) sorted by age
                tlen_matx: numpy array                  - list of patent ages sorted in the same way as the matrix
                quantiles: list of float                - quantiles to be computed
                xs: numpy array                         - x values of the resulting curve
            Returns: tuple of
                means: numpy array          - means
                stds: numpy array           - standard deviations
                qs: tuple of numpy arrays   - quantiles
            """
        try:
            assert csr_matx.shape[0] > 0
        except:
            print("Error: selection has no data points. Skipping.")
            return None, None, (None, None, None)                   # TODO: find more generic way to return unsuccessfully?
            #pdb.set_trace()
        qs = {q: [] for q in quantiles}
        means = []
        stds = []
        maxxs = len(xs)
        for idx, x in enumerate(xs):
            print("Computed {0:4d}/{1:4d}".format(idx,maxxs), end="\r")
            # sum matrix to right
            alive = np.argmax(tlen_matx > x)
            rowsums = csr_matx[alive:,:x].sum(axis=1) # submatrix with rows > index(first alive at time x) and columns < (index x)
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

    def draw_shares(self):
        """TODO"""
        
        if self.voluntaryOnly:
            series_filename_postfix = "_voluntaryOnly"
        else:
            series_filename_postfix = ""
        green_by_year = {}
        nongreen_by_year = {}
        green_by_class = {}
        nongreen_by_class = {}
        green_by_year_relative = {}
        green_by_year_relative2 = {}
        nongreen_by_year_relative = {}
        green_by_class_relative = {}
        green_by_class_relative2 = {}
        nongreen_by_class_relative = {}
        dfs = {}
        cats_class = CCS.class_separation.columns
        cats_year = CCS.year_separation.columns
        for separ in self.green_separation.columns:
            green_by_year[separ] = []
            nongreen_by_year[separ] = []
            green_by_class[separ] = []
            nongreen_by_class[separ] = []
            green_by_year_relative[separ] = []
            green_by_year_relative2[separ] = []
            nongreen_by_year_relative[separ] = []
            green_by_class_relative[separ] = []
            green_by_class_relative2[separ] = []
            nongreen_by_class_relative[separ] = []
            dfs[separ] = pd.DataFrame(index=cats_class)
            for class_sep in cats_class:
                mnumber = np.sum((self.green_separation[separ]==True) & self.class_separation[class_sep])
                nnumber = np.sum((self.green_separation[separ]==False) & self.class_separation[class_sep])
                tnumber = np.sum(self.class_separation[class_sep])
                green_by_class[separ].append(mnumber)
                green_by_class_relative[separ].append(mnumber * 1. / (tnumber))
                green_by_class_relative2[separ].append(mnumber * 1. / (mnumber + nnumber))
                nongreen_by_class[separ].append(nnumber)
                nongreen_by_class_relative[separ].append(nnumber * 1. / (tnumber))
            for year_sep in cats_year:
                mnumber = np.sum((self.green_separation[separ]==True) & self.year_separation[year_sep])
                nnumber = np.sum((self.green_separation[separ]==False) & self.year_separation[year_sep])
                tnumber = np.sum(self.year_separation[year_sep])
                green_by_year[separ].append(mnumber)
                green_by_year_relative[separ].append(mnumber * 1. / (tnumber))
                green_by_year_relative2[separ].append(mnumber * 1. / (mnumber + nnumber))
                nongreen_by_year[separ].append(nnumber)                
                nongreen_by_year_relative[separ].append(nnumber * 1. / (tnumber))
                pdseries = []
                for class_sep in CCS.class_separation.columns:
                    print("Year: " + str(year_sep) + ", Class " + class_sep)
                    #pdb.set_trace()
                    mnumber = np.sum((self.green_separation[separ]==True) & self.class_separation[class_sep] & self.year_separation[year_sep])
                    nnumber = np.sum((self.green_separation[separ]==False) & self.class_separation[class_sep] & self.year_separation[year_sep])
                    pdseries.append(mnumber * 1. / (mnumber + nnumber))     # this time relative to sum of green+non-green, disregarding any unclassified
                dfs[separ][year_sep] = pdseries
            
            """bar plot class"""
            plotfilename = "Shares_by_class_" + separ + series_filename_postfix + ".pdf"
            plot_title = "Shares by class - " + separ
            gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 
            
            ax0 = plt.subplot(gs[0])
            xs = np.arange(len(cats_class))    # the x locations for the groups
            width = 0.35       # the width of the bars: can also be len(x) sequence
            ax0.bar(xs, green_by_class[separ], width, color="C2")
            ax0.bar(xs, nongreen_by_class[separ], width, bottom=green_by_class[separ], color="C1")            
            ax0.set_ylabel('No. of patents')
            ax0.set_xticks(xs)
            ax0.set_xticklabels(["" for cat in cats_class])
            plt.title(plot_title)
            
            ax1 = plt.subplot(gs[1])
            ax1.bar(xs, green_by_class_relative[separ], width, color="C2")
            ax1.bar(xs, nongreen_by_class_relative[separ], width, bottom=green_by_class_relative[separ], color="C1")
            ax1.set_ylabel('Share of patents')
            ax1.set_xticks(xs)
            ax1.set_xticklabels(cats_class)
            plt.tight_layout()
            plt.savefig(plotfilename)

            """bar plot year"""
            plotfilename = "Shares_by_year_" + separ + series_filename_postfix + ".pdf"
            plot_title = "Shares by year - " + separ
            gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 
            
            ax0 = plt.subplot(gs[0])
            xs = np.arange(len(cats_year))    # the x locations for the groups
            width = 0.35       # the width of the bars: can also be len(x) sequence
            ax0.bar(xs, green_by_year[separ], width, color="C2")
            ax0.bar(xs, nongreen_by_year[separ], width, bottom=green_by_year[separ], color="C1")            
            ax0.set_ylabel('No. of patents')
            ax0.set_xticks(xs)
            ax0.set_xticklabels(["" for cat in cats_year])
            plt.title(plot_title)
            
            ax1 = plt.subplot(gs[1])
            ax1.bar(xs, green_by_year_relative[separ], width, color="C2")
            ax1.bar(xs, nongreen_by_year_relative[separ], width, bottom=green_by_year_relative[separ], color="C1")
            ax1.set_ylabel('Share of patents')
            ax1.set_xticks(xs)
            ax1.set_xticklabels([cat if i//5==i/5. else "" for i, cat in enumerate(cats_year)])
            plt.tight_layout()
            plt.savefig(plotfilename)
            
            """heatmap plot"""
            plotfilename = "Shares_by_both_" + separ + series_filename_postfix + ".pdf"
            plot_title = "Shares of green patents by year and class - " + separ
            
            plt.figure()
            plt.pcolor(dfs[separ])
            xlabels = [cat if i//5==i/5. else "" for i, cat in enumerate(dfs[separ].columns)]
            plt.yticks(np.arange(0.5, len(dfs[separ].index), 1), dfs[separ].index)
            plt.xticks(np.arange(0.5, len(dfs[separ].columns), 1), xlabels)
            plt.colorbar()
            plt.title(plot_title)
            plt.tight_layout()
            plt.savefig(plotfilename)
            
        """line plot class"""
        plotfilename = "Shares_by_class_all" + series_filename_postfix + ".pdf"
        plot_title = "Shares by class"
        xs = np.arange(len(cats_class))
        fig, ax = plt.subplots(nrows=3)
        figst = fig.suptitle(plot_title)
        for separ in dfs.keys():
            ax[0].plot(xs, green_by_class[separ], label=separ)
            ax[1].plot(xs, nongreen_by_class[separ], label=separ)
            ax[2].plot(xs, green_by_class_relative2[separ], label=separ)
        ax[0].set_ylabel('Green patents')
        ax[0].set_xticks(xs)
        ax[0].set_xticklabels(["" for cat in cats_class])
        legendhandles, legendlabels = ax[0].get_legend_handles_labels()
        ax[0].legend("best", handles=legendhandles, labels=legendlabels)
        ax[1].set_ylabel('Non-green patents')
        ax[1].set_xticks(xs)
        ax[1].set_xticklabels(["" for cat in cats_class])
        ax[2].set_ylabel('Share green')
        ax[2].set_xticks(xs)
        ax[2].set_xticklabels(cats_class)
        fig.tight_layout()  
        figst.set_y(0.975)
        fig.subplots_adjust(top=0.91)
        fig.savefig(plotfilename)

        """line plot year"""
        plotfilename = "Shares_by_year_all" + series_filename_postfix + ".pdf"
        plot_title = "Shares by year"
        xs = np.arange(len(cats_year))
        fig, ax = plt.subplots(nrows=3)
        figst = fig.suptitle(plot_title)
        for separ in dfs.keys():
            ax[0].plot(xs, green_by_year[separ], label=separ)
            ax[1].plot(xs, nongreen_by_year[separ], label=separ)
            ax[2].plot(xs, green_by_year_relative2[separ], label=separ)
        ax[0].set_ylabel('Green patents')
        ax[0].set_xticks(xs)
        ax[0].set_xticklabels(["" for cat in cats_year])
        legendhandles, legendlabels = ax[0].get_legend_handles_labels()
        ax[0].legend("best", handles=legendhandles, labels=legendlabels)
        ax[1].set_ylabel('Non-green patents')
        ax[1].set_xticks(xs)
        ax[1].set_xticklabels(["" for cat in cats_year])
        ax[2].set_ylabel('Share green')
        ax[2].set_xticks(xs)
        ax[2].set_xticklabels([cat if i//5==i/5. else "" for i, cat in enumerate(cats_year)])
        fig.tight_layout()  
        figst.set_y(0.975)
        fig.subplots_adjust(top=0.91)
        fig.savefig(plotfilename)

        with open("size_data" + series_filename_postfix + ".pkl","wb") as wfile:
            wdata = (green_by_year, nongreen_by_year, green_by_class, nongreen_by_class, green_by_year_relative, green_by_year_relative2, nongreen_by_year_relative, green_by_class_relative, green_by_class_relative2, nongreen_by_class_relative, dfs, cats_class, cats_year)
            #(green_by_year, nongreen_by_year, green_by_class, nongreen_by_class, green_by_year_relative, green_by_year_relative2, nongreen_by_year_relative, green_by_class_relative, green_by_class_relative2, nongreen_by_class_relative, dfs, cats_class, cats_year) = wdata
            pickle.dump(wdata, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        
            

if __name__ == "__main__":
    for vol in [False, True]:
        print("Commencing voluntary={0}...".format(vol))
        """prepare citation curves and save"""
        CCS = CitationCurveSet(vol)    
        
        """load greenness patterns, CPC class patterns, and granted year patterns"""
        CCS.populate_class_separation()
        CCS.populate_year_separation()
        CCS.populate_green_separation()
        
        """visualize sares"""
        #CCS.draw_shares()
        
        """draw central moments and dispersion for green and brown crossectional ensembles"""
        for separ in reversed(CCS.green_separation.columns):                      #TODO: getter method instead of accessing class attribute?
            CCS.draw_citation_curve(separ)
            for class_separ in CCS.class_separation.columns:            #TODO: getter method instead of accessing class attribute?
                CCS.draw_citation_curve(separ, class_sep=class_separ)
            for year_separ in CCS.year_separation.columns:              #TODO: getter method instead of accessing class attribute?
                CCS.draw_citation_curve(separ, year_sep=year_separ)

    """Exit"""
    exit(0)


