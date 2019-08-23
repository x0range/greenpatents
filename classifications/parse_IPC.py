"""Script to parse IPC classification codes for all patents starting 1976.
   The script reads the classification code files US_Grant_IPC_MCF_Text_2018-08-01.zip
   from USPTO as well as search pattern files for green technologies:
    - OECD ENVTECH from file envtech_03.txt
    - IPC green inventory from file green_inventory_03.txt
   The script records:
    - a pandas dataframe indicating membership in sets of green patents as pickle file
    - the classification bipartite network (patents vs. unique classification codes considering
        class and subclass only, disregarding group and subgroup) as npz file
    - the detailed classification bipartite network (patents vs. unique classification codes) 
        as npz file.
   The script defines two classes:
    - GreenInventory as search pattern class.
    - GreenRecord as record class

"""

"""inport modules"""
import numpy as np
import scipy
import scipy.sparse
import pickle
import pandas as pd
import glob
import pdb
import sys
import time

"""Class definitions"""
"""Green patents search pattern class. Can parse and apply OECD ENvtech and IPC green inventory 
   patterns"""
class GreenInventory:
    def __init__(self, patternsfile):
        """Constructor. Recods patternfile and calls method to read pattern
            Arguments:
                patternfile - string - path to pattern file
            Returns: Class instance"""
        self.name = patternsfile
        self.read_search_patterns(patternsfile)
        
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
    
    def __match_combined(self, class_strings):
        """Method to check if a list of class strings matches a green technology as defined
           in combined strings that all have to match.
            Arguments:
                class_strings - list of strings - list of classification codes
            Returns: bool - patent is a green technology"""
        
        """For each pattern cp, if every element is found, return True"""
        for cp in self.combined_patterns:
            cp_found = True
            for pattern_element in cp:
                if not any(pattern_element in st for st in class_strings):
                    cp_found = False
            if cp_found:
                return True
        """If none of the patterns matched, return False"""
        return False
            
    def __match_single(self, class_string):
        """Method to check if a class string matches a green technology as defined as single string.
            Arguments:
                class_string - string - classification code
            Returns: bool - patent is a green technology"""
        if any(st in class_string for st in self.single_patterns):
            return True
        else:
            return False

    def __match_any(self, class_strings):
        """Method to check if a list of class strings matches a green technology as defined as single string.
            Arguments:
                class_strings - list of strings - classification codes
            Returns: bool - patent is a green technology"""
        if any(st in cs for st in self.single_patterns for cs in class_strings):
            return True
        else:
            return self.match_combined(class_strings)

    def filter_matching(self, class_strings):
        """Method to filter all strings in a list that are matched by the green inventory.
            Arguments:
                class_strings - list of strings - classification codes
            Returns: list of int - indices of matched strings"""
        filtered = []
        for i, cs in enumerate(class_strings):
            if any(st in cs for st in self.single_patterns):
                filtered.append(i)
            #    print(cs)
            #else:
            #    print(cs, " NOT PRESENT")
        return np.array(filtered)

