import numpy as np
import pandas as pd
import glob
import pdb

def join_pandas(filenames, outputfile, zerofile):
    pddf = pd.read_pickle(zerofile)
    for i, filename in enumerate(filenames):
        print("parsing {0} of {1}".format(i+1, len(filenames)))
        next_df = pd.read_pickle(filename)
        pddf = pddf.append(next_df)
        ndup = len(pddf.index.get_duplicates())
        try:
            assert ndup == 0, "duplicate entries found: {0}".format(ndup)
        except:
            print("duplicate entries found: {0}".format(ndup))
            pdb.set_trace()
            pass
    
    pddf.to_pickle(outputfile)


filenames = glob.glob("patent_greenness_based_on_CPC*[0-9].pkl")
outputFileName = "patent_greenness_based_on_CPC_all.pkl"
zerofile = "patent_greenness_based_on_CPC.pkl"

join_pandas(filenames, outputFileName, zerofile)

