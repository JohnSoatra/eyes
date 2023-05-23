import re as __re

def strip(text):
    return __re.sub(r'\s+', ' ', text).strip()