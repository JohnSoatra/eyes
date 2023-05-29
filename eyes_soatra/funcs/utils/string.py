from eyes_soatra.constant.vars import xpath_prefix as __xpath_prefix
from eyes_soatra.constant.vars import tag_stop as __tag_stop
import re as __re

def strip_space(text):
    return __re.sub(r'\s+', ' ', text).strip()

def symbol(string):
    temp_symbol = True

    for char in string:
        temp_symbol = temp_symbol and not (char.isalnum() or char.isspace())
        
        if not temp_symbol:
            break

    return temp_symbol

def get_code(string):
    founds = __re.findall('^\[SOATRA:\d+\] ', string)
    
    if (founds):
        string = founds[0]
        string = string.replace('[SOATRA:', '').replace(']', '').strip()
        return int(string)
    
    return None

def put_code(code, string):
    founds = __re.findall('^\[SOATRA:\d+\] ', string)
    
    if not len(founds):
        return f'[SOATRA:{code}] {string}'

def remove_code(string):
    return __re.sub('^\[SOATRA:\d+\] ', '', string)

def xpath_tag(string):
    tag = ''
    
    while string.startswith(__xpath_prefix):
        for prefix in __xpath_prefix:
            string = string.removeprefix(prefix)

    for char in string:
        if char in __tag_stop:
            break
        
        tag += char
    
    return tag
