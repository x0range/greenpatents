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

def pattern12_Renewable_All_purpose(text):
    if re.search(re.compile(r"\brenewabl\w*"), text) and \
                         (re.search(re.compile(r"\benerg\w*"), text) or re.search(re.compile(r"\belectric\w*"), text)):
        return True
    return False
    
def pattern13_Renewable_Wave_tidal(text):
    if re.search(re.compile(r"\belectric\w*"), text):
        if re.search(re.compile(r"\btwo basin schem\w*"), text):
            return True
        if re.search(re.compile(r"\bwave\w* energ\w*"), text):
            return True
        if re.search(re.compile(r"\btid\w* energ\w*"), text):
            return True
    return False

def pattern14_Renewable_Biomass(text):
    if re.search(re.compile(r"\bbiomass\w*"), text):
        return True
    if re.search(re.compile(r"\benzymat\w* hydrolys\w*"), text):
        return True
    if re.search(re.compile(r"\bbio\w*bas\w* product\w*"), text):
        return True
    return False
    
def pattern15_Renewable_Wind(text):
    if re.search(re.compile(r"\bwind power\w*"), text):
        return True
    if re.search(re.compile(r"\bwind energ\w*"), text):
        return True
    if re.search(re.compile(r"\bwind farm\w*"), text):
        return True
    if re.search(re.compile(r"\bturbin\w*"), text) and re.search(re.compile(r"\bwind\w*"), text):
        return True
    return False

def pattern16_Renewable_Geothermal(text):
    if re.search(re.compile(r"\bwhole system\w*"), text) and re.search(re.compile(r"\bgeotherm\w*"), text):     # subset of next one below
        return True
    if re.search(re.compile(r"\bgeotherm\w*"), text):
        return True
    if re.search(re.compile(r"\bgeoexchang\w*"), text):
        return True
    return False

def pattern17_Renewable_PV_solar(text):
    if re.search(re.compile(r"\bsolar\w*"), text):
        if re.search(re.compile(r"\bener\w*"), text):
            return True
        if re.search(re.compile(r"\blinear fresnel sys\w*"), text):
            return True
        if re.search(re.compile(r"\belectric\w*"), text):
            return True
        if re.search(re.compile(r"\bcell\w*"), text):                   # seems too broad, instead: "solar cell"?
            return True
        if re.search(re.compile(r"\bheat\w*"), text):                   # seems too broad
            return True
        if re.search(re.compile(r"\bcool\w*"), text):                   # seems too broad
            return True
        if re.search(re.compile(r"\bphotovolt\w*"), text):
            return True
        if re.search(re.compile(r"\bPV"), text):                        #maybe too broad?       ### 
            return True
        if re.search(re.compile(r"\bcdte"), text):
            return True
        if re.search(re.compile(r"\bcadmium tellurid\w*"), text):
            return True
        if re.search(re.compile(r"\bPVC-U"), text):                     ###
            return True
        if re.search(re.compile(r"\bphotoelectr\w*"), text):
            return True
        if re.search(re.compile(r"\bphotoactiv\w*"), text):
            return True
        if re.search(re.compile(r"\bsol\w*gel\w* process\w*"), text):
            return True
        if re.search(re.compile(r"\bevacuat\w* tub\w*"), text):
            return True
        if re.search(re.compile(r"\bflat plate collect\w*"), text):
            return True
        if re.search(re.compile(r"\broof integr\w* system\w*"), text):
            return True
    return False

def pattern18_LowCarb_All_purpose(text):
    if re.search(re.compile(r"\blow carbon"), text):
        return True
    if re.search(re.compile(r"\bzero carbon"), text):
        return True
    if re.search(re.compile(r"\bno carbon"), text):
        return True
    if re.search(re.compile(r"\b0 carbon"), text):
        return True
    if re.search(re.compile(r"\blow\w*carbon"), text):
        return True
    if re.search(re.compile(r"\bzero\w*carbon"), text):
        return True
    if re.search(re.compile(r"\bno\w*carbon"), text):
        return True
    return False

