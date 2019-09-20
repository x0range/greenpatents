import numpy as np
import pandas as pd
import scipy.sparse
import pickle
import pdb


def obtain_Y02_greenness(df_save_filename, patlist_filename, classificationmatrix_filename, classlist_filename=None):
    """Function to check for Y02 codes and save dataframe identifying green patents based on Y codes
        Arguments:
            df_save_filename (str)  - Filename under which to save the Y codes dataframe
            patlist_filename (str)  - Name of the file to read patent IDs from
            classificationmatrix_filename (str) - Name of the file to read classification matrix from
            classlist_filename (str or None)    - Name of file to read classification codes from
        Returns None"""
    
    """Read classification matrix"""
    print("Reloading node keys")
    with open(patlist_filename, "rb") as rfile:
        patlist = pickle.load(rfile)
    if len(patlist) == 3 and len(patlist[0]) > 1000000:
        """This is in case of USPTO.gov based classification scheme"""
        classlist_coarse = patlist[2]       # order in patlist is: patlist, classlist, classlist_coarse
        patlist = patlist[0]
    elif len(patlist) > 1000000:
        """This is in case of patentsview.org based classification scheme"""
        assert classlist_filename is not None, "File name to read classification codes list from required"
        #classlist_coarse = {level: "patent_classification_codes_level_" + str(level) + ".pkl" \
        with open(classlist_filename, "rb") as rfile:
            classlist_coarse = pickle.load(rfile)
    assert len(patlist) > 1000000, "Patent ID list file {} not found".format(patlist_filename)
    #with open("../CPC/patent_codes.pkl", "rb") as rfile:
    #    patlist = pickle.load(rfile)
    #with open("../CPCs/patent_classification_matrix_node_keys.pkl", "rb") as rfile:
    #    patlist, classlist, classlist_coarse = pickle.load(rfile)
    """This is the one handled and saved in parse_CPC_USPTO_gov_based.py as classificationmatrix_coarse."""
    #classificationmatrix = (scipy.sparse.load_npz("../CPCs/patent_classification_matrix_all.npz")).todok()     
    classificationmatrix = (scipy.sparse.load_npz(classificationmatrix_filename)).todok()     
    
    y02codes = [cc for cc in classlist_coarse if cc[0:3] == "Y02"]
    y02code_idxs = [i for i, cc in enumerate(classlist_coarse) if cc[0:3]=="Y02"]
    
    if len(y02code_idxs) > 0:
        """sum over these columns"""
        b = np.zeros((1, classificationmatrix.shape[1]), 'int8')
        b[:, y02code_idxs] = 1
        y02codes_green = (classificationmatrix * np.transpose(b)).flatten()
    else:
        y02codes_green = np.zeros(len(patlist), 'int8')
            
    y02codes_green = (y02codes_green > 0)
    
    """Compile df"""
    dfdict = {'PatID': patlist, 'Y_Codes': y02codes_green}
    pddf = pd.DataFrame(dfdict).set_index('PatID')
    
    pdb.set_trace()
    """save"""
    #pddf.to_pickle("patent_greenness_based_on_CPC_Y_classes_USPTO.pkl")
    pddf.to_pickle(df_save_filename)
        
        
if __name__ == "__main__":
    obtain_Y02_greenness(df_save_filename = "patent_greenness_based_on_CPC_Y_classes_USPTO.pkl",
                         patlist_filename = "../CPCs/patent_classification_matrix_node_keys.pkl",
                         classificationmatrix_filename = "../CPCs/patent_classification_matrix_all.npz",
                         classlist_filename = None)
    obtain_Y02_greenness(df_save_filename = "patent_greenness_based_on_CPC_Y_classes_patstat.pkl",
                         patlist_filename = "../CPC/patent_codes.pkl",
                         classificationmatrix_filename = "../CPC/patent_classification_matrix_level_subsection.npz",
                         classlist_filename = "../CPC/patent_classification_codes_level_subsection.pkl")                         
