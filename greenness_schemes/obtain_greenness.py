import numpy as np
import pandas as pd
import scipy.sparse
import pickle
import pdb
"""Class definitions"""
"""Green patents search pattern class. Can parse and apply OECD ENvtech and CPC green inventory 
   patterns"""
class GreenInventory:
    def __init__(self, patternsfile):
        """Constructor. Recods patternfile and calls method to read pattern
            Arguments:
                patternfile - string - path to pattern file
            Returns: Class instance"""
        self.name = patternsfile
        self.read_search_patterns(patternsfile)
        self.strip_space_from_search_patterns()
        
    def strip_space_from_search_patterns(self):
        """Method to strip space from between group ID and subgroup ID as CPC does not use that.
            Arguments: None
            Returns: None."""
        for i, pattern in enumerate(self.single_patterns):
            self.single_patterns[i] = pattern.replace(" ", "")
        
    def read_search_patterns(self, patternsfile):
        """Method to read search patterns from file
            Arguments:
                patternfile - string - path to pattern file
            Returns: None"""
            
        """Prepare record variables"""
        self.single_patterns = []
        self.combined_patterns = []
        
        """Parse file"""
        for line in line_generator_from_file(patternsfile):
            if line[0]=="[":                        #find conditional patterns
                elements = line[1:].split("]")[0].split(" and ")
                self.combined_patterns.append(elements)
            elif "-" in line:                       #find wildcard patterns
                """Identify start and endpoint of range"""
                line, endnum = line.split("-")
                if "/" in line:
                    startnum_idx = len(line) - line[::-1].index("/")
                else:
                    startnum_idx = len(line) - line[::-1].index(" ")
                line, startnum = line[:startnum_idx], line[startnum_idx:]
                """Build numeric range and corresponding classification codes"""
                allnum = list(range(int(startnum), int(endnum)+1))
                allendings = [str(x) for x in allnum]
                """Record patterns"""
                for ending in allendings:
                    while len(ending) < len(startnum):
                        ending = "0" + ending
                    self.single_patterns.append(line + ending)
            else:                                   #find simple patterns
                self.single_patterns.append(line)
    
    def filter_matching(self, class_strings):
        """Method to filter all strings in a list that are matched by the green inventory.
            Arguments:
                class_strings - list of strings - classification codes
            Returns: list of int - indices of matched strings"""
        filtered = []
        for i, cs in enumerate(class_strings):
            if any(st in cs for st in self.single_patterns):
                filtered.append(i)
            #    if "H01" in cs:
            #        print(cs)
            #else:
            #    if "H01" in cs:
            #        print(cs, " NOT PRESENT")
        return np.array(filtered)

