"""
Patterns for identifying green technologies in text descriptions such as patent abstracts. 
Follows Shapira et al. (2014) p.102 http://dx.doi.org/10.1016/j.techfore.2013.10.023
"""

import re

def pattern01_general(text):
    if re.search(re.compile(r"\bsustainab\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgreen good\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgreen technolog\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgreen innov\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\beco\w*innov\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgreen manufac\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgreen prod\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bpollut\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\becolabel\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benviron\w* product declarat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bEPD\b"), text) and re.search(re.compile(r"\benviron\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benviron\w* prefer\w* product\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benviron\w* label\w*\b", flags=re.I), text):
        return True
    return False
    
def pattern02_Environmental_All_purpose(text):
    if re.search(re.compile(r"\bnatur\w* environ\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benviron\w* friend\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benvironment\w* conserv\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bbiocompat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bbiodivers\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bfilter\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bfiltra\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bsynth\w* gas\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bregenerat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\brecircul\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgasification\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgasifier\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bfluidized clean gas\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgas cleaning\b", flags=re.I), text):
        return True
    return False

def pattern03_Environmental_Biological_treatment(text):
    if re.search(re.compile(r"\bbioremed\w*\b", flags=re.I), text) or re.search(re.compile(r"\bbiorecov\w*\b", flags=re.I), text) or \
       re.search(re.compile(r"\bbiolog\w* treat\w*\b", flags=re.I), text) or re.search(re.compile(r"\bbiodegrad\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\bbiogas\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bbioreact\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bpolyolef\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bbiopolymer\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bdisinfect\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bbiofilm\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bbiosens\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bbiosolid\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bcaprolact\w*\b", flags=re.I), text):
            return True
        if (re.search(re.compile(r"\bultraviol\w*\b", flags=re.I), text) or re.search(re.compile(r"\bUV\b"), text)) and \
                 (re.search(re.compile(r"\bradiat\w*\b", flags=re.I), text) or re.search(re.compile(r"\bsol\w*\b", flags=re.I), text)):
            return True
    return False

def pattern04_Environmental_Air_pollution(text):
    if re.search(re.compile(r"\bpollut\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\bair\w* contr\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bdust\w* contr\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bparticular\w* contr\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bair\w* qual\w*\b", flags=re.I), text):
            return True
    return False
        
def pattern05_Environmental_Environmental_monitoring(text):
    if re.search(re.compile(r"\benviron\w* monitor\w*\b", flags=re.I), text):
        if (re.search(re.compile(r"\benviron\w*\b", flags=re.I), text) and re.search(re.compile(r"\binstrument\w*\b", flags=re.I), text)) or \
            (re.search(re.compile(r"\benviron\w*\b", flags=re.I), text) and re.search(re.compile(r"\banalys\w*\b", flags=re.I), text)):
            # note that including keyword "environ" here is unneccessary, because this is implied by the first condition
            return True
        if re.search(re.compile(r"\blife\w*cycle analysis\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\blife cycle analys\w*\b", flags=re.I), text):
            return True
    return False

def pattern06_Environmental_Marine_pollution(text):
    if re.search(re.compile(r"\bmarin\w* control\w*\b", flags=re.I), text) and re.search(re.compile(r"\bpollut\w*\b", flags=re.I), text):
        return True
    return False
    
def pattern07_Environmental_Noise_vibration(text):
    if re.search(re.compile(r"\bnois\w* abat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnois\w* reduc\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnois\w* lessen\w*\b", flags=re.I), text):
        return True
    return False

def pattern08_Environmental_Contaminated_land(text):
    if re.search(re.compile(r"\bland\b", flags=re.I), text):
        if re.search(re.compile(r"\breclam\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bremediat\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bcontamin\w*\b", flags=re.I), text):
            return True
    return False
        
def pattern09_Environmental_Waste_management(text):
    if re.search(re.compile(r"\bwast\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bsewag\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\binciner\w*\b", flags=re.I), text):
        return True
    return False
    
