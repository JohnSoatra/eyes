#!python3
from eyes_soatra.constant.depends.app_date.period import depends as __depends_period
from eyes_soatra.constant.depends.app_date.start import depends as __depends_start
from eyes_soatra.constant.depends.app_date.end import depends as __depends_end
from eyes_soatra.constant.depends.app_date.formats.period import formats as __formats_period
from eyes_soatra.constant.depends.app_date.formats.start import formats as __formats_start
from eyes_soatra.constant.depends.app_date.formats.end import formats as __formats_end
from eyes_soatra.constant.user.user_agents import User_Agents as __User_Agents
from eyes_soatra.funcs.utils.list import find as __find
from eyes_soatra.funcs.utils.list import map_list as __map_list
from eyes_soatra.funcs.utils.string import strip_space as __strip_space
from eyes_soatra.funcs.utils.string import symbol as __symbol_all
from eyes_soatra.funcs.utils.string import xpath_tag as __xpath_tag
from eyes_soatra.constant.libs.requests import requests as __requests
from eyes_soatra.constant.vars import header_xpaths as __header_xpath
from eyes_soatra.constant.vars import description_xpath as __description_xpath
from eyes_soatra.constant.vars import full_stops as __full_stops
from eyes_soatra.constant.vars import remove_tags as __remove_tags
from eyes_soatra.constant.vars import priority_tag as __priority_tags
from eyes_soatra.constant.vars import priority_header_tag as __priority_header_tags
from eyes_soatra.constant import labels

from translate import Translator as __Translator
from lxml import html as __html
from lxml import etree as __etree

import jellyfish as __jellyfish
import random as __random
import time as __time
import re as __re
import json as __json

__separator = '\||-|:|\s+'
__header_min_length = 4
__date_max_length = 60

def __highlighter(
    html,
    xpath,
    xpath_desc,
    separator
):
    texts = []
    blogs = []
    separator = __separator + (separator if separator else '')
    
    xpaths = (__header_xpath + (xpath if type(xpath) == list else []))
    xpaths = __map_list(lambda each: f'({each})', xpaths)
    xpath = '|'.join(xpaths)
    
    xpaths_desc = (__description_xpath + (xpath_desc if type(xpath_desc) == list else []))
    tags_desc = __map_list(lambda xpath: __xpath_tag(xpath), xpaths_desc)
    
    elements = html.xpath(xpath)
    index = 0

    for element in elements:
        tag = element.tag
        temp_blogs = []
        text_list = element.xpath('.//text()')

        for text in text_list:
            for token in __re.split(separator, text):
                if token and not __symbol_all(token):
                    texts.append({
                        'tag': tag,
                        'token': token
                    })
                    temp_blogs.append({
                        'index': index,
                        'token': token
                    })
                    index += 1

        if temp_blogs and tag in tags_desc:
            blogs.append({
                'tag': tag,
                'blogs': temp_blogs
            })
    
    html_texts = []

    for text in html.xpath('//text()'):
        for token in __re.split(separator, text):
            if token and not __symbol_all(token):
                html_texts.append(token)
    
    return {
        'texts': texts,
        'blogs': blogs,
        'html-texts': html_texts
    }
    
def __type_formats(type):
    if type == labels.APP_START:
        return __formats_start
    
    if type == labels.APP_END:
        return __formats_end
    
    else:
        return __formats_period
    
def __best_point(word, depends):
    point = 0
    
    for depend in depends:
        temp = __jellyfish.jaro_similarity(word, depend)
        
        if point < temp:
            point  = temp

    return point
    
def __next_word(type_app, keyword, highlight):
    texts = highlight['html-texts']
    founds = []
    
    for i in range(0, len(texts)):
        if texts[i] == keyword and i < len(texts) - 1:
            next_word = texts[i + 1]
            
            if not next_word in founds:
                founds.append(next_word)

    if len(founds):
        formats = __type_formats(type_app)
        nexts = {
            'word': founds[0],
            'point': __best_point(founds[0], formats)
        }
        
        for i in range(1, len(founds)):
            point = __best_point(founds[i], formats)
            
            if point > nexts['point']:
                nexts = {
                    'word': founds[i],
                    'point': point
                }
        
        return nexts['word']

    return None

def __find_priority(founds):
    for tag in __priority_tags:
        found = __find(
            lambda each: each['tag'] == tag,
            founds
        )
        
        if found:
            return found
        
    priority = founds[0]
    
    for i in range(1, len(founds)):
        if len(priority['token']) > len(founds[i]['token']):
            priority = founds[i]
            
    return priority

