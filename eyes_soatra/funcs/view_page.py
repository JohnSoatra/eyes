#!python3
from eyes_soatra.constant.depends.view.no_data import depends as __depends_no_data
from eyes_soatra.constant.depends.view.not_found import depends as __depends_404
from eyes_soatra.constant.user.user_agents import User_Agents as __User_Agents
from eyes_soatra.constant.libs.requests import requests as __requests
from eyes_soatra.constant.vars import header_xpaths as __header_xpaths_all
from eyes_soatra.constant.vars import remove_tags as __remove_tags
from eyes_soatra.funcs.utils.string import strip_space as __strip_space
from eyes_soatra.funcs.utils.string import back_home as __back_home
from eyes_soatra.funcs.utils.string import protocol as __protocol
from eyes_soatra.funcs.utils.string import join_path as __join_path
from eyes_soatra.funcs.utils.string import get_domain as __get_domain
from eyes_soatra.funcs.utils.string import raw_url as __raw_url

from translate import Translator as __Translator
from lxml import html as __html
from lxml import etree as __etree

import jellyfish as __jellyfish
import random as __random
import time as __time
import re as __re

# private global variables
__separator = '\||-|:'
__header_min_length = 3
__paragraph_min_length = 7
__content_min_length = 1
__container = 'self::div or self::span or self::table'
__header_xpaths = [
    '//title',
    '//h1[self::*//text() and last()=1]',
    '//h2[self::*//text() and last()=1]'
]
__paragraph_xpaths = [
    '//p[@class="no_data"]',
    '//h1[self::*//text()]/following-sibling::p[1]',
    '//h1[self::*//text()]/following-sibling::*//p[1]',
    f'//*[({__container}) and self::*//h1[self::*//text()] and self::*/*[last()=1]]/following-sibling::*[1][{__container}]//p[1]'
]
__content_xpaths = [
    '//h1[self::*//text()]/following-sibling::*|//h1[self::*//text()]/following-sibling::*//*|//*[self::*//h1[self::*//text()] and self::*/*[last()=1]]/following-sibling::*[1]//*'
]

def __translate(lang, highlight):
    if not (lang == 'ja' or lang == 'en'):
        translate = __Translator(from_lang=lang, to_lang='en')
        
        for key in highlight:
            for i in range(0, len(highlight[key])):
                highlight[key][i] = translate.translate(highlight[key][i])
                
    return highlight

def __highlighter(
    html,
    header_xpath,
    paragraph_xpath,
    content_xpath,
    allow_all_tags,
    separator
):
    header_texts = []
    paragraph_texts = []
    content_texts = []
    separator = __separator + (separator if separator else '')
    
    for xpath in (__header_xpaths_all if allow_all_tags else __header_xpaths) + (header_xpath if type(header_xpath) == list else []):
        element_list = html.xpath(xpath)
        
        for element in element_list:
            header_list = element.xpath('.//text()')
            header = ' '.join(header_list)

            for token in __re.split(separator, header):
                    token = __strip_space(token)

                    if len(token) >= __header_min_length:
                        header_texts.append(token)

    for xpath in __paragraph_xpaths + (paragraph_xpath if type(paragraph_xpath) == list else []):
        element_list = html.xpath(xpath)
        
        for element in element_list:
            paragraph_list = element.xpath('.//text()')
            paragraph = ' '.join(paragraph_list)

            for token in __re.split(separator, paragraph):
                token = __strip_space(token)

                if len(token) >= __paragraph_min_length:
                    paragraph_texts.append(token)
    
    for xpath in __content_xpaths + (content_xpath if type(content_xpath) == list else []):
        element_list = html.xpath(xpath)

        for element in element_list:
            content_list = element.xpath('.//text()')
            content = ' '.join(content_list)

            for token in __re.split(separator, content):
                token = __strip_space(token)
                
                if len(token) >= __content_min_length:
                    content_texts.append(token)
            
    return {
        'headers': header_texts,
        'paragraphs': paragraph_texts,
        'contents': content_texts,
    }

