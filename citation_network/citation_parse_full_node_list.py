import networkx as nx
import pandas as pd
import os
import psutil
import pdb
import pickle
import scipy as sp
import zipfile
import argparse

parser = argparse.ArgumentParser(description='Script to scrape the full node list out of the OSPTO citations file')
parser.add_argument("--voluntaryonly", action="store_true", help="citation network to include only citations created by the applicant, not the examiner, not other, not unknown.")
args = parser.parse_args()

class CitationSpace():
    def __init__(self, buildVoluntaryNetwork=False):
        self.buildVoluntaryNetwork = buildVoluntaryNetwork
        self.DGindex = 0 
        self.DGnodes = {}
        
    def record_node(self, label):
        self.DGnodes[label] = self.DGindex
        self.DGindex += 1
        return self.DGindex - 1

    def parse_citation_file_line(self, line):
        elementi = line.decode("UTF-8").split("\t")
        assert len(elementi) == 9
        origin, destination, date, cited_by, country = elementi[1], elementi[2], elementi[3], elementi[7], elementi[6]
        if country != "US":
            print("weird country detected")
            pdb.set_trace()
        cited_by = cited_by.replace("cited by ", "")
        if (not self.buildVoluntaryNetwork) or cited_by == "applicant":
            origin_idx, destination_idx = self.DGnodes.get(origin), self.DGnodes.get(destination)
            if origin_idx is None:
                origin_idx = self.record_node(origin)
            if destination_idx is None:
                destination_idx = self.record_node(destination)
            
    #def parse_citation_file(self):
    def prepare(self, zipsourcefile = "uspatentcitation.tsv.zip", sourcefile="data/20180528/bulk-downloads/uspatentcitation.tsv"):
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
        if self.buildVoluntaryNetwork:
            fullnodelistPath = "full_node_list_voluntary.pkl"
        else:
            fullnodelistPath = "full_node_list.pkl"
        with open(fullnodelistPath, "wb") as ofile:
            pickle.dump(self.DGnodes, ofile, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    buildVoluntaryNetwork = False
    if args.voluntaryonly:
        buildVoluntaryNetwork=True
    CS = CitationSpace(buildVoluntaryNetwork=buildVoluntaryNetwork)
    CS.prepare()
    print("\nFinished.")
    CS.save()
    #pdb.set_trace()