def pattern10_Environmental_Water_supply(text):
    if re.search(re.compile(r"\bwater treat\w*\b", flags=re.I), text) or re.search(re.compile(r"\bwater purif\w*\b", flags=re.I), text) or \
                                                            re.search(re.compile(r"\bwater pollut\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\bslurr\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bsludg\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\baque\w* solution\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bwastewat\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\beffluent\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bsediment\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bfloccul\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bdetergen\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bcoagul\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bdioxin\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bflow\w* control\w* dev\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bfluid commun\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bhigh purit\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bimpur\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bzeolit\w*\b", flags=re.I), text):
            return True
    return False
    
def pattern11_Environmental_Recovery_recycling(text):
    if re.search(re.compile(r"\brecycl\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcompost\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bstock process\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcoal combust\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bremanufactur\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcoal\b", flags=re.I), text) and re.search(re.compile(r"\bPCC\b"), text):
        return True
    if re.search(re.compile(r"\bcirculat\w* fluid\w* bed combust\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcombust\w*\b", flags=re.I), text) and re.search(re.compile(r"\bCFBC\b"), text):
        return True
    return False

def pattern12_Renewable_All_purpose(text):
    if re.search(re.compile(r"\brenewabl\w*\b", flags=re.I), text) and \
                         (re.search(re.compile(r"\benerg\w*\b", flags=re.I), text) or re.search(re.compile(r"\belectric\w*\b", flags=re.I), text)):
        return True
    return False
    
def pattern13_Renewable_Wave_tidal(text):
    if re.search(re.compile(r"\belectric\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\btwo basin schem\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bwave\w* energ\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\btid\w* energ\w*\b", flags=re.I), text):
            return True
    return False

def pattern14_Renewable_Biomass(text):
    if re.search(re.compile(r"\bbiomass\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benzymat\w* hydrolys\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bbio\w*bas\w* product\w*\b", flags=re.I), text):
        return True
    return False
    
def pattern15_Renewable_Wind(text):
    if re.search(re.compile(r"\bwind power\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bwind energ\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bwind farm\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bturbin\w*\b", flags=re.I), text) and re.search(re.compile(r"\bwind\w*\b", flags=re.I), text):
        return True
    return False

def pattern16_Renewable_Geothermal(text):
    if re.search(re.compile(r"\bwhole system\w*\b", flags=re.I), text) and re.search(re.compile(r"\bgeotherm\w*\b", flags=re.I), text):     # subset of next one below
        return True
    if re.search(re.compile(r"\bgeotherm\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bgeoexchang\w*\b", flags=re.I), text):
        return True
    return False

def pattern17_Renewable_PV_solar(text):
    if re.search(re.compile(r"\bsolar\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\bener\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\blinear fresnel sys\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\belectric\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bcell\w*\b", flags=re.I), text):                   # seems too broad, instead: "solar cell"?
            return True
        if re.search(re.compile(r"\bheat\w*\b", flags=re.I), text):                   # seems too broad
            return True
        if re.search(re.compile(r"\bcool\w*\b", flags=re.I), text):                   # seems too broad
            return True
        if re.search(re.compile(r"\bphotovolt\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bPV\b"), text):                                    # maybe too broad?
            return True
        if re.search(re.compile(r"\bcdte\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bcadmium tellurid\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bPVC-U\b"), text):
            return True
        if re.search(re.compile(r"\bphotoelectr\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bphotoactiv\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bsol\w*gel\w* process\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bevacuat\w* tub\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bflat plate collect\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\broof integr\w* system\w*\b", flags=re.I), text):
            return True
    return False

def pattern18_LowCarb_All_purpose(text):
    if re.search(re.compile(r"\blow carbon\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bzero carbon\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bno carbon\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\b0 carbon\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\blow\w*carbon\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bzero\w*carbon\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bno\w*carbon\b", flags=re.I), text):
        return True
    return False

def pattern19_LowCarb_Alt_fuel_vehicle(text):
    if re.search(re.compile(r"\belectric\w* vehic\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bhybrid vehic\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\belectric\w* motor\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bhybrid motor\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bhybrid driv\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\belectric\w* car\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bhybrid car\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\belectric\w* machin\w*\b", flags=re.I), text):         #seems too broad
        return True
    if re.search(re.compile(r"\belectric\w* auto\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bhybrid auto\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\byaw\w* rat\w* sens\w*\b", flags=re.I), text):
        return True
    return False
    