def __bad_page(
    highlight,
    depends,
    header_min_point,
    paragraph_min_point,
    show_highlight,
    show_header,
    show_paragraph,
    show_content,
):
    header_high_point = 0
    paragraph_high_point = 0
    
    headers = highlight['headers']
    paragraphs = highlight['paragraphs']
    contents = highlight['contents']
    
    result = {
        'active': True,
        'informed': False,
        'blank': False,
        'checked': True,
        **({'highlight': highlight} if show_highlight else {})
    }

    if len(headers):
        header_similar = ''
        header_keyword = ''
        
        for depend in __depends_404 + (depends if type(depends) == list else []):
            for token in headers:
                point = __jellyfish.jaro_similarity(depend, token)
                
                if point > header_high_point:
                    header_high_point = point
                    header_similar = depend
                    header_keyword = token
                    
                if point >= header_min_point:
                    result = {
                        **result,
                        'active': False,
                    }
                    break
                
        if header_high_point > 0 and show_header:
            result = {
                **result,
                'header': {
                    'keyword': header_keyword,
                    'similar-to': header_similar,
                    'points': round(header_high_point, 2),
                }
            }

    if len(paragraphs):
        paragraph_similar = ''
        paragraph_keyword = ''
        
        for depend in __depends_no_data + (depends if type(depends) == list else []):
            for token in paragraphs:
                point = __jellyfish.jaro_similarity(depend, token)
                
                if point > paragraph_high_point:
                    paragraph_high_point = point
                    paragraph_similar = depend
                    paragraph_keyword = token
                    
                if point >= paragraph_min_point:
                    result = {
                        **result,
                        'informed': True,
                    }
                    break
                
        if paragraph_high_point > 0 and show_paragraph:
            result = {
                **result,
                'paragraph': {
                    'keyword': paragraph_keyword,
                    'similar-to': paragraph_similar,
                    'points': round(paragraph_high_point, 2)
                }
            }

    if len(contents) == 0 and show_content:
        result = {
            **result,
            'blank': True,
        }
        
    return result

# ------------------------ public function
def view_page(
    url,
    lang='ja',
    timeout=15,
    verify=False,
    headers=None,
    depends=None,
    separator=None,
    sleep_reject=2,
    tries_timeout=3,
    tries_reject=25,
    tries_forward=10,
    header_xpath=None,
    paragraph_xpath=None,
    content_xpath=None,
    allow_redirects=True,
    allow_all_header_tags=True,
    header_min_point=0.8,
    paragraph_min_point=0.85,
    
    show_highlight=False,
    show_header=False,
    show_paragraph=False,
    show_content=False,
    
    **requests_options
):
    url = __re.sub(r'\s', '', url)
    start_url = url
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
            redirected = redirected_forward if redirected_forward else __raw_url(start_url) != __raw_url(response.url)
            expired = response.headers.get('Expires')
            expired = expired if expired else (response.headers.get('expires') or False)
            expired_obj = {'expired': expired} if expired else {}
            current_url = response.url

            back_home = __back_home(
                url,
                response
            )

            if back_home:
                return {
                    'active': None,
                    'checked': False,
                    **expired_obj,
                    'error': f'Back to Home Page',
                    'redirected': True,
                    'url': current_url,
                    'status': status_code,
                    'tried': tried,
                }
            
            if status_code >= 400 and status_code <= 499:
                return {
                    'active': False,
                    'checked': False,
                    **expired_obj,
                    'error': f'Client error responses: {status_code}',
                    'redirected': redirected,
                    'url': current_url,
                    'status': status_code,
                    'tried': tried,
                }
                
            if status_code >= 500 and status_code <= 599:
                return {
                    'active': False,
                    'checked': False,
                    **expired_obj,
                    'error': f'Server error responses: {status_code}',
                    'redirected': redirected,
                    'url': current_url,
                    'status': status_code,
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
                            
                            if __protocol(url_refresh):
                                url = url_refresh

                            else:
                                protocol = __protocol(url)
                                domain = __get_domain(url)
                                url = __join_path(protocol, domain, url_refresh)

                            continue

                    else:
                        return {
                            'active': None,
                            'checked': False,
                            'error': f'Out of forwarding tries.',
                            'redirected': True,
                            'url': url,
                            'tried': tried
                        }

            highlight = __highlighter(
                html,
                header_xpath,
                paragraph_xpath,
                content_xpath,
                allow_all_header_tags,
                separator
            )
            highlight = __translate(lang, highlight)
            
            return {
                **__bad_page(
                    highlight,
                    depends,
                    header_min_point,
                    paragraph_min_point,
                    
                    show_highlight,
                    show_header,
                    show_paragraph,
                    show_content,
                ),
                **expired_obj,
                'redirected': redirected,
                'url': current_url,
                'status': status_code,
                'tried': tried,
            }

        except Exception as error:
            if (
                type(error) == __requests.exceptions.ConnectionError or
                type(error) == __requests.exceptions.SSLError
            ):
                if tried >= tries_reject:
                    return {
                        'active': None,
                        'checked': False,
                        'error': f'{error.__class__.__name__}: {error}',
                        'redirected': False,
                        'url': url,
                        'tried': tried
                    }
                __time.sleep(sleep_reject)
                
            else :
                if tried >= tries_timeout:
                    return {
                        'active': None,
                        'checked': False,
                        'error': f'{error.__class__.__name__}: {error}',
                        'redirected': False,
                        'url': url,
                        'tried': tried
                    }
