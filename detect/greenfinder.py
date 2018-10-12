import pickle
import pandas as pd
import numpy as np
import os
import glob
from inspect import getmembers, isfunction
import greenfinder_patterns

def open_file(tfile):
    """Function to read title and abstract pickle files
        Arguments:
            tfile - title file filename
        Returnd:
            keys - list of patent IDs
            titles - dict of titles
            abstracts - dict of abstracts"""
    """obtain corresponding abstract file title"""
    afile = tfile.replace("titles_", "abstracts_")
    assert os.path.exists(afile)
    """read both files"""
    with open(tfile, "rb") as f:
        titles = pickle.load(f)
    with open(afile, "rb") as f:
        abstracts = pickle.load(f)
    """obtain keys (patent IDs)"""
    keys = list(titles.keys())
    """ascertain that key list is consistent, deal with differences"""
    try:
        assert keys == list(abstracts.keys())
    except:
        diff = set(list(abstracts.keys())) - set(keys)
        for key in diff:
            if abstracts[key] is not None:
                titles[key] = None
        diff = set(keys) - set(list(abstracts.keys()))
        for key in diff:
            if titles[key] is not None:
                abstracts[key] = None
            else:
                """remove key in case of None title and no recorded abstract"""
                keys.remove(key)
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
        

def parse_single(tfile, patterns, df):
    """Function to parse a single file, find patterns in all contained patents (abstracts and titles)
        Arguments: 
            tfile: title file filename
            patterns: list of pattern search function
            df: dataframe to save the found patterns
        Returns: dataframe of found patterns"""
    keys, titles, abstracts = open_file(tfile)
    for key in keys:
        title = titles[key]
        abstract = abstracts[key]   
        detected = find_patterns(title, abstract, patterns)
        if sum(detected) > 0:
            df.loc[key] = detected
        return df

def main():
    """Main function; searches in all files for all patterns, saves as pickle"""

    # collect search patterns
    patterns = [f[1] for f in getmembers(greenfinder_patterns) if isfunction(f[1])]
    pattern_names = [f[0] for f in getmembers(greenfinder_patterns) if isfunction(f[1])]
    
    # prepare output dataframe
    df = pd.DataFrame(columns = pattern_names)
    
    # collect files
    files = glob.glob("titles_*.pkl")
    for i, fi in enumerate(files):
        df_part = parse_single(fi, patterns, pd.DataFrame(columns = pattern_names))
        df = df.append(df_part)
        with open("detected_green_patents.pkl", "wb") as ofile:
            pd.to_pickle(df, ofile)
        if i//100 == i/100:
            print(df)
        
# main entry point
if __name__ == "__main__":
    main()