"""Green patents record class. Can parse classification files, apply search patterns and save records"""
class GreennessRecord():
    def __init__(self):
        """Constructor method.
           Assumes that the classification files from USPTO US_Grant_IPC_MCF_Text_2018-08-01.zip are unpacked
            in the current working directory, i.e. the individual files are "./data/20181127/bulk-downloads/ipcr.tsv"
            Arguments: None
            Returns class instance."""
        
        """Prepare variables"""
        self.levels_list = ['section', 'class', 'subclass', 'maingroup', 'subgroup']
        self.patlist = None
        self.classlist = {}
        self.classificationmatrix = {}
        
        """Identify classification files"""
        self.classfilelist = ['./data/20181127/bulk-downloads/ipcr.tsv']
        """Prepare matrices"""
        print("Preparing matrices")
        self.prepare_lists_and_matrices(self.classfilelist)
            
        """Prepare search patterns"""
        print("Preparing search patterns")
        self.GIenvtech = GreenInventory("envtech_03.txt")
        self.GI_IPC = GreenInventory("green_inventory_03.txt")
        self.pddf = pd.DataFrame(columns=['envtech', 'IPCGI'])  #greenness data frame
        
        
        print("All set up.")
        
    def __finalize_greenness_record(self, patID, is_green_ENVTECH, is_green_IPCGI, class_strings):
        """DELETE THIS
            Method to affect final checks on green pattern matching (with combined patterns of several
           classification strings) and to record the result in data frame.
            Arguments:
                patID - string - patent ID
                is_green_ENVTECH - bool - OECD envtech green patterns found so far
                is_green_IPCGI - bool - IPC green inventory patterns found so far
                class_strings - list of strings - list of classification codes.
            Returns None"""
        
        """Check combined patterns"""
        if len(class_strings) > 1: 
            if not is_green_ENVTECH:
                is_green_ENVTECH = self.GIenvtech.match_combined(class_strings)
            if not is_green_IPCGI:
                is_green_IPCGI = self.GI_IPC.match_combined(class_strings)
        """Record greenness in data frame"""
        self.pddf.loc[patID] = [is_green_ENVTECH, is_green_IPCGI]

    def parse_line(self, line):
        """Method to parse one lingle line from the classification file
            Arguments:
                line - string - The line
            Returns:
                tuple of:
                    patID - string - the patent ID
                    class_code - dict - the class code at different depth levels."""
        class_code_raw = line.split('\t')[1:8]
        class_code_raw = [it.strip("/") for it in class_code_raw]
        #class_code_raw = np.asarray(class_code_raw)
        
        patID = class_code_raw[0]
        
        if len(class_code_raw[3]) == 1:
            class_code_raw[3] = '0' + class_code_raw[3]
        class_code = {}
        class_code['section'] = class_code_raw[2]
        class_code['class'] = class_code['section'] + class_code_raw[3]
        class_code['subclass'] = class_code['class'] + class_code_raw[4]
        class_code['maingroup'] = class_code['subclass'] + ' {0:>3s}'.format(class_code_raw[5])
        class_code['subgroup'] = class_code['maingroup'] + '/' + class_code_raw[6].strip()
        return patID, class_code
    
    def search_IPC_file(self, classificationfile):
        """Method for parsing IPC file. Identifies citations and records matrices
            Arguments:
                classificationfile - string - the classification file to be used
            Returns None."""
        i = 0
        for line in line_generator_from_file(classificationfile):
            i += 1
            print("\rSearch IPC file {0:10d}".format(i), end="")

            """read class codes and patent ID"""
            patID, class_code = self.parse_line(line)
            
            """update matrices"""
            for level in self.levels_list:
                classID = class_code[level]
                pat_idx = self.patlist.index(patID)
                class_idx = int(np.where(self.classlist[level]==classID)[0])
                self.classificationmatrix[level][pat_idx, class_idx] = 1
        print("")
        
    def __check_greenness(self):
        """cycle through patents"""
        for pat_idx, patID in enumerate(self.patlist):
            print("\rCheck greenness {0:10d}".format(pat_idx), end="")
            #print("Check greenness {0:10d}".format(pat_idx))
            #t0 = time.time()
            """identify class strings"""
            class_code_idxs = scipy.sparse.find(self.classificationmatrix['subgroup'][pat_idx])[1]
            #t1 = time.time()
            class_codes = self.classlist['subgroup'][class_code_idxs]
            #t2 = time.time()
            """identify greenness"""
            is_green_ENVTECH = self.GIenvtech.match_any(class_codes)
            #t3 = time.time()
            is_green_IPCGI = self.GI_IPC.match_any(class_codes)
            #t4 = time.time()
            """record greenness"""
            self.pddf.loc[patID] = [is_green_ENVTECH, is_green_IPCGI]
            #t5 = time.time()
            #print(t1-t0, t2-t1, t3-t2, t4-t3, t5-t4)
        print("")
    
    
    def check_greenness2(self):
        """Method to find green patents based in the subgroup level classification matrix. Records this in pandas df.
            Arguments None
            Returns: None"""
        """Obtain 3 lists of Envtech matrix columns"""
        """Single code"""
        col_array_Envtech_single = self.GIenvtech.filter_matching(self.classlist['subgroup'])
        green_Envtech_single = self.classification_matrix_sum_by_indices(col_array_Envtech_single, level='subgroup')
        
        """Combined codes E03 and ..."""
        pseudoGIenvtech = GreenInventory("pseudo_envtech_conditional_complement_E03.txt")
        pseudoGIenvtech_E03 = GreenInventory("pseudo_envtech_conditional_E03.txt")
        col_array_Envtech_E03_complement = pseudoGIenvtech.filter_matching(self.classlist['subgroup'])
        col_array_Envtech_E03 = pseudoGIenvtech_E03.filter_matching(self.classlist['subgroup'])
        green_Envtech_E03_complement = self.classification_matrix_sum_by_indices(col_array_Envtech_E03_complement, level='subgroup')
        green_Envtech_E03 = self.classification_matrix_sum_by_indices(col_array_Envtech_E03, level='subgroup')
        
        """Perform computation to combine the 3 lists"""
        green_Envtech = green_Envtech_E03 * green_Envtech_E03_complement + green_Envtech_single
        green_Envtech = (green_Envtech>0)
        
        """Obtain 1 list of IPCGI matrix columns"""
        col_array_IPCGI = self.GI_IPC.filter_matching(self.classlist['subgroup'])
        green_IPCGI = self.classification_matrix_sum_by_indices(col_array_IPCGI, level='subgroup')
        green_IPCGI = (green_IPCGI>0)
        
        """Enter results in self.pddf data frame"""
        assert len(green_Envtech) == len(green_IPCGI) == len(self.patlist)
        for pat_idx, patID in enumerate(self.patlist):
            print("\rCheck greenness {0:10d}".format(pat_idx), end="")
            self.pddf.loc[patID] = [green_Envtech[pat_idx], green_IPCGI[pat_idx]]
        print("")
        
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
        
    
    def run(self):
        """Method to parse all classification files.
            No Arguments
            Returns None"""
        
        print("Commencing search. File: ")
        """parse all files"""
        n = 0
        for fname in self.classfilelist:
            n += 1
            print("{0:4d}".format(n), end="\r")
            #self.search_file(fname)
            self.search_IPC_file(fname)
            self.check_greenness2()
            
    
    def save(self):
        """Method to save the current state of data frame, matrixes and node lists.
            No Arguments
            Returns None"""
        """Save data frame"""
        self.pddf.to_pickle("patent_greenness_based_on_IPC.pkl")
        
        """save classification matrices"""
        matrix_save_names = {level: "patent_classification_matrix_level_" + str(level) + ".npz" for level in self.levels_list}
        classlist_save_names = {level: "patent_classification_codes_level_" + str(level) + ".pkl" for level in self.levels_list}
        patentID_save_name = "patent_codes.pkl"
        print("Saving node keys")
        with open(patentID_save_name, "wb") as wfile:
            pickle.dump(self.patlist, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        for level in self.levels_list:
            with open(classlist_save_names[level], "wb") as wfile:
                pickle.dump(self.classlist[level], wfile, protocol=pickle.HIGHEST_PROTOCOL)
        for level in self.levels_list:
            print("Transforming matrix")
            save_mtx = self.classificationmatrix[level].tocsr()
            print("Matrix transformed. Saving...")
            scipy.sparse.save_npz(matrix_save_names[level], save_mtx)
            print("Matrix saved.")
    
    def reload(self):
        """Method to reload the initial data frame, matrixes and node lists.
            No Arguments
            Returns None"""
        """Read data frame"""
        self.pddf = pd.read_pickle("patent_greenness_based_on_IPC.pkl")
        
        """Read classification matrices"""
        matrix_save_names = {level: "patent_classification_matrix_level_" + str(level) + ".npz" for level in self.levels_list}
        classlist_save_names = {level: "patent_classification_codes_level_" + str(level) + ".pkl" for level in self.levels_list}
        patentID_save_name = "patent_codes.pkl"
        print("Reloading node keys")
        with open(patentID_save_name, "rb") as rfile:
            self.patlist = pickle.load(rfile)
        for level in self.levels_list:
            with open(classlist_save_names[level], "rb") as rfile:
                self.classlist[level] = pickle.load(rfile)
        for level in self.levels_list:
            print("Reloading matrix...")
            reloaded_matrix = scipy.sparse.load_npz(matrix_save_names[level])
            print("Transforming matrix")
            self.classificationmatrix[level] = reloaded_matrix.todok()
            
            
        
    def prepare_lists_and_matrices(self, filelist):
        """Methods to identify the complete set of patent IDs and classification codes in order
           to create sparse matrices of the correct size before parsing begins.
            Arguments:
                filelist - list of strings - list of paths to classification files
            Returns None"""
        
        """Prepare local variables: dicts of IDs and codes and counters"""
        patdict = {}
        classdict = {item: {} for item in self.levels_list}
        #classdict_coarse = {}
        pat_idx = 0
        class_idx = {item: 0 for item in self.levels_list}
        #class_c_idx = 0
        
        """Parse all files"""
        for filename in filelist:
            i = -1
            for line in line_generator_from_file(filename):
                i += 1
                print("\rPrepare matrices {0:10d}".format(i), end="")

                """Obtain current code and paten ID"""
                
                patID, class_code = self.parse_line(line)
                            
                """Check if ID and code have been recorded already, otherwise update."""
                
                if patdict.get(patID) is None:
                    patdict[patID] = pat_idx
                    pat_idx += 1
                
                for level in self.levels_list:
                    classID = class_code[level]
                    if classdict[level].get(classID) is None:
                        classdict[level][classID] = class_idx
                        class_idx[level] += 1
                
                #if classdict.get(classID) is None:
                #    classdict[classID] = class_idx
                #    class_idx += 1
                #
                #if classdict_coarse.get(classID_coarse) is None:
                #    classdict_coarse[classID_coarse] = class_c_idx
                #    class_c_idx += 1
        print("")
        
        """Record lists of uniques IDs and codes"""
        self.patlist = list(patdict.keys())
        for level in self.levels_list:
            self.classlist[level] = np.array(list(classdict[level].keys()))
        #self.classlist_coarse = list(classdict_coarse.keys())
        
        """Setup sparse matrices"""
        for level in self.levels_list:
            self.classificationmatrix[level] = scipy.sparse.dok_matrix((pat_idx, class_idx[level]), dtype=bool)
        #self.classificationmatrix_coarse = scipy.sparse.dok_matrix((pat_idx, class_c_idx), dtype=bool)

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



""" main entry point """

if __name__ == "__main__":
        GR = GreennessRecord()
        GR.save()
        GR.reload()
        print("""Setup is done. Running...""")
        GR.run()
        GR.save()
    
