"""
Patterns for identifying green technologies in text descriptions such as patent abstracts. 
"""

import re

def pattern01_ecology(text):
    if re.search(re.compile(r"\becologi\w*\b", flags=re.I), text):
        if re.search(re.compile(r"\benvironmenta\w*\b", flags=re.I), text) or \
                        re.search(re.compile(r"\bgreen\w*\b", flags=re.I), text) or \
                        re.search(re.compile(r"\bsustainab\w*\b", flags=re.I), text):
            return True
    return False