"""Green patents record class. Can parse classification files, apply search patterns and save records"""
class ClassificationAndGreennessRecord():
    def __init__(self, levels_list=None, setup=False, scheme="CPC"):
        """Constructor method.
           Assumes that the classification files from USPTO cpc_current.tsv.zip is unpacked
            in the current working directory, i.e. the individual file is "./cpc_current.tsv"
            Arguments: 
                setup      - bool - Should matrices etc be newly set up (empty)?
            Returns class instance."""
        
        """Prepare variables"""
        self.scheme = scheme
        scheme_prefix = "../" + scheme + "/"
        if levels_list is None:
            #self.levels_list = ['section', 'subsection', 'group', 'subgroup']
            self.levels_list = ['subgroup']
        else:
            self.levels_list = levels_list
        matrix_save_names = {level: scheme_prefix + "patent_classification_matrix_level_" + str(level) + ".npz" \
                                                                                for level in self.levels_list}
        classlist_save_names = {level: scheme_prefix + "patent_classification_codes_level_" + str(level) + ".pkl" \
                                                                                for level in self.levels_list}
        patentID_save_name = scheme_prefix + "patent_codes.pkl"
        print("Reloading node keys")
        with open(patentID_save_name, "rb") as rfile:
            self.patlist = pickle.load(rfile)
        self.classlist = {}
        self.classificationmatrix = {}
        for level in self.levels_list:
            with open(classlist_save_names[level], "rb") as rfile:
                self.classlist[level] = pickle.load(rfile)
        for level in self.levels_list:
            print("Reloading matrix...")
            reloaded_matrix = scipy.sparse.load_npz(matrix_save_names[level])
            print("Transforming matrix")
            self.classificationmatrix[level] = reloaded_matrix.todok()

        """Prepare search patterns"""
        print("Preparing search patterns")
        self.GIenvtech = GreenInventory("envtech_" + scheme + ".txt")
        self.IPCGI= GreenInventory("green_inventory.txt")


    def check_IPCGI(self):
        """Method to find green patents based in the subgroup level classification matrix. Records this in pandas df.
            Arguments None
            Returns: df"""
        """Obtain 3 lists of Envtech matrix columns"""
        
        """Obtain 1 list of IPCGI matrix columns"""
        col_array_IPCGI = self.IPCGI.filter_matching(self.classlist['subgroup'])
        green_IPCGI = self.classification_matrix_sum_by_indices(col_array_IPCGI, level='subgroup')
        green_IPCGI = (green_IPCGI>0)
        assert len(green_IPCGI) == len(self.patlist)

        """merge df"""
        df = pd.DataFrame({"pat_ID": self.patlist, "IPCGI": green_IPCGI})
        df.set_index("pat_ID", inplace=True)
        del df.index.name
        return df
        
        #"""Enter results in self.pddf data frame"""
        #for pat_idx, patID in enumerate(self.patlist):
        #    if start <= pat_idx < stop:
        #        print("\rCheck greenness {0:10d}".format(pat_idx), end="")
        #        self.pddf.loc[patID] = [green_Envtech[pat_idx], green_IPCGI[pat_idx]]
        #print("")
        
    def check_Envtech(self):
        """Method to find green patents based in the subgroup level classification matrix. Records this in pandas df.
            Arguments None
            Returns: df"""
        """Obtain 3 lists of Envtech matrix columns"""
        """Single code"""
        col_array_Envtech_single = self.GIenvtech.filter_matching(self.classlist['subgroup'])
        green_Envtech_single = self.classification_matrix_sum_by_indices(col_array_Envtech_single, level='subgroup')
        
        """Combined codes E03 and ..."""
        pseudoGIenvtech = GreenInventory("pseudo_envtech_conditional_complement_E03.txt")
        pseudoGIenvtech_E03 = GreenInventory("pseudo_envtech_conditional_E03.txt")

        col_array_Envtech_E03_complement = pseudoGIenvtech.filter_matching(self.classlist['subgroup'])
        col_array_Envtech_E03 = pseudoGIenvtech_E03.filter_matching(self.classlist['subgroup'])
        green_Envtech_E03_complement = self.classification_matrix_sum_by_indices(col_array_Envtech_E03_complement, \
                                                                                                level='subgroup')
        green_Envtech_E03 = self.classification_matrix_sum_by_indices(col_array_Envtech_E03, level='subgroup')
    
        """Perform computation to combine the 3 lists"""
        green_Envtech = green_Envtech_E03 * green_Envtech_E03_complement + green_Envtech_single
        
        """Apply Y codes (except Y02A and Y02D) as well in CPC"""
        if self.scheme == "CPC":
            y02code_idxs = [i for i, cc in enumerate(self.classlist["subgroup"]) if cc[0:4] in ["Y02B", "Y02C", "Y02E", "Y02P", "Y02T", "Y02W"]]
            y_codes_green = self.classification_matrix_sum_by_indices(y02code_idxs, level='subgroup')              
            y_codes_green = (y_codes_green > 0)
            green_Envtech = green_Envtech + y_codes_green
        
        green_Envtech = (green_Envtech>0)
        assert len(green_Envtech) == len(self.patlist)
        
        """merge df"""
        df = pd.DataFrame({"pat_ID": self.patlist, "Envtech": green_Envtech})
        df.set_index("pat_ID", inplace=True)
        del df.index.name
        return df
                
        #"""Enter results in self.pddf data frame"""
        #for pat_idx, patID in enumerate(self.patlist):
        #    if start <= pat_idx < stop:
        #        print("\rCheck greenness {0:10d}".format(pat_idx), end="")
        #        self.pddf.loc[patID] = [green_Envtech[pat_idx], green_IPCGI[pat_idx]]
        #print("")
        
    def check_Y_codes(self):
        """Method to find green patents based in the subgroup level classification matrix. Records this in pandas df.
            Arguments None
            Returns: df"""
            
        #y02_codes = [cc for cc in self.classlist[subgroup] if cc[0:3] == "Y02"]
        y02code_idxs = [i for i, cc in enumerate(self.classlist["subgroup"]) if cc[0:3]=="Y02"]
    
        y_codes_green = self.classification_matrix_sum_by_indices(y02code_idxs, level='subgroup')              
        y_codes_green = (y_codes_green > 0)
        assert len(y_codes_green) == len(self.patlist)

        """merge df"""
        df = pd.DataFrame({"pat_ID": self.patlist, "Y_Codes": y_codes_green})
        df.set_index("pat_ID", inplace=True)
        del df.index.name
        return df
                
        #"""Enter results in self.pddf data frame"""
        #for pat_idx, patID in enumerate(self.patlist):
        #    if start <= pat_idx < stop:
        #        print("\rCheck greenness {0:10d}".format(pat_idx), end="")
        #        self.pddf.loc[patID] = [green_Envtech[pat_idx], green_IPCGI[pat_idx]]
        #print("")
        
    def classification_matrix_sum_by_indices(self, col_array, level='subgroup'):
        """Method for summing columns by indices in the classificationmatrices.
            Arguments: 
                col_array - numpy array of int - columns to be summed
                level - string - classification depth level indicator. Will usually be 'subgroup'
            Returns:
                numpy array of int: The sum."""
        if len(col_array) > 0:
            """sum over these columns"""
            b = np.zeros((1, self.classificationmatrix[level].shape[1]), 'int8')
            b[:, col_array] = 1
            return (self.classificationmatrix[level] * np.transpose(b)).flatten()
        else:
            return np.zeros(len(self.patlist), 'int8')

