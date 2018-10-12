"""
Patterns for identifying green technologies in text descriptions such as patent abstracts. 
Follows Shapira et al. (2014) p.102 http://dx.doi.org/10.1016/j.techfore.2013.10.023
"""

import re

def pattern01_general(text):
    if re.search(re.compile(r"\bsustainab\w*"), text):
        return True
    if re.search(re.compile(r"\bgreen good\w*"), text):
        return True
    if re.search(re.compile(r"\bgreen technolog\w*"), text):
        return True
    if re.search(re.compile(r"\bgreen innov\w*"), text):
        return True
    if re.search(re.compile(r"\beco\w*innov\w*"), text):
        return True
    if re.search(re.compile(r"\bgreen manufac\w*"), text):
        return True
    if re.search(re.compile(r"\bgreen prod\w*"), text):
        return True
    if re.search(re.compile(r"\bpollut\w*"), text):
        return True
    if re.search(re.compile(r"\becolabel"), text):
        return True
    if re.search(re.compile(r"\benviron\w* product declarat\w*"), text):
        return True
    if re.search(re.compile(r"\bEPD"), text) and re.search(re.compile(r"\benviron\w*"), text):
        return True
    if re.search(re.compile(r"\benviron\w* prefer\w* product\w*"), text):
        return True
    if re.search(re.compile(r"\benviron\w* label\w*"), text):
        return True
    return False
    
def pattern02_Environmental_All_purpose(text):
    if re.search(re.compile(r"\bnatur\w* environ\w*"), text):
        return True
    if re.search(re.compile(r"\benviron\w* friend\w*"), text):
        return True
    if re.search(re.compile(r"\benvironment\w* conserv\w*"), text):
        return True
    if re.search(re.compile(r"\bbiocompat\w*"), text):
        return True
    if re.search(re.compile(r"\bbiodivers\w*"), text):
        return True
    if re.search(re.compile(r"\bfilter\w*"), text):
        return True
    if re.search(re.compile(r"\bfiltra\w*"), text):
        return True
    if re.search(re.compile(r"\bsynth\w* gas\w*"), text):
        return True
    if re.search(re.compile(r"\bregenerat\w*"), text):
        return True
    if re.search(re.compile(r"\brecircul\w*"), text):
        return True
    if re.search(re.compile(r"\bgasification"), text):
        return True
    if re.search(re.compile(r"\bgasifier"), text):
        return True
    if re.search(re.compile(r"\bfluidized clean gas"), text):
        return True
    if re.search(re.compile(r"\bgas cleaning"), text):
        return True
    return False

def pattern03_Environmental_Biological_treatment(text):
    if re.search(re.compile(r"\bbioremed\w*"), text) or re.search(re.compile(r"\bbiorecov\w*"), text) or \
       re.search(re.compile(r"\bbiolog\w* treat\w*"), text) or re.search(re.compile(r"\bbiodegrad\w*"), text):
        if re.search(re.compile(r"\bbiogas\w*"), text):
            return True
        if re.search(re.compile(r"\bbioreact\w*"), text):
            return True
        if re.search(re.compile(r"\bpolyolef\w*"), text):
            return True
        if re.search(re.compile(r"\bbiopolymer\w*"), text):
            return True
        if re.search(re.compile(r"\bdisinfect\w*"), text):
            return True
        if re.search(re.compile(r"\bbiofilm\w*"), text):
            return True
        if re.search(re.compile(r"\bbiosens\w*"), text):
            return True
        if re.search(re.compile(r"\bbiosolid\w*"), text):
            return True
        if re.search(re.compile(r"\bcaprolact\w*"), text):
            return True
        if (re.search(re.compile(r"\bultraviol\w*"), text) or re.search(re.compile(r"\bUV"), text)) and \
                 (re.search(re.compile(r"\bradiat\w*"), text) or re.search(re.compile(r"\bsol\w*"), text)):
            return True
    return False

def pattern04_Environmental_Air_pollution(text):
    if re.search(re.compile(r"\bpollut\w*"), text):
        if re.search(re.compile(r"\bair\w* contr\w*"), text):
            return True
        if re.search(re.compile(r"\bdust\w* contr\w*"), text):
            return True
        if re.search(re.compile(r"\bparticular\w* contr\w*"), text):
            return True
        if re.search(re.compile(r"\bair\w* qual\w*"), text):
            return True
    return False
        
