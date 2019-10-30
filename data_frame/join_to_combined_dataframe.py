#join df
import pandas as pd
import pickle
import pdb

def join_all_dfs(filenames, outputfilepickle, outputfilefeather, patent_codes_files):
    colnames = {"detected_green_patents.pkl": "Shapira et al. GI pattern",
                #"patent_greenness_merged.pkl": ["Envtech", "IPCGI", "Y_Codes"],      #have already correct filenames
                }
    
    dfs = [pd.read_pickle(fn) for fn in filenames]
    #pddf = pd.concat(dfs, axis=1, sort=True)
    
    pddf = pd.DataFrame()
    for i, df in enumerate(dfs):
        print("parsing {0} of {1}: {2}".format(i+1, len(dfs), filenames[i]))
        merge_direction = 'left' if i>0 else 'right'
        if filenames[i] in ["patent_greenness_merged.pkl", "patent_greenness_based_on_CPC_all.pkl", "patent_greenness_based_on_CPC_Y_classes_USPTO.pkl"]:     # in this file the indices (patent numbers) have for some reason a leading space character
                df.index = df.index.str.strip() 
        if filenames[i] in ["detected_green_patents.pkl"]:
            colname = colnames["detected_green_patents.pkl"]
            df = pd_from_gi_table(df, colname)
        elif colnames.get(filenames[i]):
            df.columns = colnames[filenames[i]]
        
        try:
            assert df.index.is_unique
        except:
            print("df index not unique")
            pdb.set_trace()
        
        try:
            pddf = pd.merge(pddf, df, left_index=True, right_index=True, how=merge_direction)
        except:
            print("couldn't merge")
            pdb.set_trace()
    
    print(pddf.info())  # memory usage info
    
    """ free some memory """
    del dfs
    del df
    
    for classification_scheme in ["IPC", "CPC"]:
        if patent_codes_files.get(classification_scheme) is not None:
            
            """reindex to match CPC/IPC matrix"""
            with open(patent_codes_files.get(classification_scheme), "rb") as infile:
                pcs = pickle.load(infile)
            additionals = list(set(pddf.index) - set(pcs))
            pcs += additionals
            pddf2 = pddf.reindex(pcs)
            
            """save combined dataframe"""
            #pddf.sort_index(inplace=True)          # No sorting. We want the index in the same order as the CPC/IPC matrix
            pddf2.to_pickle(classification_scheme + "_sorted_" + outputfilepickle)
            pddf2.to_pickle(classification_scheme + "_sorted_" + outputfilepickle[:-4] + "_pickleProtocol2.pkl", protocol=2)
            pddf2.rename_axis("Patent ID", inplace=True)
            pddf2.reset_index(inplace=True)
            pddf2.to_feather(classification_scheme + "_sorted_" + outputfilefeather)

def pd_from_gi_table(df, framename):
    idx = df.index
    oldlen= -1
    newlen = len(idx)
    while oldlen != newlen:
        oldlen = newlen
        idx = [di[1:] if di[0]=="0" else di for di in idx]
        newlen = len(idx)
    new_df = pd.DataFrame(index=idx)
    new_df[framename] = True
    new_df = new_df[~new_df.index.duplicated(keep='first')]
    return new_df

    
filenames = ["patents_dates_years.pkl",                 # Application and grant dates (2 x pd.datetime, 2 x int)
             "patents_value_kogan.pkl",                 # Kogan et al. value (1 x float)
             "patents_citation_df.pkl",                 # Pageranks and citation counts
             "patents_lag_citation_counts_df.pkl",      # Lag citation counts 5y, 10y, 20y, 30y, (4x float)
             "patents_table.pkl",                       # Geographic, assignee, etc data
             "detected_green_patents.pkl",              # Green patents detection following Shapira
             #"patent_greenness_based_on_CPC.pkl",       # Green inventory membership (2 x bool)
             #"patent_greenness_based_on_IPC.pkl",       # Green inventory membership (2 x bool)
             #"patent_greenness_based_on_CPC_Y_classes_patstat.pkl",         # Green inventory membership (bool)
             #"patent_greenness_based_on_CPC_Y_classes_USPTO.pkl"            # Green inventory membership (bool)
             "patent_greenness_merged.pkl"              # Green inventory, Envtech, Y Codes membership (3 x bool)
            ]

outputFileName = "green_patents_combined_df.pkl"
outputFileFeatherName = "green_patents_combined_df.feather"
patent_codes_files = {"CPC": "patent_codes.pkl"}
join_all_dfs(filenames, outputFileName, outputFileFeatherName, patent_codes_files)
