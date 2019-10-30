#from matplotlib import pyplot as plt
#from matplotlib_venn import venn3
import pickle
import pandas as pd
import numpy as np
import scipy.sparse
import pdb

def find_incidence(pddf, scheme, level = "section"):
    classification_matrix = (scipy.sparse.load_npz("patent_classification_matrix_level_" + level + ".npz")).tocsr()    # matrix
    with open("patent_classification_codes_level_" + level + ".pkl", "rb") as infile:
        classification_codes = pickle.load(infile)
    #patentID_save_name = "patent_codes.pkl"
    #with open(patentID_save_name, "rb") as rfile:
    #    patlist = pickle.load(rfile)
    selected = np.asarray(pddf[scheme]==True)
    len_diff = classification_matrix.shape[0] - len(selected)
    assert len_diff <= 0
    #selected = np.concatenate((selected, np.zeros(len_diff, dtype=bool)))
    selected = selected[:classification_matrix.shape[0]]
    selected_matrix = classification_matrix[selected,:]
    incidence = selected_matrix.sum(axis=0)
    return classification_codes, np.array(incidence)[0]
    #for cl_idx, cl in enumerate(classification_codes):
    #    patent_indices = scipy.sparse.find(classification_matrix[:, cl_idx])[0]
        
def combine_incidences(level=None):
    if level is None:
        level = "section"
    pddf = pd.read_pickle("CPC_sorted_green_patents_combined_df.pkl")    # dataframe
    _, i_env = find_incidence(pddf, "envtech", level=level)        
    _, i_gi = find_incidence(pddf, "IPCGI", level=level)        
    codes, i_yc = find_incidence(pddf, "Y_Codes", level=level)        
    df = pd.DataFrame({"envtech": i_env, "IPCGI": i_gi, "Y_Codes": i_yc}, index=codes)
    df["sort"] = df["envtech"]*df["IPCGI"]*df["Y_Codes"]
    df = df.sort_values("sort", ascending=0)
    del df["sort"]
    df.to_pickle("greenness_code_incidences" + level + ".pkl")
    print(df.head(10))
    print(df.sort_values("envtech", ascending=0).head(10))
    print(df.sort_values("IPCGI", ascending=0).head(10))
    print(df.sort_values("Y_Codes", ascending=0).head(10))
    #pdb.set_trace()

def return_by_years(level, section_code, )
    pddf = pd.read_pickle("CPC_sorted_green_patents_combined_df.pkl")    # dataframe
    classification_matrix = (scipy.sparse.load_npz("patent_classification_matrix_level_" + level + ".npz")).tocsr()    # matrix
    with open("patent_classification_codes_level_" + level + ".pkl", "rb") as infile:
        classification_codes = pickle.load(infile)
    # id in classification codes, get index
    # get patents
    # count in pddf by year

if __name__ == "__main__":
    #combine_incidences("section")
    combine_incidences("subgroup")