def pattern20_LowCarb_Alt_fuels(text):
    if re.search(re.compile(r"\balternat\w* fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bmainstream\w* fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bfuel cell\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnuclear powe\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnuclear stat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnuclear plant\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnuclear energ\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnuclear\b", flags=re.I), text) and re.search(re.compile(r"\belectric\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bnuclear fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bfuel\w* process\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bporous\w* struct\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bporous\w* substrat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bsolid\w* oxid\w* fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bFischer\w*Tropsch\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\brefus\w* deriv\w* fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\brefus\w*deriv\w* fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bfuel\b", flags=re.I), text) and re.search(re.compile(r"\bbiotech\w*\b", flags=re.I), text) and \
        (re.search(re.compile(r"\bethanol\b", flags=re.I), text) or re.search(re.compile(r"\bhydrogen\w*\b", flags=re.I), text)):
        return True
    if re.search(re.compile(r"\bbio\w*fuel\w*\b", flags=re.I), text):                     # subset of previous one above
        return True
    if re.search(re.compile(r"\bsynthetic fuel\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcombined heat and power\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bsynth\w* gas\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bsyngas\b", flags=re.I), text):
        return True
    return False

def pattern21_LowCarb_Electrochemical_processes(text):
    if re.search(re.compile(r"\belectrochem\w* cell\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\belectrochem\w* fuel\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bmembran\w* electrod\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bion\w* exchang\w* membran\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bion\w*exchang\w* membran\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\belectrolyt\w* cell\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcatalyt\w* convers\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bsolid\w* separat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bmembran\w* separat\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bion\w* exchang\w* resin\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bion\w*exchang\w* resin\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bproton\w* exchang\w* membra\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bproton\w*exchang\w* membra\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcataly\w* reduc\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\belectrod\w* membra\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\btherm\w* engin\w*\b", flags=re.I), text):
        return True
    return False

def pattern22_LowCarb_Battery(text):
    if re.search(re.compile(r"\bbatter\w*\b", flags=re.I), text) or re.search(re.compile(r"\baccumul\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\bcharg\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\brechar\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bturbocharg\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bhigh capacit\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\brapid charg\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\blong life\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bultra\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bsolar\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bno lead\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bno mercury\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bno cadmium\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\blithium\w*ion\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\blithium\w* ion\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bLi\w*ion\w*\b"), text):
            return True
    return False

def pattern23_LowCarb_Additional_energy(text):
    if re.search(re.compile(r"\baddition\w* energ\w* sourc\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\baddition\w* sourc\w* of energ\w*\b", flags=re.I), text):
        return True
    return False

def pattern24_LowCarb_Carbon_capture_storage(text):
    if re.search(re.compile(r"\bcarbon\b", flags=re.I), text) and re.search(re.compile(r"\bcaptu\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcarbon\b", flags=re.I), text) and re.search(re.compile(r"\bstor\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bcarbon dioxid\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bCO2\b"), text):
        return True
    return False

def pattern25_LowCarb_Energy_management(text):
    if re.search(re.compile(r"\bener\w* sav\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bener\w* effic\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benerg\w*effic\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benerg\w*sav\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\blight\w* emit\w* diod\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\bLED\b"), text):
        return True
    if re.search(re.compile(r"\borganic LED\b"), text):
        return True
    if re.search(re.compile(r"\bOrganic LED\b"), text):
        return True
    if re.search(re.compile(r"\bOLED\b"), text):
        return True
    if re.search(re.compile(r"\bCFL\b"), text):
        return True
    if re.search(re.compile(r"\bcompact fluorescent\w*\b", flags=re.I), text):
        return True
    if re.search(re.compile(r"\benerg\w* conserve\w*\b", flags=re.I), text):
        return True
    return False

def pattern26_LowCarb_Building_technologies(text):
    if re.search(re.compile(r"\bbuild\w*\b", flags=re.I), text) or re.search(re.compile(r"\bconstruct\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\binsula\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bheat\w* retent\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bheat\w* exchang\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bheat\w* pump\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\btherm\w* exchang\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\btherm\w* decompos\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\btherm\w* energ\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\btherm\w* communic\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bthermoplast\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bthermocoup\w*\b", flags=re.I), text):
            return True
        if re.search(re.compile(r"\bheat\w* recover\w*\b", flags=re.I), text):
            return True
    return False
