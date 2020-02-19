import pickle
import pandas as pd
import numpy as np
import os
import glob
import pdb
import gzip
from inspect import getmembers, isfunction
import greenfinder_patterns_2 as greenfinder_patterns


def open_file(tfile, full_text_search=False):
    """Function to read title and abstract pickle files
        Arguments:
            tfile - title file filename
            full_text_search - bool: should it search full patent text, not just title and abstract
        Returns:
            keys - list of patent IDs
            titles - dict of titles
            abstracts - dict of abstracts"""
    """read title file"""
    with gzip.GzipFile(tfile, 'r') as f:
        titles = pickle.load(f)
    """prepare other files"""
    docs = {}
    abstracts = None
    docs_type_list = ["abstracts"]
    if full_text_search:
        docs_type_list = ["abstracts", "descriptions", "claims"]
    
    """obtain keys (patent IDs)"""
    keys = list(titles.keys())
    
    """open corresponding abstract etc files"""
    for doc_name in docs_type_list:
        """ Obtain file name"""
        docfile = tfile.replace("titles", doc_name)
        """ Open"""
        assert os.path.exists(docfile)
        with gzip.GzipFile(docfile, 'r') as f:
            docs[doc_name] = pickle.load(f)
        """ Update keys (patent IDs) list"""
        keys = list(set(keys + list(docs[doc_name].keys())))
    
    """ Make title dict consistent"""    
    for key in keys:
        if (not key in titles) or (titles[key] is None):
            print("None title found")
            titles[key] = ""
        
    """Populate abstract dict"""
    abstracts = {key: "" for key in keys}
    for doc_name in docs_type_list:
        for key in keys:
            if (key in docs[doc_name]) and (docs[doc_name][key] is not None):
                abstracts[key] += " \n" + docs[doc_name][key]

    return keys, titles, abstracts

    
def find_patterns(title, abstract, patterns):
    """Function to find all patterns in one patent.
        Arguments:
            title - patent title
            abstract - patent abstract
            patterns - list of pattern search functions
        Returns:
            res - numpy array of 0 and 1 of the same length as the list of patterns, 
                  each 1 representing a detected pattern"""
    try:
        text = title + " \n" + abstract
    except:
        if abstract is None:
            text = title
        else:
            assert False
    res = np.zeros(len(patterns))
    for i, pattern in enumerate(patterns):
        if pattern(text):
            res[i] = 1
    return res
        

def parse_single(tfile, patterns, df, full_text_search=False):
    """Function to parse a single file, find patterns in all contained patents (abstracts and titles)
        Arguments: 
            tfile: title file filename
            patterns: list of pattern search function
            df: dataframe to save the found patterns
            full_text_search: (bool) should it search full patent text, not just title and abstract
        Returns: dataframe of found patterns"""
    keys, titles, abstracts = open_file(tfile, full_text_search)
    for key in keys:
        title = titles[key]
        abstract = abstracts[key]   
        detected = find_patterns(title, abstract, patterns)
        if sum(detected) > 0:
            df.loc[key] = detected
    
    return df

def main(full_text_search=False):
    """Main function; searches in all files for all patterns, saves as pickle.
        Arguments: 
            full_text_search: (bool) should it search full patent text, not just title and abstract
    """

    # collect search patterns
    patterns = [f[1] for f in getmembers(greenfinder_patterns) if isfunction(f[1])]
    pattern_names = [f[0] for f in getmembers(greenfinder_patterns) if isfunction(f[1])]
    
    # prepare output dataframe
    df = pd.DataFrame(columns = pattern_names)
    
    # collect files
    files = glob.glob("../patent_corpus_new/titles/titles_*.pkl.gz")
    for i, fi in enumerate(files):
        df_part = parse_single(fi, patterns, pd.DataFrame(columns = pattern_names), full_text_search)
        df = df.append(df_part)
        df.to_pickle("detected_green_patents.pkl")
        #if i//100 == i/100:
        print("\rFound {1:5d} so far. Parsing file {2:4d}/{3:d}, file name: {0:s}                                         ".format(fi, len(df), i, len(files)), end="")
        
# main entry point
if __name__ == "__main__":
    main(full_text_search=True)
