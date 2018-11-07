"""Script to parse the citation network from USPTO
        Website: http://www.patentsview.org/download/
        Data: http://s3.amazonaws.com/data-patentsview-org/20180528/download/uspatentcitation.tsv.zip
        Code book: http://www.patentsview.org/data/Patents_DB_dictionary_bulk_downloads.xlsx
   Script will read the list of nodes provided by citation_parse_full_node_list.py for efficiency. So 
        citation_parse_full_node_list.py must be executed first.
   Script will compute and save the network, citation counts, and pageranks."""

import networkx as nx
import pandas as pd
import os
import psutil
import pdb
import pickle
import scipy as sp
import numpy as np
import zipfile
import argparse

"""Argument handling"""
parser = argparse.ArgumentParser(description='Script to parse patent citations to obtain network, pageranks, statistics')
parser.add_argument("--networks", action="store_true", help="build and save citation network and pageranks")
parser.add_argument("--statistics", action="store_true", help="obtain and save citation statistics by patent")
parser.add_argument("--voluntaryonly", action="store_true", help="include only citations created by the applicant, not the examiner, not other, not unknown. Can be combined with --networks or with --statictics or both.")
args = parser.parse_args()
if args.networks == False and args.statistics == False:
    print("Error: No options received, script does not know what to do.")    
    parser.print_help()
    raise SystemExit