def pattern05_Environmental_Environmental_monitoring(text):
    if re.search(re.compile(r"\benviron\w* monitor\w*"), text):
        if (re.search(re.compile(r"\benviron\w*"), text) and re.search(re.compile(r"\binstrument\w*"), text)) or \
            (re.search(re.compile(r"\benviron\w*"), text) and re.search(re.compile(r"\banalys\w*"), text)):
            # note that including keyword "environ" here is unneccessary, because this is implied by the first condition
            return True
        if re.search(re.compile(r"\blife\w*cycle analysis"), text):
            return True
        if re.search(re.compile(r"\blife cycle analys\w*"), text):
            return True
    return False

def pattern06_Environmental_Marine_pollution(text):
    if re.search(re.compile(r"\bmarin\w* control\w*"), text) and re.search(re.compile(r"\bpollut\w*"), text):
        return True
    return False
    
def pattern07_Environmental_Noise_vibration(text):
    if re.search(re.compile(r"\bnois\w* abat\w*"), text):
        return True
    if re.search(re.compile(r"\bnois\w* reduc\w*"), text):
        return True
    if re.search(re.compile(r"\bnois\w* lessen\w*"), text):
        return True
    return False

def pattern08_Environmental_Contaminated_land(text):
    if re.search(re.compile(r"\bland"), text):
        if re.search(re.compile(r"\breclam\w*"), text):
            return True
        if re.search(re.compile(r"\bremediat\w*"), text):
            return True
        if re.search(re.compile(r"\bcontamin\w*"), text):
            return True
    return False
        
def pattern09_Environmental_Waste_management(text):
    if re.search(re.compile(r"\bwast\w*"), text):
        return True
    if re.search(re.compile(r"\bsewag\w*"), text):
        return True
    if re.search(re.compile(r"\binciner\w*"), text):
        return True
    return False
    
def pattern10_Environmental_Water_supply(text):
    if re.search(re.compile(r"\bwater treat\w*"), text) or re.search(re.compile(r"\bwater purif\w*"), text) or \
                                                            re.search(re.compile(r"\bwater pollut\w*"), text):
        if re.search(re.compile(r"\bslurr\w*"), text):
            return True
        if re.search(re.compile(r"\bsludg\w*"), text):
            return True
        if re.search(re.compile(r"\baque\w* solution\w*"), text):
            return True
        if re.search(re.compile(r"\bwastewat\w*"), text):
            return True
        if re.search(re.compile(r"\beffluent\w*"), text):
            return True
        if re.search(re.compile(r"\bsediment\w*"), text):
            return True
        if re.search(re.compile(r"\bfloccul\w*"), text):
            return True
        if re.search(re.compile(r"\bdetergen\w*"), text):
            return True
        if re.search(re.compile(r"\bcoagul\w*"), text):
            return True
        if re.search(re.compile(r"\bdioxin\w*"), text):
            return True
        if re.search(re.compile(r"\bflow\w* control\w* dev\w*"), text):
            return True
        if re.search(re.compile(r"\bfluid commun\w*"), text):
            return True
        if re.search(re.compile(r"\bhigh purit\w*"), text):
            return True
        if re.search(re.compile(r"\bimpur\w*"), text):
            return True
        if re.search(re.compile(r"\bzeolit\w*"), text):
            return True
    return False
    
def pattern11_Environmental_Recovery_recycling(text):
    if re.search(re.compile(r"\brecycl\w*"), text):
        return True
    if re.search(re.compile(r"\bcompost\w*"), text):
        return True
    if re.search(re.compile(r"\bstock process\w*"), text):
        return True
    if re.search(re.compile(r"\bcoal combust\w*"), text):
        return True
    if re.search(re.compile(r"\bremanufactur\w*"), text):
        return True
    if re.search(re.compile(r"\bcoal"), text) and re.search(re.compile(r"\bPCC"), text):
        return True
    if re.search(re.compile(r"\bcirculat\w* fluid\w* bed combust\w*"), text):
        return True
    if re.search(re.compile(r"\bcombust\w*"), text) and re.search(re.compile(r"\bCFBC"), text):
        return True
    return False
