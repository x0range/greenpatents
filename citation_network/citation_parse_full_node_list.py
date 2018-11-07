"""Script to parse the citation network from USPTO
        Website: http://www.patentsview.org/download/
        Data: http://s3.amazonaws.com/data-patentsview-org/20180528/download/uspatentcitation.tsv.zip
        Code book: http://www.patentsview.org/data/Patents_DB_dictionary_bulk_downloads.xlsx
   Script will prepare and save the list of nodes for citation_parse.py. This is done separately for efficiency. So 
        citation_parse_full_node_list.py (this script) must be executed first."""

import os
import psutil
import pdb
import pickle
import zipfile
import argparse

"""Argument handling"""
parser = argparse.ArgumentParser(description='Script to scrape the full node list out of the OSPTO citations file')
parser.add_argument("--voluntaryonly", action="store_true", help="citation network to include only citations created by the applicant, not the examiner, not other, not unknown.")
args = parser.parse_args()

"""Reduced citation space class"""
class ReducedCitationSpace():
    def __init__(self, voluntaryOnly=False):
        """Constructor method. Prepares variables.
            Arguments:
                voluntaryOnly   - bool - should only citations put by the applicant be considered or all citations, 
            Returns:
                Instance of object."""
        self.voluntaryOnly = voluntaryOnly
        self.DGindex = 0 
        self.DGnodes = {}
        
    def record_node(self, label):
        """Method to add a node.
            Arguments:
                label - type:string - label of the node; should be the patentID.
            Returns
                int - index of the created node in the list"""
        self.DGnodes[label] = self.DGindex
        self.DGindex += 1
        return self.DGindex - 1

    def parse_citation_file_line(self, line):
        """Method to parse a single citation as recorded in the USPTO source file
            Arguments:
                line - type: bytes - the line to be parsed
            Returns:
                None."""
        elementi = line.decode("UTF-8").split("\t")
        assert len(elementi) == 9
        origin, destination, date, cited_by, country = elementi[1], elementi[2], elementi[3], elementi[7], elementi[6]
        if country != "US":
            print("weird country detected")
            pdb.set_trace()
        cited_by = cited_by.replace("cited by ", "")
        if (not self.voluntaryOnly) or cited_by == "applicant":
            origin_idx, destination_idx = self.DGnodes.get(origin), self.DGnodes.get(destination)
            if origin_idx is None:
                origin_idx = self.record_node(origin)
            if destination_idx is None:
                destination_idx = self.record_node(destination)
            
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
                        print("\rParsing line {}".format(i), end="")
                    if (i)%100000 == 0:
                        process = psutil.Process(os.getpid())
                        mem_usage = process.memory_info().rss
                        print("\nMemory usage: {}".format(round(mem_usage/1000000000, 3)))
                        if mem_usage > 8000000000:
                            print("Uses too much memory, ...interrupting.")
                            #self.compute_pagerank()
                            self.save()
                            #self.compute_network_pagerank()
                            raise SystemExit
                            #pdb.set_trace()

    def save(self):
        """Method to save the created full node list.
            No Arguments
            Returns:
                None."""
        if self.voluntaryOnly:
            fullnodelistPath = "full_node_list_voluntary.pkl"
        else:
            fullnodelistPath = "full_node_list.pkl"
        with open(fullnodelistPath, "wb") as ofile:
            pickle.dump(self.DGnodes, ofile, protocol=pickle.HIGHEST_PROTOCOL)


"""Main entry point"""

if __name__ == "__main__":
    """Set arguments"""
    voluntaryOnly = False
    if args.voluntaryonly:
        voluntaryOnly=True
        
    """Create object instance"""
    CS = ReducedCitationSpace(voluntaryOnly=voluntaryOnly)

    """Populate CitationSpace"""
    CS.populate()
    print("\nFinished.")

    """Save CitationSpace"""    
    CS.save()
    #pdb.set_trace()
