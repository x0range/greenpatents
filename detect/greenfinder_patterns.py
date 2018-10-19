"""
Patterns for identifying green technologies in text descriptions such as patent abstracts. 
Follows Shapira et al. (2014) p.102 http://dx.doi.org/10.1016/j.techfore.2013.10.023
"""

import re

def pattern01_general(text):
    if re.search(re.compile(r"\bsustainab\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgreen good\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgreen technolog\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgreen innov\w*\b"), text):
        return True
    if re.search(re.compile(r"\beco\w*innov\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgreen manufac\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgreen prod\w*\b"), text):
        return True
    if re.search(re.compile(r"\bpollut\w*\b"), text):
        return True
    if re.search(re.compile(r"\becolabel\b"), text):
        return True
    if re.search(re.compile(r"\benviron\w* product declarat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bEPD\b"), text) and re.search(re.compile(r"\benviron\w*\b"), text):
        return True
    if re.search(re.compile(r"\benviron\w* prefer\w* product\w*\b"), text):
        return True
    if re.search(re.compile(r"\benviron\w* label\w*\b"), text):
        return True
    return False
    
def pattern02_Environmental_All_purpose(text):
    if re.search(re.compile(r"\bnatur\w* environ\w*\b"), text):
        return True
    if re.search(re.compile(r"\benviron\w* friend\w*\b"), text):
        return True
    if re.search(re.compile(r"\benvironment\w* conserv\w*\b"), text):
        return True
    if re.search(re.compile(r"\bbiocompat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bbiodivers\w*\b"), text):
        return True
    if re.search(re.compile(r"\bfilter\w*\b"), text):
        return True
    if re.search(re.compile(r"\bfiltra\w*\b"), text):
        return True
    if re.search(re.compile(r"\bsynth\w* gas\w*\b"), text):
        return True
    if re.search(re.compile(r"\bregenerat\w*\b"), text):
        return True
    if re.search(re.compile(r"\brecircul\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgasification\b"), text):
        return True
    if re.search(re.compile(r"\bgasifier\b"), text):
        return True
    if re.search(re.compile(r"\bfluidized clean gas\b"), text):
        return True
    if re.search(re.compile(r"\bgas cleaning\b"), text):
        return True
    return False

def pattern03_Environmental_Biological_treatment(text):
    if re.search(re.compile(r"\bbioremed\w*\b"), text) or re.search(re.compile(r"\bbiorecov\w*\b"), text) or \
       re.search(re.compile(r"\bbiolog\w* treat\w*\b"), text) or re.search(re.compile(r"\bbiodegrad\w*\b"), text):
        if re.search(re.compile(r"\bbiogas\w*\b"), text):
            return True
        if re.search(re.compile(r"\bbioreact\w*\b"), text):
            return True
        if re.search(re.compile(r"\bpolyolef\w*\b"), text):
            return True
        if re.search(re.compile(r"\bbiopolymer\w*\b"), text):
            return True
        if re.search(re.compile(r"\bdisinfect\w*\b"), text):
            return True
        if re.search(re.compile(r"\bbiofilm\w*\b"), text):
            return True
        if re.search(re.compile(r"\bbiosens\w*\b"), text):
            return True
        if re.search(re.compile(r"\bbiosolid\w*\b"), text):
            return True
        if re.search(re.compile(r"\bcaprolact\w*\b"), text):
            return True
        if (re.search(re.compile(r"\bultraviol\w*\b"), text) or re.search(re.compile(r"\bUV\b"), text)) and \
                 (re.search(re.compile(r"\bradiat\w*\b"), text) or re.search(re.compile(r"\bsol\w*\b"), text)):
            return True
    return False

def pattern04_Environmental_Air_pollution(text):
    if re.search(re.compile(r"\bpollut\w*\b"), text):
        if re.search(re.compile(r"\bair\w* contr\w*\b"), text):
            return True
        if re.search(re.compile(r"\bdust\w* contr\w*\b"), text):
            return True
        if re.search(re.compile(r"\bparticular\w* contr\w*\b"), text):
            return True
        if re.search(re.compile(r"\bair\w* qual\w*\b"), text):
            return True
    return False
        