def pattern19_LowCarb_Alt_fuel_vehicle(text):
    if re.search(re.compile(r"\belectric\w* vehic\w*"), text):
        return True
    if re.search(re.compile(r"\bhybrid vehic\w*"), text):
        return True
    if re.search(re.compile(r"\belectric\w* motor\w*"), text):
        return True
    if re.search(re.compile(r"\bhybrid motor\w*"), text):
        return True
    if re.search(re.compile(r"\bhybrid driv\w*"), text):
        return True
    if re.search(re.compile(r"\belectric\w* car\w*"), text):
        return True
    if re.search(re.compile(r"\bhybrid car\w*"), text):
        return True
    if re.search(re.compile(r"\belectric\w* machin\w*"), text):         #seems too broad
        return True
    if re.search(re.compile(r"\belectric\w* auto\w*"), text):
        return True
    if re.search(re.compile(r"\bhybrid auto\w*"), text):
        return True
    if re.search(re.compile(r"\byaw\w* rat\w* sens\w*"), text):
        return True
    return False
    
def pattern20_LowCarb_Alt_fuels(text):
    if re.search(re.compile(r"\balternat\w* fuel\w*"), text):
        return True
    if re.search(re.compile(r"\bmainstream\w* fuel\w*"), text):
        return True
    if re.search(re.compile(r"\bfuel cell\w*"), text):
        return True
    if re.search(re.compile(r"\bnuclear powe\w*"), text):
        return True
    if re.search(re.compile(r"\bnuclear stat\w*"), text):
        return True
    if re.search(re.compile(r"\bnuclear plant\w*"), text):
        return True
    if re.search(re.compile(r"\bnuclear energ\w*"), text):
        return True
    if re.search(re.compile(r"\bnuclear"), text) and re.search(re.compile(r"\belectric\w*"), text):
        return True
    if re.search(re.compile(r"\bnuclear fuel\w*"), text):
        return True
    if re.search(re.compile(r"\bfuel\w* process\w*"), text):
        return True
    if re.search(re.compile(r"\bporous\w* struct\w*"), text):
        return True
    if re.search(re.compile(r"\bporous\w* substrat\w*"), text):
        return True
    if re.search(re.compile(r"\bsolid\w* oxid\w* fuel\w*"), text):
        return True
    if re.search(re.compile(r"\bFischer\w*Tropsch\w*"), text):
        return True
    if re.search(re.compile(r"\brefus\w* deriv\w* fuel\w*"), text):
        return True
    if re.search(re.compile(r"\brefus\w*deriv\w* fuel\w*"), text):
        return True
    if re.search(re.compile(r"\bfuel"), text) and re.search(re.compile(r"\bbiotech\w*"), text) and \
        (re.search(re.compile(r"\bethanol"), text) or re.search(re.compile(r"\bhydrogen\w*"), text)):
        return True
    if re.search(re.compile(r"\bbio\w*fuel\w*"), text):                     # subset of previous one above
        return True
    if re.search(re.compile(r"\bsynthetic fuel"), text):
        return True
    if re.search(re.compile(r"\bcombined heat and power"), text):
        return True
    if re.search(re.compile(r"\bsynth\w* gas\w*"), text):
        return True
    if re.search(re.compile(r"\bsyngas"), text):
        return True
    return False

def pattern21_LowCarb_Electrochemical_processes(text):
    if re.search(re.compile(r"\belectrochem\w* cell\w*"), text):
        return True
    if re.search(re.compile(r"\belectrochem\w* fuel\w*"), text):
        return True
    if re.search(re.compile(r"\bmembran\w* electrod\w*"), text):
        return True
    if re.search(re.compile(r"\bion\w* exchang\w* membran\w*"), text):
        return True
    if re.search(re.compile(r"\bion\w*exchang\w* membran\w*"), text):
        return True
    if re.search(re.compile(r"\belectrolyt\w* cell\w*"), text):
        return True
    if re.search(re.compile(r"\bcatalyt\w* convers\w*"), text):
        return True
    if re.search(re.compile(r"\bsolid\w* separat\w*"), text):
        return True
    if re.search(re.compile(r"\bmembran\w* separat\w*"), text):
        return True
    if re.search(re.compile(r"\bion\w* exchang\w* resin\w*"), text):
        return True
    if re.search(re.compile(r"\bion\w*exchang\w* resin\w*"), text):
        return True
    if re.search(re.compile(r"\bproton\w* exchang\w* membra\w*"), text):
        return True
    if re.search(re.compile(r"\bproton\w*exchang\w* membra\w*"), text):
        return True
    if re.search(re.compile(r"\bcataly\w* reduc\w*"), text):
        return True
    if re.search(re.compile(r"\belectrod\w* membra\w*"), text):
        return True
    if re.search(re.compile(r"\btherm\w* engin\w*"), text):
        return True
    return False

