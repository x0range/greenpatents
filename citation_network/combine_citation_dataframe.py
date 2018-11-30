import pandas as pd
import pdb

def parse_citation_type_frame(cdf, nodeDictFileName, arrayFileNames, colnames):
    node_dict = pd.read_pickle(nodeDictFileName)
    next_df = pd.DataFrame.from_dict(node_dict, orient='index')
    next_df['counter'] = range(len(next_df))
    assert all(next_df['counter'] == next_df[0])
    next_df.drop(next_df.columns, inplace=True, axis=1)
    pagerank_colname, citationcount_colname = colnames
    pagerank_array = pd.read_pickle(arrayFileNames[0])
    citationcount_dict = pd.read_pickle(arrayFileNames[1])
    citationcount_df = pd.DataFrame.from_dict(citationcount_dict, orient='index')
    citationcount_df.columns = [citationcount_colname]
    #pdb.set_trace()
    next_df[pagerank_colname] = pagerank_array
    cdf = pd.concat([cdf, next_df, citationcount_df], axis=1, sort=True)
    print(cdf.head())
    return cdf

def combine_all_citation_frames():
    pddf = pd.DataFrame()
    
    nextarrayfiles = ["pagerank_general.pkl", "received_citation_count.pkl"]
    nextcolnames = ['Pagerank (all)', 'Received citations (all)']
    nodeDictFile = "full_node_list.pkl"
    pddf = parse_citation_type_frame(pddf, nodeDictFile, nextarrayfiles, nextcolnames)

    nextarrayfiles = ["pagerank_voluntary.pkl", "received_citation_count_voluntary.pkl"]
    nextcolnames = ['Pagerank (assignee citations only)', 'Received citations (assignee citations only)']
    nodeDictFile = "full_node_list_voluntary.pkl"
    pddf = parse_citation_type_frame(pddf, nodeDictFile, nextarrayfiles, nextcolnames)

    pdb.set_trace()
    #pddf.index = pddf.index.str.strip()
    pddf.to_pickle("patents_citation_df.pkl")
    
if __name__ == '__main__':
    combine_all_citation_frames()