def pattern05_Environmental_Environmental_monitoring(text):
    if re.search(re.compile(r"\benviron\w* monitor\w*\b"), text):
        if (re.search(re.compile(r"\benviron\w*\b"), text) and re.search(re.compile(r"\binstrument\w*\b"), text)) or \
            (re.search(re.compile(r"\benviron\w*\b"), text) and re.search(re.compile(r"\banalys\w*\b"), text)):
            # note that including keyword "environ" here is unneccessary, because this is implied by the first condition
            return True
        if re.search(re.compile(r"\blife\w*cycle analysis\b"), text):
            return True
        if re.search(re.compile(r"\blife cycle analys\w*\b"), text):
            return True
    return False

def pattern06_Environmental_Marine_pollution(text):
    if re.search(re.compile(r"\bmarin\w* control\w*\b"), text) and re.search(re.compile(r"\bpollut\w*\b"), text):
        return True
    return False
    
def pattern07_Environmental_Noise_vibration(text):
    if re.search(re.compile(r"\bnois\w* abat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnois\w* reduc\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnois\w* lessen\w*\b"), text):
        return True
    return False

def pattern08_Environmental_Contaminated_land(text):
    if re.search(re.compile(r"\bland\b"), text):
        if re.search(re.compile(r"\breclam\w*\b"), text):
            return True
        if re.search(re.compile(r"\bremediat\w*\b"), text):
            return True
        if re.search(re.compile(r"\bcontamin\w*\b"), text):
            return True
    return False
        
def pattern09_Environmental_Waste_management(text):
    if re.search(re.compile(r"\bwast\w*\b"), text):
        return True
    if re.search(re.compile(r"\bsewag\w*\b"), text):
        return True
    if re.search(re.compile(r"\binciner\w*\b"), text):
        return True
    return False
    
def pattern10_Environmental_Water_supply(text):
    if re.search(re.compile(r"\bwater treat\w*\b"), text) or re.search(re.compile(r"\bwater purif\w*\b"), text) or \
                                                            re.search(re.compile(r"\bwater pollut\w*\b"), text):
        if re.search(re.compile(r"\bslurr\w*\b"), text):
            return True
        if re.search(re.compile(r"\bsludg\w*\b"), text):
            return True
        if re.search(re.compile(r"\baque\w* solution\w*\b"), text):
            return True
        if re.search(re.compile(r"\bwastewat\w*\b"), text):
            return True
        if re.search(re.compile(r"\beffluent\w*\b"), text):
            return True
        if re.search(re.compile(r"\bsediment\w*\b"), text):
            return True
        if re.search(re.compile(r"\bfloccul\w*\b"), text):
            return True
        if re.search(re.compile(r"\bdetergen\w*\b"), text):
            return True
        if re.search(re.compile(r"\bcoagul\w*\b"), text):
            return True
        if re.search(re.compile(r"\bdioxin\w*\b"), text):
            return True
        if re.search(re.compile(r"\bflow\w* control\w* dev\w*\b"), text):
            return True
        if re.search(re.compile(r"\bfluid commun\w*\b"), text):
            return True
        if re.search(re.compile(r"\bhigh purit\w*\b"), text):
            return True
        if re.search(re.compile(r"\bimpur\w*\b"), text):
            return True
        if re.search(re.compile(r"\bzeolit\w*\b"), text):
            return True
    return False
    
def pattern11_Environmental_Recovery_recycling(text):
    if re.search(re.compile(r"\brecycl\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcompost\w*\b"), text):
        return True
    if re.search(re.compile(r"\bstock process\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcoal combust\w*\b"), text):
        return True
    if re.search(re.compile(r"\bremanufactur\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcoal\b"), text) and re.search(re.compile(r"\bPCC\b"), text):
        return True
    if re.search(re.compile(r"\bcirculat\w* fluid\w* bed combust\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcombust\w*\b"), text) and re.search(re.compile(r"\bCFBC\b"), text):
        return True
    return False

def pattern12_Renewable_All_purpose(text):
    if re.search(re.compile(r"\brenewabl\w*\b"), text) and \
                         (re.search(re.compile(r"\benerg\w*\b"), text) or re.search(re.compile(r"\belectric\w*\b"), text)):
        return True
    return False
    
