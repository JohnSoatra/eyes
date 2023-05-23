#!python3
from eyes_soatra.constant.depends.app_date.period import depends as __depends_period
from eyes_soatra.constant.depends.app_date.start import depends as __depends_start
from eyes_soatra.constant.depends.app_date.end import depends as __depends_end
from eyes_soatra.constant.user.user_agents import User_Agents as __User_Agents
from eyes_soatra.constant.vars import all_header_xpaths as __header_xpath
from eyes_soatra.funcs.utils.dict import sort_dict as __sort_dict
from eyes_soatra.funcs.utils.string import strip as __strip
from eyes_soatra.constant.libs.requests import requests as __requests

from translate import Translator as __Translator
from requests_html import HTML as __HTML

import jellyfish as __jellyfish
import random as __random
import time as __time
import re as __re

__separator = '\||-|:|\s+'
__header_min_length = 4

def __highlighter(html, xpath,):
    texts = []
    
    for xpath in (__header_xpath + (xpath if type(xpath) == list else [])):
        text_list = html.xpath(f'({xpath})//text()')
        
        for text in text_list:
            text = __strip(text)
            
            if len(text) >= __header_min_length:
                texts.append(text)

    return texts

def __check_each(
    highlight,
    depends,
    min_point,
    separator,
):
    temp_point = 0
    temp_depend = None
    temp_keyword = None
    
    for token in highlight:
        for each_token in __re.split(__separator + (separator if separator else ''), token):
            if len(each_token) >= __header_min_length:
                for depend in depends:
                    point = __jellyfish.jaro_similarity(depend, each_token)
                    
                    if point >= min_point:
                        return {
                            'ticked': True,
                            'keyword': each_token,
                            'similar-to': depend,
                            'point': round(point, 2)
                        }
                        
                    if point > temp_point:
                        temp_point = point
                        temp_depend = depend
                        temp_keyword = each_token

    return {
        'keyword': temp_keyword,
        'similar-to': temp_depend,
        'point': round(temp_point, 2)
    }

def __wanted_page(
    highlight,
    min_point,
    depends_end,
    depends_start,
    depends_period,
    separator
):
    result = {
        'highlight': highlight
    }
    depends = {
        'app-start': (__depends_start + (depends_start if type(depends_start) == list else [])),
        'app-end': (__depends_end + (depends_end if type(depends_end) == list else [])),
        'app-period': (__depends_period + (depends_period if type(depends_period) == list else [])),
    }
    
    for key in depends:
        checked_result = __check_each(
            highlight,
            depends[key],
            min_point,
            separator
        )
        
        if checked_result:
            result[key] = checked_result
        
    return result

# ----------- public function
def time_app(
    url,
    lang='ja',
    xpath=None,
    timeout=15,
    verify=False,
    headers=None,
    separator=None,
    sleep_reject=2,
    tries_timeout=3,
    tries_reject=25,
    allow_redirects=True,
    min_point=0.85,
    depends_end=None,
    depends_start=None,
    depends_period=None,
    
    **requests_options
):
    tried = 0
    agents = []
    
    while True:
        try:
            tried += 1
            user_agent = __random.choice(__User_Agents)
            
            while user_agent in agents:
                user_agent = __random.choice(__User_Agents)
                
            agents.append(user_agent)
                
            response = __requests.get(
                **requests_options,
                url=url,
                timeout=timeout,
                allow_redirects=allow_redirects,
                verify=verify,
                headers={
                    **(headers if headers else {}),
                    'USER-AGENT': user_agent,
                    'ACCEPT' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'ACCEPT-ENCODING' : 'gzip, deflate, br',
                    'ACCEPT-LANGUAGE' : 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,km-KH;q=0.6,km;q=0.5,ja-JP;q=0.4,ja;q=0.3',
                    'REFERER' : 'https://www.google.com/'
                },
            )
            status_code = response.status_code
            redirected = response.is_redirect
            
            if status_code >= 400 and status_code <= 499:
                return __sort_dict({
                    'error': f'Client error responses: {status_code}',
                    'status': status_code,
                    'redirected': redirected,
                    'url': response.url,
                    'tried': tried,
                })
                
            if status_code >= 500 and status_code <= 599:
                return __sort_dict({
                    'error': f'Server error responses: {status_code}',
                    'status': status_code,
                    'redirected': redirected,
                    'url': response.url,
                    'tried': tried,
                })
                
            highlight = __highlighter(__HTML(html=response.content), xpath)
            
            if not (lang == 'ja' or lang == 'en'):
                translate = __Translator(from_lang=lang, to_lang='en')
                
                for i in range(0, len(highlight)):
                    highlight[i] = translate.translate(highlight[i])
            
            return __sort_dict({
                'status': status_code,
                'redirected': redirected,
                'url': response.url,
                'tried': tried,
                'detail': __wanted_page(
                    highlight,
                    min_point,
                    depends_end,
                    depends_start,
                    depends_period,
                    separator
                ),
            })

        except Exception as error:                    
            if (
                type(error) == __requests.exceptions.ConnectionError or
                type(error) == __requests.exceptions.SSLError
            ):
                if tried >= tries_reject:
                    return __sort_dict({
                        'error': f'{error.__class__.__name__}: {error}',
                        'url': url,
                        'tried': tried
                    })
                    
                __time.sleep(sleep_reject)
                
            else :
                if tried >= tries_timeout:
                    return __sort_dict({
                        'error': f'{error.__class__.__name__}: {error}',
                        'url': url,
                        'tried': tried
                    })
