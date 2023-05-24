import re as __re

def strip_space(text):
    return __re.sub(r'\s+', ' ', text).strip()