def pattern13_Renewable_Wave_tidal(text):
    if re.search(re.compile(r"\belectric\w*\b"), text):
        if re.search(re.compile(r"\btwo basin schem\w*\b"), text):
            return True
        if re.search(re.compile(r"\bwave\w* energ\w*\b"), text):
            return True
        if re.search(re.compile(r"\btid\w* energ\w*\b"), text):
            return True
    return False

def pattern14_Renewable_Biomass(text):
    if re.search(re.compile(r"\bbiomass\w*\b"), text):
        return True
    if re.search(re.compile(r"\benzymat\w* hydrolys\w*\b"), text):
        return True
    if re.search(re.compile(r"\bbio\w*bas\w* product\w*\b"), text):
        return True
    return False
    
def pattern15_Renewable_Wind(text):
    if re.search(re.compile(r"\bwind power\w*\b"), text):
        return True
    if re.search(re.compile(r"\bwind energ\w*\b"), text):
        return True
    if re.search(re.compile(r"\bwind farm\w*\b"), text):
        return True
    if re.search(re.compile(r"\bturbin\w*\b"), text) and re.search(re.compile(r"\bwind\w*\b"), text):
        return True
    return False

def pattern16_Renewable_Geothermal(text):
    if re.search(re.compile(r"\bwhole system\w*\b"), text) and re.search(re.compile(r"\bgeotherm\w*\b"), text):     # subset of next one below
        return True
    if re.search(re.compile(r"\bgeotherm\w*\b"), text):
        return True
    if re.search(re.compile(r"\bgeoexchang\w*\b"), text):
        return True
    return False

def pattern17_Renewable_PV_solar(text):
    if re.search(re.compile(r"\bsolar\w*\b"), text):
        if re.search(re.compile(r"\bener\w*\b"), text):
            return True
        if re.search(re.compile(r"\blinear fresnel sys\w*\b"), text):
            return True
        if re.search(re.compile(r"\belectric\w*\b"), text):
            return True
        if re.search(re.compile(r"\bcell\w*\b"), text):                   # seems too broad, instead: "solar cell"?
            return True
        if re.search(re.compile(r"\bheat\w*\b"), text):                   # seems too broad
            return True
        if re.search(re.compile(r"\bcool\w*\b"), text):                   # seems too broad
            return True
        if re.search(re.compile(r"\bphotovolt\w*\b"), text):
            return True
        if re.search(re.compile(r"\bPV\b"), text):                        #maybe too broad?       ### 
            return True
        if re.search(re.compile(r"\bcdte\b"), text):
            return True
        if re.search(re.compile(r"\bcadmium tellurid\w*\b"), text):
            return True
        if re.search(re.compile(r"\bPVC-U\b"), text):                     ###
            return True
        if re.search(re.compile(r"\bphotoelectr\w*\b"), text):
            return True
        if re.search(re.compile(r"\bphotoactiv\w*\b"), text):
            return True
        if re.search(re.compile(r"\bsol\w*gel\w* process\w*\b"), text):
            return True
        if re.search(re.compile(r"\bevacuat\w* tub\w*\b"), text):
            return True
        if re.search(re.compile(r"\bflat plate collect\w*\b"), text):
            return True
        if re.search(re.compile(r"\broof integr\w* system\w*\b"), text):
            return True
    return False

def pattern18_LowCarb_All_purpose(text):
    if re.search(re.compile(r"\blow carbon\b"), text):
        return True
    if re.search(re.compile(r"\bzero carbon\b"), text):
        return True
    if re.search(re.compile(r"\bno carbon\b"), text):
        return True
    if re.search(re.compile(r"\b0 carbon\b"), text):
        return True
    if re.search(re.compile(r"\blow\w*carbon\b"), text):
        return True
    if re.search(re.compile(r"\bzero\w*carbon\b"), text):
        return True
    if re.search(re.compile(r"\bno\w*carbon\b"), text):
        return True
    return False

