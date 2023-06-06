from eyes_soatra.constant.vars import xpath_prefix as __xpath_prefix
from eyes_soatra.constant.vars import tag_stop as __tag_stop
from eyes_soatra.constant.vars import protocols as __protocols
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

def protocol(url):
    for each in __protocols:
        if url.startswith(each):
            return each
        
    return None

def get_domain(url):
    url = remove_protocol(url)
    url = url.split('/')[0]

    return url

def join_path(*args):
    result = ''
    
    for each in args:
        if result == '':
            result += each
        
        else:
            if result.endswith('/'):
                if each.startswith('/'):
                    result += each.removeprefix('/')

                else:
                    result += each

            else:
                if each.startswith('/'):
                    result += each

                else:
                    result += '/' + each

    return result

def raw_url(url):
    return remove_slash(remove_protocol(url))

def remove_protocol(url):
    return url.removeprefix('http://').removeprefix('https://')

def remove_slash(url):
    while url.endswith('/'):
        url = url.removesuffix('/')
    
    return url

def back_home(url, response):
    if remove_slash(url) == remove_slash(response.url):
        return False
    
    path = remove_protocol(response.url)
    path = remove_slash(path)
    
    if not '/' in path:
        return True

    return False