"""Citation space class"""
class CitationSpace():
    def __init__(self, buildNetworks=True, voluntaryOnly=False, buildCitationCurve=False):
        """Constructor. Reads node list, prepares sparse matrix and variables.
            Arguments:
                buildNetworks   - bool - should the citation matrix be constructed, 
                voluntaryOnly   - bool - should only citations put by the applicant be considered or all citations, 
                buildCitationCurve - bool - should the citations for each patent be recorded with dates.
            Returns:
                CitationSpace instance."""
        self.buildNetworks = buildNetworks
        self.voluntaryOnly = voluntaryOnly 
        self.buildCitationCurve = buildCitationCurve
            
        # load nodelist if it exists
        if voluntaryOnly:
            fullNodeListPath = "full_node_list_voluntary.pkl"
        else:
            fullNodeListPath = "full_node_list.pkl"
        if os.path.exists(fullNodeListPath):
            with open(fullNodeListPath, "rb") as ifile:
                self.DGnodes = pickle.load(ifile)
                self.DGindex = len(self.DGnodes)
        else:
            assert False, "Error: script requires prerecorded nodelist. Please execute citation_parse_full_node_list.py first"
        
        if self.buildNetworks:
            #self.DG = nx.DiGraph()
            self.DGA = sp.sparse.dok_matrix((self.DGindex, self.DGindex), dtype=bool)
            self.pageranks = {}
        
        if self.buildCitationCurve:
            self.citation_curves = {}           # should eventually hold the number of citations up to day x vs. age of patent. For this we would still have to parse the application date (and the mapping from patent to application). 
            self.received_citation_list = {patentID: [] for patentID in self.DGnodes}
            self.received_citation_count = {patentID: 0 for patentID in self.DGnodes}

    def record_node(self, label):
        """Method to record additional nodes. This should be done by the citation_parse_full_node_list.py script,
           so this method will throw an error if called in this script. Logic is included in comments below."""
        try:
            assert False, "Error: unknown node encountered"
        except:
            pdb.set_trace()
        #self.DGnodes[label] = self.DGindex
        #self.DGindex += 1
        #return self.DGindex - 1

    def parse_citation_file_line(self, line):
        """Method to parse a single citation as recorded in the USPTO source file
            Arguments:
                line - type: bytes - the line to be parsed
            Returns:
                None."""
        elementi = line.decode("UTF-8").split("\t")
        assert len(elementi) == 9
        origin, destination, date, cited_by = elementi[1], elementi[2], elementi[3], elementi[7]
        cited_by = cited_by.replace("cited by ", "")
        if self.buildNetworks and ((not self.voluntaryOnly) or (cited_by == "applicant")):
            origin_idx, destination_idx = self.DGnodes.get(origin), self.DGnodes.get(destination)
            if origin_idx is None:
                origin_idx = self.record_node(origin)
            if destination_idx is None:
                destination_idx = self.record_node(destination)
            self.DGA[origin_idx, destination_idx] = 1
        if self.buildCitationCurve and ((not self.voluntaryOnly) or (cited_by == "applicant")):
            try:
                if date[-1] == "0":
                    date = date[:-1] + "1"
                date = pd.to_datetime(date)
                self.received_citation_count[destination] += 1
                self.received_citation_list[destination].append(date)
            except:
                print("\nIrregular date encountered " + str(date))
                self.received_citation_list[destination].append(pd.to_datetime(np.nan))
                #pdb.set_trace()
            
    def populate(self, zipsourcefile = "uspatentcitation.tsv.zip", sourcefile="data/20180528/bulk-downloads/uspatentcitation.tsv"):
        """Method to populate the variables. Will open zipped sourcefile and parse every line. Will interrupt
           if some memory limit is exceeded.
            Optional arguments:
                zipsourcefile - type:string - path to zip file holding the source
                sourcefile - type:string - path to sourcefile in the zip file.
            Returns:
                None."""
        with zipfile.ZipFile(zipsourcefile) as zfile:
            with zfile.open(sourcefile, "r") as rfile:
                for i, line in enumerate(rfile):
                    if i>0:
                        self.parse_citation_file_line(line)
                    if (i)%10000 == 0:
                        """Print progress."""
                        print("\rParsing line {}".format(i), end="")
                    if (i)%100000 == 0:
                        """Print memory usage statistics."""
                        process = psutil.Process(os.getpid())
                        mem_usage = process.memory_info().rss
                        print("\nMemory usage: {}".format(round(mem_usage/1000000000, 3)))
                        
                        """If at any point we exceed some memory limit (32G), save and exit."""
                        if mem_usage > 32000000000:
                            print("Uses too much memory, ...interrupting.")
                            #self.compute_pagerank()
                            self.save()
                            #self.compute_network_pagerank()
                            raise SystemExit
                            pdb.set_trace()
        
    def save(self):
        """Method to save all computed data structures: pageranks, citation matrix, citation statistics.
            No Arguments
            Returns:
                None."""
        if self.buildNetworks:
            if self.voluntaryOnly:
                outputFileName = "citation_network_voluntary.npz"
                outputFileNamePR = "pagerank_voluntary.pkl"
            else:
                outputFileName = "citation_network_general.npz"        
                outputFileNamePR = "pagerank_general.pkl"
            
            """ save pageranks """
            if len(self.pageranks) > 0:
                with open(outputFileNamePR, "wb") as ofile:
                    pickle.dump(self.pageranks, ofile, protocol=pickle.HIGHEST_PROTOCOL)

            """ save network as sparse matrix
                Syntax for saving and loading sparse matrices is:
                    sp.sparse.save_npz("filename.npz", sparse_matrix)
                    reloaded_matrix = sp.sparse.load_npz("filename.npz")"""
            try:
                print("Transforming matrix")
                save_mtx = self.DGA.tocsr()
                print("Matrix transformed. Saving...")
                sp.sparse.save_npz(outputFileName, save_mtx)
                print("Matrix saved.")
            except:
                print("Cannot save matrix for whatever reason")
                pass
            
        """ save also the citation statistics    """
        if self.buildCitationCurve:
            if self.voluntaryOnly:
                citationCurveFileName = "citation_curves_voluntary.pkl"
                citationListFileName = "received_citation_list_voluntary.pkl"
                citationCountFileName = "received_citation_count_voluntary.pkl"
            else:
                citationCurveFileName = "citation_curves.pkl"
                citationListFileName = "received_citation_list.pkl"
                citationCountFileName = "received_citation_count.pkl"
            if self.citation_curves:
                with open(citationCurveFileName, "wb") as ofile:
                    pickle.dump(self.citation_curves, ofile, protocol=pickle.HIGHEST_PROTOCOL)
            if len(self.received_citation_list) > 0:
                with open(citationListFileName, "wb") as ofile:
                    pickle.dump(self.received_citation_list, ofile, protocol=pickle.HIGHEST_PROTOCOL)
            if len(self.received_citation_count) > 0:
                with open(citationCountFileName, "wb") as ofile:
                    pickle.dump(self.received_citation_count, ofile, protocol=pickle.HIGHEST_PROTOCOL)
        
    def compute_network_pagerank(self, validate=False):
        """Method to compute network pagerank. Requires citation matrix to be populated.
            Arguments:
                validate - bool - should this pagerank computation method be validated by comparison to the one in networkx
            Returns:
                None."""
        """Compute and save pagerank"""
        self.pageranks = comp_PageRank(self.DGA)
        
        """ validation with networkx """
        if validate:
            print("Valitation of pagerank computation requested. This is not recommended, will take a very long time, and comsume large amounts of memory.")
            net = nx.from_scipy_sparse_matrix(self.DGA, create_using=nx.DiGraph())
            pr = nx.pagerank(net)           #default alpha=.85
            try:
                assert self.pageranks == pr, "Pageranks not identical"
            except:
                pass
            try:
                diffs = np.asarray(list(pr.values()))-np.asarray(self.pageranks)
                assert (abs(diffs) < 10**-4).all(), "Pageranks not even close"
            except:
                print(diffs)
            
