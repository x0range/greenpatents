# prototype

# from https://stackoverflow.com/questions/48897635/given-a-geographical-coordinate-in-u-s-how-to-find-out-if-it-is-in-urban-or-ru
# with shapefile from https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-urban-area/

import shapefile
from shapely.geometry import Point 
from shapely.geometry import shape 
import pandas as pd
import sys
import pdb


class AssigneeDataParser():
    def __init__(self):
        """prepare geo-lookup for urben/rural"""
        self.shp = shapefile.Reader('ne_10m_urban_areas.shp') #open the shapefile
        self.all_shapes = self.shp.shapes() # get all the polygons
        #all_records = shp.records()
        
        """prepare variables"""
        self.assigneeDict = {}
        self.patentDict = {}
        self.locationsDict = {}

    def is_urban(self, pt):       
        """Method to identify rural/urban status corresponding to pair of coordinates.
           Adapted from https://stackoverflow.com/questions/48897635
            Arguments:
                pt - tuple - coordinates (Latitude, Longitude)
            Returnd:
                bool - is this an urban place"""
        pt = (pt[1], pt[0]) # reverse coordinate order
        result = False
        for current_shape in self.all_shapes:
            if not result:
                result = Point(pt).within(shape(current_shape))
        #print (pt, result)
        return result

    def parse_locations(self, sourcefile="location.tsv"):
        """Method to parse locations. Populates location dict"""
        count = 0
        with open(sourcefile, "r") as ifile:
            _ = ifile.readline()
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                locID, locCountry, locState, locLat, locLong = elementi[0], elementi[3], elementi[2], float(elementi[4]), float(elementi[5])
                locIsUrban = self.is_urban((locLat, locLong))
                
                """ attach to dict"""
                self.locationsDict[locID] = {"urban": locIsUrban, "country": locCountry, "state": locState, "latitude": locLat, "longitude": locLong}       

    def parse_location_assignee_correspondence(self, sourcefile="location_assignee.tsv"):
        """Method to parse assignee-location correspondence. Populates assignee dict with 
           corresponding location data."""
        count = 0
        with open(sourcefile, "r") as ifile:
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                locID, assigneeID = elementi[0], elementi[1].replace("\n", "")
                
                """ match """
                self.assigneeDict[assigneeID] = self.locationsDict[locID]
            
    def parse_assignee(self, sourcefile="assignee.tsv"):
        """Method to parse assignee data. Populates assignee dict with all except location."""
        count = 0
        with open(sourcefile, "r") as ifile:
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                assigneeID, assigneeType, assigneeName = elementi[0], int(elementi[1]), elementi[4].replace("\n", "")
                """Assignee types are:
                        2 - US Company or Corporation, 
                        3 - Foreign Company or Corporation, 
                        4 - US Individual, 
                        5 - Foreign Individual, 
                        6 - US Government, 
                        7 - Foreign Government, 
                        8 - Country Government, 
                        9 - State Government (US). 
                        Note: A "1" appearing before any of these codes signifies part interest)
                   Universities count as private. Therefore that needs to be scraped out of the Names.
                    """
                
                """keyword search of assignee name to identify universities, research institutes etc. as non-private"""
                isPrivate = True
                company_cindicating_terms = ["Ltda.", "Ltd.", "S.a.r.l.", "LLC", "GmbH", "GBR", "Inc.", "Private Inst",  
                                             "Co.", "S.A.", "S.a.S.", "S.p.A.", "S.n.c.", "S.a.p.a.", "SNC", "SARL", 
                                             "A.G.", "Company", "Corp.", "INC", "L.L.C.", "S.L.", "S.r.l.", "AG"]
                university_indicating_terms = ["Universit",  "universit", "Ecole", "Escuel", "Hochschule", 
                                               "hochschul", "Regent", "Univ.", "Akadem"]
                if (assigneeType in [6, 7, 8, 9]):
                    isPrivate = False
                elif any(st in assigneeName for st in university_indicating_terms):       # use terms from Nanda et al
                    isPrivate = False
                elif any(st in assigneeName for st in ["Inst.", "Institut", "Academ"]) and \
                                not any(st in assigneeName for st in company_cindicating_terms):
                    isPrivate = False
                
                """ match """ 
                self.assigneeDict[assigneeID]["officialType"] = assigneeType
                self.assigneeDict[assigneeID]["private"] = isPrivate
                #print(assigneeDict[assigneeID])

    def parse_patent_assignee_correspondence(self, sourcefile="patent_assignee.tsv"):
        """Method to parse patent-assignee correspondence. Populates patent dict with 
           corresponding assignee data."""
        count = 0
        with open(sourcefile, "r") as ifile:
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                patentID, assigneeID = elementi[0], elementi[1].replace("\n", "")
                
                # match 
                locRecord = self.assigneeDict[assigneeID]
                self.patentDict[patentID] = {"urban": locRecord["urban"], "country": locRecord["country"], 
                                        "state": locRecord["state"], "officialtype": locRecord["officialType"],
                                        "private": locRecord["private"], "latitude": locRecord["latitude"], 
                                        "longitude": locRecord["longitude"]}
                #print(patentDict[patentID])


    def populate_and_save(self):
        """Method to govern population of the records from source files.
           Will transform patentDict to pandas and save the data frame in the end.
           No Arguments, no returns."""
        print("Parse location data ...")
        sys.stdout.flush()
        self.parse_locations()
                    
        print(" Finished.\nParse assignee data, match location data...")
        sys.stdout.flush()
        self.parse_location_assignee_correspondence()
                
        print(" Finished.\nParse assignee type data...")
        sys.stdout.flush()
        self.parse_assignee()
                
        print(" Finished.\nParse patent data, match assignee data...")
        sys.stdout.flush()
        self.parse_patent_assignee_correspondence()
        
        print(" Finished.\nTransform to pandas and save...")
        sys.stdout.flush()
        self.df = pd.DataFrame.from_dict(self.patentDict, orient="index")
        self.df.to_pickle("./patents_table.pkl")
        print(" Finished.\n\nAnything else?")
        pdb.set_trace()


# main entry point

if __name__ == "__main__":
    
    ADP = AssigneeDataParser()
    ADP.populate_and_save()