def pattern19_LowCarb_Alt_fuel_vehicle(text):
    if re.search(re.compile(r"\belectric\w* vehic\w*\b"), text):
        return True
    if re.search(re.compile(r"\bhybrid vehic\w*\b"), text):
        return True
    if re.search(re.compile(r"\belectric\w* motor\w*\b"), text):
        return True
    if re.search(re.compile(r"\bhybrid motor\w*\b"), text):
        return True
    if re.search(re.compile(r"\bhybrid driv\w*\b"), text):
        return True
    if re.search(re.compile(r"\belectric\w* car\w*\b"), text):
        return True
    if re.search(re.compile(r"\bhybrid car\w*\b"), text):
        return True
    if re.search(re.compile(r"\belectric\w* machin\w*\b"), text):         #seems too broad
        return True
    if re.search(re.compile(r"\belectric\w* auto\w*\b"), text):
        return True
    if re.search(re.compile(r"\bhybrid auto\w*\b"), text):
        return True
    if re.search(re.compile(r"\byaw\w* rat\w* sens\w*\b"), text):
        return True
    return False
    
def pattern20_LowCarb_Alt_fuels(text):
    if re.search(re.compile(r"\balternat\w* fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\bmainstream\w* fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\bfuel cell\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnuclear powe\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnuclear stat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnuclear plant\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnuclear energ\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnuclear\b"), text) and re.search(re.compile(r"\belectric\w*\b"), text):
        return True
    if re.search(re.compile(r"\bnuclear fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\bfuel\w* process\w*\b"), text):
        return True
    if re.search(re.compile(r"\bporous\w* struct\w*\b"), text):
        return True
    if re.search(re.compile(r"\bporous\w* substrat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bsolid\w* oxid\w* fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\bFischer\w*Tropsch\w*\b"), text):
        return True
    if re.search(re.compile(r"\brefus\w* deriv\w* fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\brefus\w*deriv\w* fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\bfuel\b"), text) and re.search(re.compile(r"\bbiotech\w*\b"), text) and \
        (re.search(re.compile(r"\bethanol\b"), text) or re.search(re.compile(r"\bhydrogen\w*\b"), text)):
        return True
    if re.search(re.compile(r"\bbio\w*fuel\w*\b"), text):                     # subset of previous one above
        return True
    if re.search(re.compile(r"\bsynthetic fuel\b"), text):
        return True
    if re.search(re.compile(r"\bcombined heat and power\b"), text):
        return True
    if re.search(re.compile(r"\bsynth\w* gas\w*\b"), text):
        return True
    if re.search(re.compile(r"\bsyngas\b"), text):
        return True
    return False

def pattern21_LowCarb_Electrochemical_processes(text):
    if re.search(re.compile(r"\belectrochem\w* cell\w*\b"), text):
        return True
    if re.search(re.compile(r"\belectrochem\w* fuel\w*\b"), text):
        return True
    if re.search(re.compile(r"\bmembran\w* electrod\w*\b"), text):
        return True
    if re.search(re.compile(r"\bion\w* exchang\w* membran\w*\b"), text):
        return True
    if re.search(re.compile(r"\bion\w*exchang\w* membran\w*\b"), text):
        return True
    if re.search(re.compile(r"\belectrolyt\w* cell\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcatalyt\w* convers\w*\b"), text):
        return True
    if re.search(re.compile(r"\bsolid\w* separat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bmembran\w* separat\w*\b"), text):
        return True
    if re.search(re.compile(r"\bion\w* exchang\w* resin\w*\b"), text):
        return True
    if re.search(re.compile(r"\bion\w*exchang\w* resin\w*\b"), text):
        return True
    if re.search(re.compile(r"\bproton\w* exchang\w* membra\w*\b"), text):
        return True
    if re.search(re.compile(r"\bproton\w*exchang\w* membra\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcataly\w* reduc\w*\b"), text):
        return True
    if re.search(re.compile(r"\belectrod\w* membra\w*\b"), text):
        return True
    if re.search(re.compile(r"\btherm\w* engin\w*\b"), text):
        return True
    return False

