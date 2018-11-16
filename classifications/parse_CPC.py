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
    - GreenRecord as record class

The script is intended to be run in 10 different instances in different shells after an initial
setup of the matrices and dataframe. First do the setup:
    python3 parse_CPC.py
And then run the 10 chunks:
    python3 parse_CPC.py 0
    python3 parse_CPC.py 1
    python3 parse_CPC.py 2
    python3 parse_CPC.py 3
    python3 parse_CPC.py 4
    python3 parse_CPC.py 5
    python3 parse_CPC.py 6
    python3 parse_CPC.py 7
    python3 parse_CPC.py 8
    python3 parse_CPC.py 9
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
    def __init__(self, chunk_idx = None):
        """Constructor method.
           Assumes that the classification files from USPTO US_Grant_CPC_MCF_Text_2018-08-01.zip are unpacked
            in the current working directory, i.e. the individual files are "./US_Grant_CPC_MCF_Text_2018-08-01/*"
            With the optional argument, it is possible to parse only a chunk of 20 of the 200 source files. This 
            allows for multiple instances of the script to work in parallel, the matrices and data frames can
            afterwards be combined. (This requires the matrices to already be set up, which is done at the beginning
            of running this script without optional argument before)
            Arguments: 
                chunk_idx - int \in [0,9] - ch
            Returns class instance."""
        
        """Identify classification files"""
        self.classfilelist = glob.glob("./US_Grant_CPC_MCF_Text_2018-08-01/*")
        """for testing and debugging with a smaller data set comment in this line"""
        #self.classfilelist = ["./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08000000.txt"]
        self.chunk_idx = chunk_idx
        
        if chunk_idx is not None:
            """separated into chunks"""
            """Classfilelist is split into chunks like so:
                bounds = list(range(0, 201, 20))[:-1]+[201]
                classfilelist = [classfilelist[bounds[i]:bounds[i+1]] for i in range(len(bounds)-1)]
               But hardcoding chunks with filenames avoids errors."""
            self.classfilelist = [['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00000001.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_00950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_01950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_02950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_03950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_04950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_05950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_06950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_07950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_08950000.txt'], ['./US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09000000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09050000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09100000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09150000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09200000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09250000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09300000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09350000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09400000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09450000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09500000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09550000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09600000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09650000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09700000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09750000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09800000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09850000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09900000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_09950000.txt', './US_Grant_CPC_MCF_Text_2018-08-01/US_Grant_CPC_MCF_10000000.txt']]
            self.classfilelist = self.classfilelist[chunk_idx] 
            
            """Prepare matrices"""
            print("Preparing matrices")
            self.reload()
        
        else:        
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
            self.search_file(fname)
    
    def save(self):
        """Method to save the current state of data frame, matrixes and node lists.
            No Arguments
            Returns None"""
        """Save data frame"""
        if self.chunk_idx is not None:
            self.pddf.to_pickle("patent_greenness_based_on_CPC_" + str(self.chunk_idx) + ".pkl")
        else:
            self.pddf.to_pickle("patent_greenness_based_on_CPC.pkl")
        
        """save classification matrices"""
        matrix_handles = [self.classificationmatrix, self.classificationmatrix_coarse]
        save_list = [self.patlist, self.classlist, self.classlist_coarse]
        if self.chunk_idx is not None:
            matrix_save_names = ["patent_detailed_classification_matrix_" + str(self.chunk_idx) + ".npz", "patent_classification_matrix_" + str(self.chunk_idx) + ".npz"]
            save_list_name = "patent_classification_matrix_node_keys" + str(self.chunk_idx) + ".pkl"
        else:
            matrix_save_names = ["patent_detailed_classification_matrix.npz", "patent_classification_matrix.npz"]
            save_list_name = "patent_classification_matrix_node_keys.pkl"
        for i in range(len(matrix_save_names)):
            print("Saving node keys")
            with open(save_list_name, "wb") as wfile:
                pickle.dump(save_list, wfile, protocol=pickle.HIGHEST_PROTOCOL)
            print("Transforming matrix")
            save_mtx = matrix_handles[i].tocsr()
            print("Matrix transformed. Saving...")
            scipy.sparse.save_npz(matrix_save_names[i], save_mtx)
            print("Matrix saved.")
    
    def reload(self):
        """Method to reload the initial data frame, matrixes and node lists.
            No Arguments
            Returns None"""
        """Read data frame"""
        self.pddf = pd.read_pickle("patent_greenness_based_on_CPC.pkl")
        
        """Read classification matrices"""
        matrix_handles = [None, None]
        matrix_save_names = ["patent_detailed_classification_matrix.npz", "patent_classification_matrix.npz"]
        print("Reloading node keys")
        with open("patent_classification_matrix_node_keys.pkl", "rb") as rfile:
            self.patlist, self.classlist, self.classlist_coarse = pickle.load(rfile)
        for i in range(len(matrix_save_names)):
            print("Reloading matrix...")
            reloaded_matrix = scipy.sparse.load_npz(matrix_save_names[i])
            print("Transforming matrix")
            matrix_handles[i] = reloaded_matrix.todok()
        self.classificationmatrix, self.classificationmatrix_coarse = matrix_handles
            
            
        
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
    if not len(sys.argv) > 1:
        GR = GreennessRecord()
        GR.save()
        GR.reload()
        print("""Setup is done. Feel free to interrupt (CTRL+C) and run the script in parallel for 10 chunks, doing, in different shells:\n
                 python3 parse_CPC.py 0\n
                 python3 parse_CPC.py 1\n
                 python3 parse_CPC.py 2\n
                 python3 parse_CPC.py 3\n
                 python3 parse_CPC.py 4\n
                 python3 parse_CPC.py 5\n
                 python3 parse_CPC.py 6\n
                 python3 parse_CPC.py 7\n
                 python3 parse_CPC.py 8\n
                 python3 parse_CPC.py 9""")
        print("If you do not interrupt, the script will continue and parse all files. This will take a very long time.")
        GR.run()
        GR.save()
    else:
        chunk_idx = int(sys.argv[1])
        GR = GreennessRecord(chunk_idx)
        GR.run()
        GR.save()
