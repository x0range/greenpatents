import scipy.sparse
import numpy as np
import pickle
import pandas as pd
#import pdb

pddf = pd.read_pickle("../joining/patents_citation_df.pkl")
mtx = scipy.sparse.load_npz("../citation_curves/citation_curves.npz")
with open("../citation_curves/citation_curves_total_lengths.pkl", "rb") as ifile:
	tlens = pickle.load(ifile)
with open("../citation_curves/citation_curves_keys.pkl", "rb") as ifile:
	ckeys = pickle.load(ifile)

rs = {"Patent_ID": ckeys}
new_colnames = []
for lag_years in [5, 10, 20, 30]:
    lag_days = lag_years * 365.25
    alive = np.argmax(tlens > lag_days)
    part_1 = np.empty(alive) 
    part_1[:] = np.nan 
    part_2 = np.sum(mtx[alive:,:np.int64(np.round(lag_days))], axis=1)
    new_colname = "{0:s}_year_lag_citations".format(str(lag_years))
    new_colnames.append(new_colname)
    rs[new_colname] = np.hstack((part_1, np.asarray(part_2.transpose())[0]))

df = pd.DataFrame(rs)
df.set_index("Patent_ID", inplace=True)

#pdb.set_trace()
df = pd.merge(df, pddf, left_index=True, right_index=True, how="outer")
df.loc[df["Received citations (all)"]==0, new_colnames] = 0
df = df.drop(pddf.columns, axis = 1) 

df.to_pickle("patents_lag_citation_counts_df.pkl")
