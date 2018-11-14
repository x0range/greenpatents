"""Script to parse CPC classification codes for all patents starting 1976.
   The script reads the classification code files US_Grant_CPC_MCF_Text_2018-08-01.zip
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
    - GreenRecord as record class"""

"""inport modules"""
import numpy as np
import scipy
import scipy.sparse
import pickle
import pandas as pd
import glob
import pdb


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
    
    def match_combined(self, class_strings):
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
            
    def match_single(self, class_string):
        """Method to check if a class string matches a green technology as defined as single string.
            Arguments:
                class_string - string - classification code
            Returns: bool - patent is a green technology"""
        if any(st in class_string for st in self.single_patterns):
            return True
        else:
            return False

"""Green patents record class. Can parse classification files, apply search patterns and save records"""
class GreennessRecord():
    def __init__(self):
        """Constructor method.
           Assumes that the classification files from USPTO US_Grant_CPC_MCF_Text_2018-08-01.zip are unpacked
            in the current working directory, i.e. the individual files are "./US_Grant_CPC_MCF_Text_2018-08-01/*"
            Arguments: None
            Returns class instance."""
        
        """Identify classification files"""
        self.classfilelist = glob.glob("./US_Grant_CPC_MCF_Text_2018-08-01/*")
        """for testing and debugging with a smaller data set comment in this line"""
        #self.classfilelist = ["./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08000000.txt"]
        
        """Prepare matrices"""
        print("Preparing matrices")
        self.prepare_lists_and_matrices(self.classfilelist)
        
        """Prepare search patterns"""
        print("Preparing search patterns")
        self.GIenvtech = GreenInventory("envtech_03.txt")
        self.GI_IPC = GreenInventory("green_inventory_03.txt")
        self.pddf = pd.DataFrame(columns=['envtech', 'IPCGI'])  #greenness data frame
        print("All set up.")
        
    def finalize_greenness_record(self, patID, is_green_ENVTECH, is_green_IPCGI, class_strings):
        """Method to affect final checks on green pattern matching (with combined patterns of several
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
        
    def search_file(self, classificationfile):
        """Method to parse one classification file. Will identify all patent classification codes for
           each patent, check greenness, record greenness and update the classification networks.
            Arguments:
                classificationfile - string - path to classification file
            Returns None"""

        """prepare variables"""
        class_strings = []
        is_green_ENVTECH = False
        is_green_IPCGI = False    
        
        """cycle through lines of classification file"""
        first_record = True
        n = 0
        print("Parsing line: ")
        for line in line_generator_from_file(classificationfile):
            n += 1
            print("{0:4d}".format(n), end="\r")
            """read class codes"""
            classID = line[18:33].strip()
            classID_coarse = line[18:22]
            primary_ID = True if line[41]=="F" else False
            
            """record and reset if records for the previous patent are concluded"""
            if primary_ID == True and first_record == False:      # end records for single patent
                self.finalize_greenness_record(patID, is_green_ENVTECH, is_green_IPCGI, class_strings)
                is_green_ENVTECH = False
                is_green_IPCGI = False    
                class_strings = []
            
            """Set first_record to false so that subsequent ends of patent records can be sucessfully recognized"""
            first_record = False

            """read new patent ID. (Up to the record and reset step, the previous patentID must be in memory.)"""
            patID = line[10:18]
            
            """update greenness"""
            class_strings.append(classID)
            if not is_green_ENVTECH:
                is_green_ENVTECH = self.GIenvtech.match_single(classID)
            if not is_green_IPCGI:
                is_green_IPCGI = self.GI_IPC.match_single(classID)
            
            """update matrices"""
            pat_idx = self.patlist.index(patID)
            class_idx = self.classlist.index(classID)
            class_coarse_idx = self.classlist_coarse.index(classID_coarse)
            self.classificationmatrix[pat_idx, class_idx] = 1
            self.classificationmatrix_coarse[pat_idx, class_coarse_idx] = 1
        
        """record last patent"""    
        self.finalize_greenness_record(patID, is_green_ENVTECH, is_green_IPCGI, class_strings)
        print("")
    
    def run_and_save(self):
        """Method to parse all classification files and to record the result.
            No Arguments
            Returns None"""
        
        print("Commencing search. File: ")
        """parse all files"""
        n = 0
        for fname in self.classfilelist:
            n += 1
            print("{0:4d}".format(n), end="\r")
            self.search_file(fname)
        
        """Save data frame"""
        self.pddf.to_pickle("patent_greenness_based_on_CPC.pkl")

        """save classification matrices"""
        matrix_handles = [self.classificationmatrix, self.classificationmatrix_coarse]
        matrix_save_names = ["patent_detailed_classification_matrix.npz", "patent_classification_matrix.npz"]
        for i in range(len(matrix_save_names)):
            print("Transforming matrix")
            save_mtx = matrix_handles[i].tocsr()
            print("Matrix transformed. Saving...")
            scipy.sparse.save_npz(matrix_save_names[i], save_mtx)
            print("Matrix saved.")
        
    def prepare_lists_and_matrices(self, filelist):
        """Methods to identify the complete set of patent IDs and classification codes in order
           to create sparse matrices of the correct size before parsing begins.
            Arguments:
                filelist - list of strings - list of paths to classification files
            Returns None"""
        
        """Prepare local variables: dicts of IDs and codes and counters"""
        patdict = {}
        classdict = {}
        classdict_coarse = {}
        pat_idx = 0
        class_idx = 0
        class_c_idx = 0
        
        """Parse all files"""
        for filename in filelist:
            for line in line_generator_from_file(filename):
                
                """Obtain current ID and code"""
                classID = line[18:33].strip()
                classID_coarse = line[18:22]
                patID = line[10:18]
                
                """Check if ID and code have been recorded already, otherwise update."""
                
                if patdict.get(patID) is None:
                    patdict[patID] = pat_idx
                    pat_idx += 1
                    
                if classdict.get(classID) is None:
                    classdict[classID] = class_idx
                    class_idx += 1
                
                if classdict_coarse.get(classID_coarse) is None:
                    classdict_coarse[classID_coarse] = class_c_idx
                    class_c_idx += 1
        
        """Record lists of uniques IDs and codes"""
        self.patlist = list(patdict.keys())
        self.classlist = list(classdict.keys())
        self.classlist_coarse = list(classdict_coarse.keys())
        
        """Setup sparse matrices"""
        self.classificationmatrix = scipy.sparse.dok_matrix((pat_idx, class_idx), dtype=bool)
        self.classificationmatrix_coarse = scipy.sparse.dok_matrix((pat_idx, class_c_idx), dtype=bool)

"""Function definitions"""

def line_generator_from_file(filename):
    """Generator function. Opens filename and creates a generator that returns the relevant
       lines one by one (ignoring those starting with "#" 
        Arguments:
            filename - string - file name
        Returns generator"""
    with open(filename, "r") as rfile:
        for line in rfile:
            if not line[0] == "#":
                line = line.replace("\n", "")
                yield line



""" main entry point """

if __name__ == "__main__":
    GR = GreennessRecord()
    GR.run_and_save()