def comp_PageRank(DG, d=0.85, precision_limit = 10**-8):
    """ Function to compute PageRank from scipy sparse matrix. Following 
           - https://en.wikipedia.org/wiki/PageRank
           - http://blog.samuelmh.com/2015/02/pagerank-sparse-matrices-python-ipython.html
           - https://networkx.github.io/documentation/latest/_modules/networkx/algorithms/link_analysis/pagerank_alg.html#pagerank
        Parameters:
            DG - adjacency matrix, assumed to be sp.sparse, 2d and square. 
                 Note that links in this matrix are assumed to be the right way around: DG[i,j] records whether a link i->j exists,
                 not the other way around (j->i).
            d - PageRank dampening parameter
            precision_limit - pagerank precision limit
        Returns: 
            pagerank values as numpy ndarray
        Algorithm is 
            Iterate:
                 pr(t+1) = d*M*pr(t) + renormalization 
            until pr(t+1) - pr(t) converges,
            where M is the transposed adjacency patrix with columns normalized to sum to 1.
            Initialization:
                 pr(0) = vector of size mrank with all elements 1./mrank
    """
    
    """ Check that matrix is scipy.sparse object, is 2d and is square """
    assert sp.sparse.issparse(DG)
    assert DG.ndim == 2
    mrank, mrank2 = DG.shape
    assert mrank == mrank2
    
    """ Compute matrix M (overwriting DG to save memory)"""
    L_recip = 1/DG.sum(axis=1).A.ravel()
    L_recip[~np.isfinite(L_recip)] = 0
    L_recip_matrix = sp.sparse.diags(L_recip)
    DG = DG.T
    DG = DG.dot(L_recip_matrix)
    
    """ Initialize pagerank vector """
    pr_old = np.ones(mrank)
    pr = np.ones(mrank) * 1./mrank
    
    """ Iterative computation"""
    iterations = 0
    while (abs(pr_old-pr) >= precision_limit).any():
        iterations += 1
        print("PageRank computation. Iteration {0:4d}".format(iterations))
        pr_old = pr
        pr = d*DG.dot(pr_old) #+ np.ones(mrank)*((1-d)/mrank)   # additive term useless since we have to renormalize in the next line (since some colum sums will be zero for sparse matrices)
        pr += (1-pr.sum()) / mrank
    
    return pr
    
"""main entry point"""

if __name__ == "__main__":
    
    """Set arguments"""
    buildNetworks = False 
    voluntaryOnly = False
    buildCitationCurve = False
    if args.networks:
        buildNetworks = True, 
    if args.voluntaryonly:
        voluntaryOnly = True
    if args.statistics:
        buildCitationCurve = True
    
    """Create CitationSpace instance"""
    CS = CitationSpace(buildNetworks=buildNetworks, voluntaryOnly=voluntaryOnly, buildCitationCurve=buildCitationCurve)
    
    """Populate CitationSpace"""
    CS.populate()
    print("\nFinished.")

    """Save CitationSpace"""    
    CS.save()
    print("Saved. Now computing pagerank.")
    
    if args.networks:
        """Compute pageranks and save again."""
        CS.compute_network_pagerank()
        CS.save()
    #pdb.set_trace()