def __specific_blog(
    next_word,
    keyword,
    highlight,
):
    texts = highlight['texts']
    texts_tokens = __map_list(lambda each: each['token'], texts)
    blogs = highlight['blogs']
    founds = []

    for each_blog in blogs:
        blogs_inner = each_blog['blogs']
        tokens = __map_list(lambda each: each['token'], blogs_inner)
        
        if next_word in tokens:
            for index in range(0, len(blogs_inner)):
                each = blogs_inner[index]
                
                if each['token'] == next_word:
                    preceding = each['index'] - 1
                    preceding = preceding if preceding >= 0 else 0
                    
                    if texts_tokens[preceding] == keyword:
                        str_token = ' '.join(tokens[index:])
                        found = __find(
                            lambda each: each['tag'] == each_blog['tag'],
                            founds
                        )
                        if found:
                            if len(found['token']) > len(str_token):
                                found['token'] = str_token

                        else:
                            founds.append({
                                'tag': each_blog['tag'],
                                'token': str_token
                            })
    
    priority = __find_priority(founds)
    if priority:
        return priority['token']

    return None

def __translate(lang, highlight):
    if not (lang == 'ja' or lang == 'en'):
        translate = __Translator(from_lang=lang, to_lang='en')
        
        highlight['html-texts'] = __map_list(
            lambda each: translate.translate(each),
            highlight['html-texts']
        )
        highlight['texts'] = __map_list(
            lambda each: {
                **each,
                'token': translate.translate(each['token'])
            },
            highlight['texts']
        )
        highlight['blogs'] = __map_list(
            lambda each: {
                **each,
                'blogs': __map_list(
                    lambda each: {
                        **each,
                        'token': translate.translate(each['token'])
                    },
                    each['blogs']
                )
            },
            highlight['blogs']
        )

    return highlight

def __header_best(founds):
    for found in founds:
        if found['tag'] in __priority_header_tags:
            return found
    
    header = founds[0]
    
    for i in range(1, len(founds)):
        if header['point'] < founds[i]['point']:
            header = founds[i]

    return header    

def __check_each(
    type_app,
    min_point,
    depends,
    highlight,
):
    texts = highlight['texts']
    result = {}
    point_temp = 0
    founds = []

    for text_obj in texts:
        token = text_obj['token']
        
        if len(token) >= __header_min_length:
            for depend in depends:
                point = __jellyfish.jaro_similarity(depend, token)
                
                if point > point_temp:
                    point_temp = point
                    result['keyword'] = token
                    result['similar-to'] = depend
                    result['point'] = round(point, 2)

                if point >= min_point:
                    founds.append({
                        'tag': text_obj['tag'],
                        'keyword': token,
                        'similar-to': depend,
                        'point': round(point, 2)
                    })

    if len(founds):
        best_header = __header_best(founds)
        result = {
            'ticked': True,
            **result,
            **best_header,
            'next-word': __next_word(
                type_app,
                best_header['keyword'],
                highlight
            )
        }
    
    return result

def __table_title(html, keyword, highlight):
    blogs = highlight['blogs']
    
    for blog in blogs:
        if (
            (blog['tag'] == 'th' or blog['tag'] == 'td') and
            keyword in __map_list(lambda each: each['token'], blog['blogs'])
        ):
            for table in html.xpath('//table'):
                tr1 = table.xpath('./thead/tr[1]')
                tr1 = tr1 if tr1 else table.xpath('./tbody/tr[1]')
                tr1 = tr1 if tr1 else table.xpath('./tr[1]')
                
                if len(tr1):
                    tr1 = tr1[0]
                    if tr1.xpath('./th') and tr1.xpath('./td'):
                        return None
                    
                    ts = tr1.xpath('./*[self::td or self::th]')
                    position = 0

                    for th in ts:
                        text = th.text_content()
                        position += 1
                        
                        if __re.sub(r'\s+', '', text) == keyword:
                            return {
                                'table': table,
                                'position': position
                            }

    return None

def __table_worker(html, keyword, highlight):
    table_obj = __table_title(html, keyword, highlight)
    
    if table_obj:
        table = table_obj['table']
        position = table_obj['position']
        tr_position = 1 if table.xpath(f'./thead') else 2
        tds = table.xpath(f'./tbody/tr[{tr_position}]/td[position()={position}]')
        tds = tds if tds else table.xpath(f'./tr[{tr_position}]/td[position()={position}]')

        if len(tds):
            return __strip_space(tds[0].text_content())
        
    else:
        for tr in html.xpath('//tr'):
            tds = tr.xpath('./td')
            
            for i in range(0, len(tds)):
                td = tds[i]
                
                if __re.sub(r'\s+', '', td.text_content()) == keyword:
                    texts = tr.xpath(f'./td[position()>{i+1}]//text()')
                    
                    return __strip_space(' '.join(texts))

    return None

