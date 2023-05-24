#!python3
from eyes_soatra.constant.depends.app_date.period import depends as __depends_period
from eyes_soatra.constant.depends.app_date.start import depends as __depends_start
from eyes_soatra.constant.depends.app_date.end import depends as __depends_end
from eyes_soatra.constant.user.user_agents import User_Agents as __User_Agents
from eyes_soatra.constant.vars import all_header_xpaths as __header_xpath
from eyes_soatra.funcs.utils.dict import sort_dict as __sort_dict
from eyes_soatra.funcs.utils.string import strip_space as __strip_space
from eyes_soatra.constant.libs.requests import requests as __requests

from translate import Translator as __Translator
from requests_html import HTML as __HTML

import jellyfish as __jellyfish
import random as __random
import time as __time
import re as __re

__separator = '\||-|:|\s+'
__header_min_length = 4
__date_max_length = 10
__date_last_words = ('まで', '以内', '。')
__date_more_signs = ('～')

# period 期間, 以内, 随時

def __sort_dict(dict):
    return dict

def __check_each(
    highlight,
    depends,
    min_point,
):
    result = {}
    point_temp = 0
    
    for token in highlight:
        if len(token) >= __header_min_length:
            for depend in depends:
                point = __jellyfish.jaro_similarity(depend, token)
                
                if point > point_temp:
                    point_temp = point
                    
                    result['keyword'] = token
                    result['similar-to'] = depend
                    result['point'] = round(point, 2)
                    
                    if point >= min_point:
                        result['ticked'] = True

    return result

def __highlighter(
    html,
    xpath,
    separator
):
    texts = []
    separator = __separator + (separator if separator else '')
    
    for xpath in (__header_xpath + (xpath if type(xpath) == list else [])):
        text_list = html.xpath(f'({xpath})//text()')
        
        for text in text_list:
            for token in __re.split(separator, text):
                if token:
                    texts.append(token)

    return texts

def __detail_page(
    highlight,
    min_point,
    depends_end,
    depends_start,
    depends_period,
    show_all_detail
):
    result = {}
    depends = {
        'app-start': (__depends_start + (depends_start if type(depends_start) == list else [])),
        'app-end': (__depends_end + (depends_end if type(depends_end) == list else [])),
        'app-period': (__depends_period + (depends_period if type(depends_period) == list else [])),
    }
    
    for key in depends:
        checked_result = __check_each(
            highlight,
            depends[key],
            min_point
        )
        
        if show_all_detail:
            result[key] = checked_result

        elif 'ticked' in checked_result:
            result[key] = checked_result

    return result

def __last_index(keyword, highlight):
    index = 0

    for i in range(0, len(highlight)):
        if highlight[i] == keyword:
            index = i
            
    return index

def __get_time(detail, highlight):
    result = {}
    
    for key in detail:
        apt = detail[key]
        
        if 'ticked' in apt:
            result[key] = ''
            index = __last_index(apt['keyword'], highlight)
            
            for i in range(index + 1, len(highlight)):
                string = highlight[i]
                
                if string.endswith(__date_more_signs):
                    result[key] += string
                    continue

                else:
                    result[key] += f' {string}'
                
                if (
                    string.endswith(__date_last_words) or
                    len(result[key]) >= __date_max_length
                ):
                    break
            
            result[key] = __strip_space(result[key])

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
    sleep_time=2,
    tries_timeout=3,
    tries_reject=25,
    tries_forward=10,
    min_point=0.85,
    depends_end=None,
    depends_start=None,
    depends_period=None,
    allow_redirects=True,
    show_detail=False,
    show_all_detail=False,
    show_highlight=False,
    
    **requests_options
):
    tried = 0
    agents = []
    redirected_forward = False
    
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
            redirected = redirected_forward if redirected_forward else response.is_redirect
            
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
            
            html = __HTML(html=response.content)
            
            if allow_redirects:
                meta_refresh = html.xpath("//meta[translate(@http-equiv,'REFSH','refsh')='refresh']/@content")
                
                if len(meta_refresh):
                    if tried < tries_forward:
                        content_refresh = meta_refresh[0]
                        content_slices = content_refresh.split(';')
                        
                        if len(content_slices) > 1:
                            url_refresh = content_slices[1]
                            
                            if url_refresh.lower().startswith('url='):
                                url_refresh = url_refresh[4:]
                                
                            redirected_forward = True
                            url = url_refresh
                            continue

                    else:
                        return __sort_dict({
                            'error': f'Out of forwarding tries.',
                            'redirected': True,
                            'url': url,
                            'tried': tried
                        })
            
            highlight = __highlighter(
                html,
                xpath,
                separator
            )
            
            if not (lang == 'ja' or lang == 'en'):
                translate = __Translator(from_lang=lang, to_lang='en')
                
                for i in range(0, len(highlight)):
                    highlight[i] = translate.translate(highlight[i])
            
            detail = __detail_page(
                highlight,
                min_point,
                depends_end,
                depends_start,
                depends_period,
                show_all_detail
            )
            time_result = __get_time(
                detail,
                highlight
            )
            
            return __sort_dict({
                **time_result,
                'url': response.url,
                'tried': tried,
                'status': status_code,
                'redirected': redirected,
                **({'detail': detail} if show_detail else {}),
                **({'highlight': highlight} if show_highlight else {}),
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
                    
                __time.sleep(sleep_time)
                
            else :
                if tried >= tries_timeout:
                    return __sort_dict({
                        'error': f'{error.__class__.__name__}: {error}',
                        'url': url,
                        'tried': tried
                    })
