#join df
import pandas as pd
import pdb

def join_all_dfs(filenames, outputfilepickle, outputfilefeather):
    colnames = {"detected_green_patents.pkl": "Shapira et al. GI pattern"}
    
    dfs = [pd.read_pickle(fn) for fn in filenames]
    #pddf = pd.concat(dfs, axis=1, sort=True)
    
    pddf = pd.DataFrame()
    for i, df in enumerate(dfs):
        print("parsing {0} of {1}".format(i+1, len(dfs)))
        merge_direction = 'left' if i>0 else 'right'
        if filenames[i] == "patent_greenness_based_on_CPC_all.pkl":     # in this file the indices (patent numbers) have for some reason a leading space character
                df.index = df.index.str.strip() 
        if filenames[i] in ["detected_green_patents.pkl"]:
            colname = colnames["detected_green_patents.pkl"]
            df = pd_from_gi_table(df, colname)
        
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
    
    """save combined dataframe"""
    pddf.sort_index(inplace=True)
    pddf.to_pickle(outputfilepickle)
    pddf.rename_axis("Patent ID",inplace=True)
    pddf.reset_index(inplace=True)
    pddf.to_feather(outputfilefeather)

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
             "patents_table.pkl",                       # Geographic, assignee, etc data
             "detected_green_patents.pkl",              # Green patents detection following Shapira
             "patent_greenness_based_on_CPC_all.pkl"    # Green inventory membership (2 x bool)
            ]

outputFileName = "green_patents_combined_df.pkl"
outputFileFeatherName = "green_patents_combined_df.feather"
join_all_dfs(filenames, outputFileName, outputFileFeatherName)