def pattern22_LowCarb_Battery(text):
    if re.search(re.compile(r"\bbatter\w*\b"), text) or re.search(re.compile(r"\baccumul\w*\b"), text):
        if re.search(re.compile(r"\bcharg\w*\b"), text):
            return True
        if re.search(re.compile(r"\brechar\w*\b"), text):
            return True
        if re.search(re.compile(r"\bturbocharg\w*\b"), text):
            return True
        if re.search(re.compile(r"\bhigh capacit\w*\b"), text):
            return True
        if re.search(re.compile(r"\brapid charg\w*\b"), text):
            return True
        if re.search(re.compile(r"\blong life\b"), text):
            return True
        if re.search(re.compile(r"\bultra\w*\b"), text):
            return True
        if re.search(re.compile(r"\bsolar\b"), text):
            return True
        if re.search(re.compile(r"\bno lead\b"), text):
            return True
        if re.search(re.compile(r"\bno mercury\b"), text):
            return True
        if re.search(re.compile(r"\bno cadmium\b"), text):
            return True
        if re.search(re.compile(r"\blithium\w*ion\w*\b"), text):
            return True
        if re.search(re.compile(r"\blithium\w* ion\w*\b"), text):
            return True
        if re.search(re.compile(r"\bLi\w*ion\w*\b"), text):               ###
            return True
    return False

def pattern23_LowCarb_Additional_energy(text):
    if re.search(re.compile(r"\baddition\w* energ\w* sourc\w*\b"), text):
        return True
    if re.search(re.compile(r"\baddition\w* sourc\w* of energ\w*\b"), text):
        return True
    return False

def pattern24_LowCarb_Carbon_capture_storage(text):
    if re.search(re.compile(r"\bcarbon\b"), text) and re.search(re.compile(r"\bcaptu\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcarbon\b"), text) and re.search(re.compile(r"\bstor\w*\b"), text):
        return True
    if re.search(re.compile(r"\bcarbon dioxid\w*\b"), text):
        return True
    if re.search(re.compile(r"\bCO2\b"), text):
        return True
    return False

def pattern25_LowCarb_Energy_management(text):
    if re.search(re.compile(r"\bener\w* sav\w*\b"), text):
        return True
    if re.search(re.compile(r"\bener\w* effic\w*\b"), text):
        return True
    if re.search(re.compile(r"\benerg\w*effic\w*\b"), text):
        return True
    if re.search(re.compile(r"\benerg\w*sav\w*\b"), text):
        return True
    if re.search(re.compile(r"\blight\w* emit\w* diod\w*\b"), text):
        return True
    if re.search(re.compile(r"\bLED\b"), text):
        return True
    if re.search(re.compile(r"\borganic LED\b"), text):
        return True
    if re.search(re.compile(r"\bOLED\b"), text):
        return True
    if re.search(re.compile(r"\bCFL\b"), text):
        return True
    if re.search(re.compile(r"\bcompact fluorescent\w*\b"), text):
        return True
    if re.search(re.compile(r"\benerg\w* conserve\w*\b"), text):
        return True
    return False

def pattern26_LowCarb_Building_technologies(text):
    if re.search(re.compile(r"\bbuild\w*\b"), text) or re.search(re.compile(r"\bconstruct\w*\b"), text):
        if re.search(re.compile(r"\binsula\w*\b"), text):
            return True
        if re.search(re.compile(r"\bheat\w* retent\w*\b"), text):
            return True
        if re.search(re.compile(r"\bheat\w* exchang\w*\b"), text):
            return True
        if re.search(re.compile(r"\bheat\w* pump\w*\b"), text):
            return True
        if re.search(re.compile(r"\btherm\w* exchang\w*\b"), text):
            return True
        if re.search(re.compile(r"\btherm\w* decompos\w*\b"), text):
            return True
        if re.search(re.compile(r"\btherm\w* energ\w*\b"), text):
            return True
        if re.search(re.compile(r"\btherm\w* communic\w*\b"), text):
            return True
        if re.search(re.compile(r"\bthermoplast\w*\b"), text):
            return True
        if re.search(re.compile(r"\bthermocoup\w*\b"), text):
            return True
        if re.search(re.compile(r"\bheat\w* recover\w*\b"), text):
            return True
    return False