"""Function definitions"""

def line_generator_from_file(filename):
    """Generator function. Opens filename and creates a generator that returns the relevant
       lines one by one (ignoring those starting with "#" and the header, starting with 'uuid\tpatent_id'.
        Arguments:
            filename - string - file name
        Returns generator"""
    with open(filename, "r") as rfile:
        for line in rfile:
            if (not line[0] == "#") and (not line[:14] == 'uuid\tpatent_id'):
                line = line.replace("\n", "")
                yield line


def obtain_Envtech_greenness(df_save_filename, patlist_filename, classificationmatrix_filename, classlist_filename=None):
    """Function to check for Envtech codes and save dataframe identifying green patents based on Y codes
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
    
    envtech = [cc for cc in classlist_coarse if cc[0:3] == "Envtech"]
    y02code_idxs = [i for i, cc in enumerate(classlist_coarse) if cc[0:3]=="Envtech"]
    
    if len(y02code_idxs) > 0:
        """sum over these columns"""
        b = np.zeros((1, classificationmatrix.shape[1]), 'int8')
        b[:, y02code_idxs] = 1
        envtech_green = (classificationmatrix * np.transpose(b)).flatten()
    else:
        envtech_green = np.zeros(len(patlist), 'int8')
            
    envtech_green = (envtech_green > 0)
    
    """Compile df"""
    dfdict = {'PatID': patlist, 'Envtech': envtech_green}
    pddf = pd.DataFrame(dfdict).set_index('PatID')
    
    pdb.set_trace()
    """save"""
    #pddf.to_pickle("patent_greenness_based_on_CPC_Envtech_USPTO.pkl")
    pddf.to_pickle(df_save_filename)
        
        
if __name__ == "__main__":
    """IPC"""
    CR = ClassificationAndGreennessRecord(scheme="IPC")
    """IPCGI"""
    print("Applying IPC GI scheme")
    df_IPCGI = CR.check_IPCGI()
    """Envtech pt 1"""
    print("Applying Envtech scheme in IPC")
    df_Envtech = CR.check_Envtech()
    """CPC"""
    CR = ClassificationAndGreennessRecord(scheme="CPC")
    """Envtech pt 1"""
    print("Applying Envtech scheme in CPC")
    df_Envtech2 = CR.check_Envtech()
    """merge"""
    print("Merging Envtech schemes")
    df_Envtech = pd.merge(df_Envtech, df_Envtech2, left_index=True, right_index=True, how="outer")
    """We need to tie two or operations because if the first argument is NaN, the result is falsely given as False"""
    df_Envtech["Envtech"] = (df_Envtech["Envtech_x"] | df_Envtech["Envtech_y"]) |\
                                         (df_Envtech["Envtech_y"] | df_Envtech["Envtech_x"])
    
    del df_Envtech["Envtech_x"]
    del df_Envtech["Envtech_y"]
    
    """Y Codes"""
    print("Applying CPC Y Codes scheme")
    df_Y_Codes = CR.check_Y_codes()
    
    """merge"""
    print("Merging data frames")
    df = pd.merge(df_Envtech, df_IPCGI, left_index=True, right_index=True, how="outer")
    df = pd.merge(df, df_Y_Codes, left_index=True, right_index=True, how="outer")
    
    """save"""
    print("Saving data")
    df.to_pickle("patent_greenness_merged.pkl")
    
    #obtain_Envtech_greenness(df_save_filename = "patent_greenness_based_on_CPC_Envtech_USPTO.pkl",
    #                     patlist_filename = "../CPCs/patent_classification_matrix_node_keys.pkl",
    #                     classificationmatrix_filename = "../CPCs/patent_classification_matrix_all.npz",
    #                     classlist_filename = None)
    #obtain_Envtech_greenness(df_save_filename = "patent_greenness_based_on_CPC_Envtech_patstat.pkl",
    #                     patlist_filename = "../CPC/patent_codes.pkl",
    #                     classificationmatrix_filename = "../CPC/patent_classification_matrix_level_subsection.npz",
    #                     classlist_filename = "../CPC/patent_classification_codes_level_subsection.pkl")                         