def __detail_page(
    highlight,
    min_point,
    depends_end,
    depends_start,
    depends_period,
    show_all_detail,
    give_all
):
    result = {}
    depends = {
        labels.APP_START: (__depends_start + (depends_start if type(depends_start) == list else [])),
        labels.APP_END: (__depends_end + (depends_end if type(depends_end) == list else [])),
        labels.APP_PERIOD: (__depends_period + (depends_period if type(depends_period) == list else [])),
    }
    
    for key in depends:
        checked_result = __check_each(
            key,
            min_point,
            depends[key],
            highlight,
        )
        
        if show_all_detail:
            result[key] = checked_result

        elif 'ticked' in checked_result:
            result[key] = checked_result
            
    if not give_all:
        if labels.APP_PERIOD in result:
            for key in [labels.APP_START, labels.APP_END]:
                if key in result:
                    result.pop(key)

    return result

def __get_time(
    html,
    detail,
    highlight,
    give_all
):
    result = {}
    has_period = 'app-period' in detail and 'ticked' in detail['app-period']
    
    for key in detail:
        if not give_all and has_period:
            if key == 'app-start' or key == 'app-end':
                continue
            
        app = detail[key]
        
        if 'ticked' in app:
            keyword = app['keyword']
            text_td = __table_worker(
                html,
                keyword,
                highlight,
            )
            
            if text_td:
                result[key] = text_td
                
            else:
                next_word = app['next-word']

                if next_word:
                    specific = __specific_blog(
                        next_word,
                        keyword,
                        highlight
                    )

                    if specific:
                        result[key] = next_word
                        
                        for char in specific.removeprefix(next_word):
                            result[key] += char

                            if (
                                char in __full_stops or
                                (
                                    __re.search('\s', char) and
                                    len(result[key]) >= __date_max_length
                                )
                            ):
                                break

    return result

# ----------- public function
def time_app(
    url=None,
    content=None,
    lang='ja',
    xpath=None,
    xpath_desc=None,
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
    show_detail=True,
    show_all_detail=False,
    show_texts=False,
    show_blog=False,
    give_all=False,
    
    **requests_options
):
    if url == None and content == None:
        raise Exception('Please input one of those: url and content.')
    
    if url:
        url = __re.sub(r'\s', '', url)

    tried = 0
    agents = []
    redirected_forward = False

    while True:
        try:
            tried += 1
            
            if content:
                status_code = 200
                redirected = False
                current_url = url
                html = __html.fromstring(content)
                __etree.strip_elements(html, *__remove_tags)
                
            else:
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
                current_url = response.url
                
                if status_code >= 400 and status_code <= 499:
                    return {
                        'error': f'Client error responses: {status_code}',
                        'status': status_code,
                        'redirected': redirected,
                        'url': current_url,
                        'tried': tried,
                    }
                    
                if status_code >= 500 and status_code <= 599:
                    return {
                        'error': f'Server error responses: {status_code}',
                        'status': status_code,
                        'redirected': redirected,
                        'url': current_url,
                        'tried': tried,
                    }
                
                html = __html.fromstring(response.content)
                __etree.strip_elements(html, *__remove_tags)
                
                if allow_redirects:
                    meta_refresh = html.xpath("//meta[translate(@http-equiv,'REFSH','refsh')='refresh']/@content")
                    
                    if len(meta_refresh):
                        if tried < tries_forward:
                            content_refresh = meta_refresh[0]
                            content_slices = content_refresh.split(';')
                            
                            if len(content_slices) > 1:
                                url_refresh = __strip_space(content_slices[1])
                                
                                if url_refresh.lower().startswith('url='):
                                    url_refresh = url_refresh[4:]
                                    
                                redirected_forward = True
                                url = url_refresh
                                continue

                        else:
                            return {
                                'error': f'Out of forwarding tries.',
                                'redirected': True,
                                'url': url,
                                'tried': tried
                            }

            highlight = __highlighter(
                html,
                xpath,
                xpath_desc,
                separator
            )
            highlight = __translate(
                lang,
                highlight
            )
            detail = __detail_page(
                highlight,
                min_point,
                depends_end,
                depends_start,
                depends_period,
                show_all_detail,
                give_all
            )
            time_result = __get_time(
                html,
                detail,
                highlight,
                give_all
            )
            
            return {
                **time_result,
                'url': current_url,
                'tried': tried,
                'status': status_code,
                'redirected': redirected,
                **({'detail': detail} if show_detail and detail else {}),
                **({'texts': highlight['texts']} if show_texts else {}),
                **({'blogs': highlight['blogs']} if show_blog else {}),
            }

        except Exception as error:                    
            if (
                type(error) == __requests.exceptions.ConnectionError or
                type(error) == __requests.exceptions.SSLError
            ):
                if tried >= tries_reject:
                    return {
                        'error': f'{error.__class__.__name__}: {error}',
                        'url': url,
                        'tried': tried
                    }
                    
                __time.sleep(sleep_time)
                
            else :
                if tried >= tries_timeout:
                    return {
                        'error': f'{error.__class__.__name__}: {error}',
                        'url': url,
                        'tried': tried
                    }
