#!python3
from eyes_soatra.constant.depends.app_date.period import depends as __depends_period
from eyes_soatra.constant.depends.app_date.start import depends as __depends_start
from eyes_soatra.constant.depends.app_date.end import depends as __depends_end
from eyes_soatra.constant.user.user_agents import User_Agents as __User_Agents
from eyes_soatra.funcs.utils.dict import sort_dict as __sort_dict
from eyes_soatra.funcs.utils.list import find as __find
from eyes_soatra.funcs.utils.list import filter_list as __filter_list
from eyes_soatra.funcs.utils.string import strip_space as __strip_space
from eyes_soatra.constant.libs.requests import requests as __requests
from eyes_soatra.constant.vars import header_xpaths as __header_xpath
from eyes_soatra.constant.vars import description_xpath as __description_xpath

from translate import Translator as __Translator
from functools import reduce as __reduce
from lxml import html as __html

import jellyfish as __jellyfish
import random as __random
import time as __time
import re as __re

__separator = '\||-|:|\s+'
__header_min_length = 4
__date_max_length = 60

def __sort_dict(dict):
    return dict

def __next_word(keyword, highlight):
    result = {
        '': 0
    }
    
    for i in range(0, len(highlight)):
        if highlight[i] == keyword and i < len(highlight) - 1:
            next_word = highlight[i + 1]
            
            if next_word in result:
                result[next_word] += 1
                
            else:
                result[next_word] = 1
    
    max_point = max(list(result.values()))
    next_word = __find(
        lambda key: result[key] == max_point,
        list(result.keys())
    )

    return next_word

def __smallest(blogs):
    span = None
    other = None

    for i in range(0, len(blogs)):
        temp_blog = blogs[i]
        tag_blog = temp_blog[0]
        content_blog = ''.join(temp_blog[1:])
        
        if tag_blog == '//span':
            if span == None or len(content_blog) < len(''.join(span[1:])):
                span = temp_blog
                
        else:
            if other == None or len(content_blog) < len(''.join(other[1:])):
                other = blogs[i]

    return other or span

def __translate(lang, highlight):
    if not (lang == 'ja' or lang == 'en'):
        translate = __Translator(from_lang=lang, to_lang='en')
        
        for key in highlight:
            if key == 'blogs':
                for i in range(0, len(highlight[key])):
                    for j in range(0, len(highlight[key][i][1:])):
                        highlight[key][i][j] = translate.translate(highlight[key][i][j])

            elif key == 'texts':
                for i in range(0, len(highlight[key])):
                    highlight[key][i] = translate.translate(highlight[key][i])
    
    return highlight

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
    blogs = []
    texts = []
    separator = __separator + (separator if separator else '')
    
    for xpath in (__header_xpath + (xpath if type(xpath) == list else [])):
        element_list = html.xpath(xpath)
        
        for element in element_list:
            text_list = element.xpath('.//text()')
            blog = []

            for text in text_list:
                for token in __re.split(separator, text):
                    if token:
                        texts.append(token)
                        blog.append(token)

            if blog and (xpath in __description_xpath):
                blogs.append([xpath, *blog])

    return {
        'blogs': blogs,
        'texts': texts
    }

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

def __get_time(detail, texts, blogs, give_all):
    result = {}
    has_period = 'app-period' in detail and 'ticked' in detail['app-period']
    
    for key in detail:
        if not give_all and has_period:
            if key == 'app-start' or key == 'app-end':
                continue
            
        app = detail[key]
        
        if 'ticked' in app:
            next_word = __next_word(
                app['keyword'],
                texts
            )
            temps = __filter_list(
                lambda blog: __find(
                    lambda token: next_word in token,
                    blog
                ),
                blogs
            )
            temp = __smallest(temps)
            temp = __reduce(
                lambda str1, str2: f'{str1} {str2}' if next_word in str1 else str2,
                temp
            )
            temp = __strip_space(temp)
            result[key] = temp[:__date_max_length]
            
            for char in temp[__date_max_length:]:
                if __re.search('\s', char):
                    break
                
                result[key] += char
    
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
    show_blog=False,
    give_all=False,
    
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
            
            html = __html.fromstring(response.content)
            
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
            highlight = __translate(
                lang,
                highlight
            )
            detail = __detail_page(
                highlight['texts'],
                min_point,
                depends_end,
                depends_start,
                depends_period,
                show_all_detail
            )
            time_result = __get_time(
                detail,
                highlight['texts'],
                highlight['blogs'],
                give_all
            )
            
            return __sort_dict({
                **time_result,
                'url': response.url,
                'tried': tried,
                'status': status_code,
                'redirected': redirected,
                **({'detail': detail} if show_detail else {}),
                **({'highlight': highlight['texts']} if show_highlight else {}),
                **({'blogs': highlight['blogs']} if show_blog else {}),
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
