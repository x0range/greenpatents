"""Script to parse CPC classification codes for all patents starting 1976.
   The script reads the classification code files US_Grant_CPC_MCF_Text_2018-08-01.zip
   from USPTO as well as search pattern files for green technologies:
    - OECD ENVTECH from file envtech_03.txt
    - CPC green inventory from file green_inventory_03.txt
   The script records:
    - a pandas dataframe indicating membership in sets of green patents as pickle file
    - the classification bipartite network (patents vs. unique classification codes considering
        class and subclass only, disregarding group and subgroup) as npz file
    - the detailed classification bipartite network (patents vs. unique classification codes) 
        as npz file.
   The script defines two classes:
    - GreenInventory as search pattern class.
    - GreenRecord as record class

How to run:

python3 parse_CPC.py --setup
python3 parse_CPC.py --parse
python3 parse_CPC.py --greenness

OR:

python3 parse_CPC.py --setup
python3 parse_CPC.py --splitCPCfile
python3 parse_CPC.py --parse --chunk i # for i in 0-19 in parallel in different terminals
python3 parse_CPC.py --loadchunks
python3 parse_CPC.py --greenness

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
import os.path
import subprocess
import argparse

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
    def __init__(self, setup=False, loadchunks=False, chunk_idx=None):
        """Constructor method.
           Assumes that the classification files from USPTO cpc_current.tsv.zip is unpacked
            in the current working directory, i.e. the individual file is "./cpc_current.tsv"
            Arguments: 
                loadchunks - bool - Should this run load previously computed chunks (ergo, no setup, parsing,
                                    since that must already be done)?
                chunk_idx  - int  - Chunk index number to be parsed. Affects classfilelist definition.
                setup      - bool - Should matrices etc be newly set up (empty)?
            Returns class instance."""
        
        """Prepare variables"""
        self.chunk_idx = chunk_idx
        self.levels_list = ['section', 'subsection', 'group', 'subgroup']
        self.patlist = None
        self.classlist = {}
        self.classificationmatrix = {}
        self.pddf = pd.DataFrame(columns=['envtech', 'IPCGI'])  #greenness data frame. Will be overwritten when created.
        """Prepare search patterns"""
        #print("Preparing search patterns")
        self.GIenvtech = GreenInventory("envtech_03.txt")
        self.GI_CPC = GreenInventory("green_inventory_03.txt")
        
        """Identify classification files"""
        self.classfilelist = ['./cpc_current.tsv']
        if loadchunks:
            self.classfilelist = None               # Parsing has to be completed in this case
        if self.chunk_idx is not None:
            self.classfilelist = ['./cpc_current_{}.tsv'.format(chunk_idx)]
        """Prepare matrices"""
        if setup:
            print("Preparing matrices")
            self.prepare_lists_and_matrices(self.classfilelist)
        #print("All set up.")

    def parse_line(self, line):
        """Method to parse one lingle line from the classification file
            Arguments:
                line - string - The line
            Returns:
                tuple of:
                    patID - string - the patent ID
                    class_code - dict - the class code at different depth levels."""
        class_code_raw = line.split('\t')
        #class_code_raw = [it for it in class_code_raw if not it==""]
        class_code_raw = class_code_raw[1:6]
        #class_code_raw = np.asarray(class_code_raw)
        
        patID = class_code_raw[0]
        
        class_code = {}
        class_code['section'] = class_code_raw[1]
        class_code['subsection'] = class_code_raw[2]
        class_code['group'] = class_code_raw[3]
        class_code['subgroup'] = class_code_raw[4]
        return patID, class_code
        
    
    def search_CPC_file(self, classificationfile):
        """Method for parsing CPC file. Identifies citations and records matrices
            Arguments:
                classificationfile - string - the classification file to be used
            Returns None."""
        i = 0
        for line in line_generator_from_file(classificationfile):
            i += 1
            print("\rSearch CPC file {0:10d}".format(i), end="")
            """read class codes and patent ID"""
            patID, class_code = self.parse_line(line)
            
            """update matrices"""
            for level in self.levels_list:
                classID = class_code[level]
                pat_idx = self.patlist.index(patID)
                class_idx = int(np.where(self.classlist[level]==classID)[0])
                self.classificationmatrix[level][pat_idx, class_idx] = 1
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
        green_Envtech_E03_complement = self.classification_matrix_sum_by_indices(col_array_Envtech_E03_complement, \
                                                                                                    level='subgroup')
        green_Envtech_E03 = self.classification_matrix_sum_by_indices(col_array_Envtech_E03, level='subgroup')
        
        """Perform computation to combine the 3 lists"""
        green_Envtech = green_Envtech_E03 * green_Envtech_E03_complement + green_Envtech_single
        green_Envtech = (green_Envtech>0)
        
        """Obtain 1 list of IPCGI matrix columns"""
        col_array_IPCGI = self.GI_CPC.filter_matching(self.classlist['subgroup'])
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
        
    
    def run_search(self):
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
            self.search_CPC_file(fname)
    
    def save(self):
        """Method to save the current state of data frame, matrixes and node lists.
            No Arguments
            Returns None"""
        """Save data frame"""
        self.pddf.to_pickle("patent_greenness_based_on_CPC.pkl")
        
        """save classification matrices"""
        if self.chunk_idx is not None:
            matrix_save_names = {level: "patent_classification_matrix_level_" + str(level) + "_chunk_" + \
                                                str(self.chunk_idx) + ".npz" for level in self.levels_list}        
        else:
            matrix_save_names = {level: "patent_classification_matrix_level_" + str(level) + ".npz" \
                                                                            for level in self.levels_list}
            classlist_save_names = {level: "patent_classification_codes_level_" + str(level) + ".pkl" \
                                                                            for level in self.levels_list}
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
        self.pddf = pd.read_pickle("patent_greenness_based_on_CPC.pkl")
        
        """Read classification matrices"""
        matrix_save_names = {level: "patent_classification_matrix_level_" + str(level) + ".npz" \
                                                                                for level in self.levels_list}
        classlist_save_names = {level: "patent_classification_codes_level_" + str(level) + ".pkl" \
                                                                                for level in self.levels_list}
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
        pat_idx = 0
        class_idx = {item: 0 for item in self.levels_list}
        
        """Parse all files"""
        for filename in filelist:
            i = 0
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
                
        print("")
        
        """Record lists of uniques IDs and codes"""
        self.patlist = list(patdict.keys())
        for level in self.levels_list:
            self.classlist[level] = np.array(list(classdict[level].keys()))
        
        """Setup sparse matrices"""
        for level in self.levels_list:
            self.classificationmatrix[level] = scipy.sparse.dok_matrix((pat_idx, class_idx[level]), dtype=bool)
        #self.classificationmatrix_coarse = scipy.sparse.dok_matrix((pat_idx, class_c_idx), dtype=bool)

    def collect_chunks(self):
        """Method to collect and combine all previously computed matrix chunks.
        Arguments: None.
        Returns None."""
        
        """Assert presence of all matrix files"""
        filenames = {}
        for level in self.levels_list:
            filenames[level] = ["patent_classification_matrix_level_" + str(level) + "_chunk_" + str(i) + ".npz" \
                                                                                                for i in range(20)]
            for i in range(len(filenames[level])):
                assert os.path.exists(filenames[level][i]), "File not found: {}".format(filenames[level][i])
        
        """Load and add one by one."""
        for level in self.levels_list:
            for i, filename in enumerate(filenames[level]):
                print("Level {2:10s}; parsing {0} of {1}".format(i, len(filenames[level]), level))
                pcm = scipy.sparse.load_npz(filename)
                expected_sum = np.sum(self.classificationmatrix[level]) + np.sum(pcm)
                self.classificationmatrix[level] = self.classificationmatrix[level] + pcm
                try:
                    assert expected_sum == np.sum(self.classificationmatrix[level]), \
                                    "expected sum does not match actual sum: {0} != {1}".format(expected_sum, 
                                                                    np.sum(self.classificationmatrix[level]))
                except:
                    pass

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

def splitCPCfile():
    """Function for splitting the input class file into 20 chunks to be parsed subsequently.
       Determines the appropriate file length using UNIX 'wc -l' via python subprocess. Then creates the files
       with UNIX 'cat filename | head -line| tail -line >> filename' via python os.system().
        Arguments: None.
        Returns None."""
    p = subprocess.Popen(['wc', '-l', './cpc_current.tsv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    assert p.returncode == 0, "Error in counting lines in classfile cpc_current.tsv: {}".format(err)
    line_num = int(result.strip().split()[0])
    chunks = np.linspace(0, line_num, 21, dtype=np.int64)
    stop_idxs = chunks[1:]
    lens = chunks[1:] - chunks[:-1]
    for i in range(20):
        os.system("cat ./cpc_current.tsv | head -{0} | tail -{1} >> cpc_current_{2}.tsv".format(stop_idxs[i], lens[i], \
                                                                                                                    i))

""" main entry point """

if __name__ == "__main__":
    """Parse terminal arguments"""
    parser = argparse.ArgumentParser(description="""Patent classification parser.\n    How to run:

        python3 parse_CPC.py --setup
        python3 parse_CPC.py --parse
        python3 parse_CPC.py --greenness

    or, alternatively:

        python3 parse_CPC.py --setup
        python3 parse_CPC.py --splitCPCfile
        python3 parse_CPC.py --parse --chunk i # for i in 0-19 in parallel in different terminals
        python3 parse_CPC.py --loadchunks
        python3 parse_CPC.py --greenness
    """, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--setup", action="store_true", help="Do the initial setup of matrices, data structures.")
    parser.add_argument("--chunk", type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, \
                                        18, 19], help="Chunk for inputfile parsing. Use full raw data if not given.")
    parser.add_argument("--parse", action="store_true", help="Parse classifications.")
    parser.add_argument("--greenness", action="store_true", help="Check for greenness and save data frame.")
    parser.add_argument("--loadchunks", action="store_true", help="Load and combine chunks after parsing by chunk.")
    parser.add_argument("--splitCPCfile", action="store_true", help="Load and combine chunks after parsing by chunk.")

    args = parser.parse_args()
    
    """Catch inadmissible and critical argument combinations"""
    assert not (args.parse and args.loadchunks), "Error: Can only load chunks when parsing is completed. Stop."
    try:
        assert not ((args.chunk is not None) and (not args.parse)), \
                                            "Warning: Chunk index is ignored if parse is not set. Continuing..."
    except:
        pass
    assert not ((args.chunk is not None) and args.greenness), \
                                    "Error: Greenness check can only be done once all chunks are parsed. Stop."
    
    """For splitfile, just split the file and exit"""
    if args.splitCPCfile:
        print("Separating input file.")
        splitCPCfile()
        print("Done. Now you can parse by chunks.")
        raise SystemExit
        
    if args.setup:
        print("Setup...")
        GR = ClassificationAndGreennessRecord(setup=True, loadchunks=False, chunk_idx=None)
        GR.save()
    elif args.loadchunks:
        GR = ClassificationAndGreennessRecord(setup=False, loadchunks=True, chunk_idx=None)
    elif args.chunk is not None:
        GR = ClassificationAndGreennessRecord(setup=False, loadchunks=False, chunk_idx=args.chunk)
    else:
        GR = ClassificationAndGreennessRecord(setup=False, loadchunks=False, chunk_idx=None)
    if args.setup or args.parse or args.loadchunks or args.greenness:
        GR.reload()
        print("Setup is done.")
    if args.parse:
        print("Running parse. Chunk ", end="")
        if args.chunk is not None:
            print("{} ...".format(args.chunk))
        else:
            print("ALL\nThis is going to take a very long time.")
        GR.run_search()
        print("Done. Saving.")
        GR.save()
    if args.loadchunks:
        print("Collecting chunks ...")
        GR.collect_chunks()
        print("Done. Saving.")
        GR.save()
    if args.greenness:
        print("Running greenness check ...")
        GR.check_greenness2()
        print("Done. Saving.")
        GR.save()