def pattern22_LowCarb_Battery(text):
    if re.search(re.compile(r"\bbatter\w*"), text) or re.search(re.compile(r"\baccumul\w*"), text):
        if re.search(re.compile(r"\bcharg\w*"), text):
            return True
        if re.search(re.compile(r"\brechar\w*"), text):
            return True
        if re.search(re.compile(r"\bturbocharg\w*"), text):
            return True
        if re.search(re.compile(r"\bhigh capacit\w*"), text):
            return True
        if re.search(re.compile(r"\brapid charg\w*"), text):
            return True
        if re.search(re.compile(r"\blong life"), text):
            return True
        if re.search(re.compile(r"\bultra\w*"), text):
            return True
        if re.search(re.compile(r"\bsolar"), text):
            return True
        if re.search(re.compile(r"\bno lead"), text):
            return True
        if re.search(re.compile(r"\bno mercury"), text):
            return True
        if re.search(re.compile(r"\bno cadmium"), text):
            return True
        if re.search(re.compile(r"\blithium\w*ion\w*"), text):
            return True
        if re.search(re.compile(r"\blithium\w* ion\w*"), text):
            return True
        if re.search(re.compile(r"\bLi\w*ion\w*"), text):               ###
            return True
    return False

def pattern23_LowCarb_Additional_energy(text):
    if re.search(re.compile(r"\baddition\w* energ\w* sourc\w*"), text):
        return True
    if re.search(re.compile(r"\baddition\w* sourc\w* of energ\w*"), text):
        return True
    return False

def pattern24_LowCarb_Carbon_capture_storage(text):
    if re.search(re.compile(r"\bcarbon"), text) and re.search(re.compile(r"\bcaptu\w*"), text):
        return True
    if re.search(re.compile(r"\bcarbon"), text) and re.search(re.compile(r"\bstor\w*"), text):
        return True
    if re.search(re.compile(r"\bcarbon dioxid\w*"), text):
        return True
    if re.search(re.compile(r"\bCO2"), text):
        return True
    return False

def pattern25_LowCarb_Energy_management(text):
    if re.search(re.compile(r"\bener\w* sav\w*"), text):
        return True
    if re.search(re.compile(r"\bener\w* effic\w*"), text):
        return True
    if re.search(re.compile(r"\benerg\w*effic\w*"), text):
        return True
    if re.search(re.compile(r"\benerg\w*sav\w*"), text):
        return True
    if re.search(re.compile(r"\blight\w* emit\w* diod\w*"), text):
        return True
    if re.search(re.compile(r"\bLED"), text):
        return True
    if re.search(re.compile(r"\borganic LED"), text):
        return True
    if re.search(re.compile(r"\bOLED"), text):
        return True
    if re.search(re.compile(r"\bCFL"), text):
        return True
    if re.search(re.compile(r"\bcompact fluorescent\w*"), text):
        return True
    if re.search(re.compile(r"\benerg\w* conserve\w*"), text):
        return True
    return False

def pattern26_LowCarb_Building_technologies(text):
    if re.search(re.compile(r"\bbuild\w*"), text) or re.search(re.compile(r"\bconstruct\w*"), text):
        if re.search(re.compile(r"\binsula\w*"), text):
            return True
        if re.search(re.compile(r"\bheat\w* retent\w*"), text):
            return True
        if re.search(re.compile(r"\bheat\w* exchang\w*"), text):
            return True
        if re.search(re.compile(r"\bheat\w* pump\w*"), text):
            return True
        if re.search(re.compile(r"\btherm\w* exchang\w*"), text):
            return True
        if re.search(re.compile(r"\btherm\w* decompos\w*"), text):
            return True
        if re.search(re.compile(r"\btherm\w* energ\w*"), text):
            return True
        if re.search(re.compile(r"\btherm\w* communic\w*"), text):
            return True
        if re.search(re.compile(r"\bthermoplast\w*"), text):
            return True
        if re.search(re.compile(r"\bthermocoup\w*"), text):
            return True
        if re.search(re.compile(r"\bheat\w* recover\w*"), text):
            return True
    return False
