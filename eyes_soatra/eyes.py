#!python3
from eyes_soatra.depends.depends_404 import depends as __depends_404
from eyes_soatra.depends.depends_no_data import depends as __depends_no_data
from eyes_soatra.needs.user_agents import User_Agents as __User_Agents
from translate import Translator as __Translator
from requests_html import HTML as __HTML
import requests as __requests
import jellyfish as __jellyfish
import re as __re
import time as __time
import random

# Suppress only the single warning from urllib3 needed.
__requests.packages.urllib3.disable_warnings()
__requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    __requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

# private global variables
__separator = '\||-|:'
__header_min_length = 3
__paragraph_min_length = 7
__container = 'self::div or self::span or self::table'
__header_xpaths = [
    '//title',
    '//h1[self::*//text() and last()=1]',
    '(//h2[self::*//text() and last()=1])[1]'
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

# private functions
def __sort_dict(dict):
    keys = list(dict.keys())
    keys.sort()
    new_dict = {}
    
    for key in keys:
        new_dict[key] = dict[key]
    
    return new_dict

def __strip(text):
    return __re.sub(r'\s+', ' ', text).strip()

def __get_highlight(
    html,
    header_xpath,
    paragraph_xpath,
    content_xpath,
):
    html = __HTML(html=html)
    highlight = __highlighter(
        html,
        header_xpath,
        paragraph_xpath,
        content_xpath
    )
    
    return highlight

def __highlighter(
    html,
    header_xpath,
    paragraph_xpath,
    content_xpath,
):
    header_texts = []
    paragraph_texts = []
    content_texts = []
    
    for xpath in __header_xpaths + (header_xpath if type(header_xpath) == list else []):
        header_list = html.xpath(f'({xpath})//text()')
        header = ' '.join(header_list)
        header = __strip(header)
        
        if len(header) >= __header_min_length:
            header_texts.append(header)
        # for header in header_list:
    
    for xpath in __paragraph_xpaths + (paragraph_xpath if type(paragraph_xpath) == list else []):
        paragraph_list = html.xpath(f'({xpath})//text()')
        paragraph = ' '.join(paragraph_list)
        paragraph = __strip(paragraph)
        
        if len(paragraph) >= __paragraph_min_length:
            paragraph_texts.append(paragraph)

        if len(paragraph_texts):
            break
        # for paragraph in paragraph_list:
    
    for xpath in __content_xpaths + (content_xpath if type(content_xpath) == list else []):
        content_list = html.xpath(f'({xpath})//text()')
        content = ' '.join(content_list)
        content = __strip(content)
        
        if len(content) > 0:
            content_texts.append(content)

        if len(content_texts):
            break
        # for content in content_list:
            

    return {
        'headers': header_texts,
        'paragraphs': paragraph_texts,
        'contents': content_texts,
    }

def __bad_page(
    highlight,
    separator,
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
    
    # check active
    if len(headers):
        header_similar = ''
        header_keyword = ''
        broke = False
        
        for depend in __depends_404 + (depends if type(depends) == list else []):
            for header in headers:                
                for token_header in __re.split(__separator + (separator if separator else ''), header):
                    token_header = __strip(token_header)
                    
                    if len(token_header) >= __header_min_length:
                        s1 = __jellyfish.jaro_similarity(depend, token_header)
                        # s2 = __jellyfish.jaro_winkler_similarity(depend, token_header)
                        
                        # points = (s1 + s2) / 2
                        points = s1
                        
                        if points > header_high_point:
                            header_high_point = points
                            header_similar = depend
                            header_keyword = token_header
                            
                        if points >= header_min_point:
                            result = {
                                **result,
                                'active': False,
                            }
                            
                            broke = True
                            break
                if broke:
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

    # check informed
    if len(paragraphs):
        paragraph_similar = ''
        paragraph_keyword = ''
        broke = False
        
        for depend in __depends_no_data + (depends if type(depends) == list else []):
            for paragraph in paragraphs:
                for token_paragraph in __re.split(__separator + (separator if separator else ''), paragraph):
                    token_paragraph = __strip(token_paragraph)
                    
                    if len(token_paragraph) >= __paragraph_min_length:
                        s1 = __jellyfish.jaro_similarity(depend, token_paragraph)
                        # s2 = __jellyfish.jaro_winkler_similarity(depend, token_paragraph)
                        
                        # points = (s1 + s2) / 2
                        points = s1
                        
                        if points > paragraph_high_point:
                            paragraph_high_point = points
                            paragraph_similar = depend
                            paragraph_keyword = token_paragraph
                            
                        if points >= paragraph_min_point:
                            result = {
                                **result,
                                'informed': True,
                            }
                            
                            broke = True
                            break
                if broke:
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
    
    # check blank
    if len(contents) == 0 and show_content:
        result = {
            **result,
            'blank': True,
            'content': contents
        }
        
    return result

# ------------------------ public function
def view_page(
    url,
    lang='ja',
    sleep=2,
    timeout=20,
    verify=False,
    headers=None,
    depends=None,
    separator=None,
    tries_reject=50,
    tries_timeout=3,
    header_xpath=None,
    paragraph_xpath=None,
    content_xpath=None,
    allow_redirects=True,
    header_min_point=0.8,
    paragraph_min_point=0.85,
    
    show_highlight = False,
    show_header = False,
    show_paragraph = False,
    show_content = False,
    
    **requests_options
):
    tried = 0
    agents = []
    
    while True:
        try:
            tried += 1
            user_agent = random.choice(__User_Agents)
            
            while user_agent in agents:
                user_agent = random.choice(__User_Agents)
                
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
            expired = response.headers.get('Expires')
            expired = expired if expired else (response.headers.get('expires') or False)
            expired_obj = {'expired': expired} if expired else {}
            
            if status_code >= 400 and status_code <= 499:
                return __sort_dict({
                    'active': False,
                    'checked': False,
                    **expired_obj,
                    'error': f'Client error responses: {status_code}',
                    'redirected': redirected,
                    'url': response.url,
                    'status': status_code,
                    'tried': tried,
                })
                
            if status_code >= 500 and status_code <= 599:
                return __sort_dict({
                    'active': False,
                    'checked': False,
                    **expired_obj,
                    'error': f'Server error responses: {status_code}',
                    'redirected': redirected,
                    'url': response.url,
                    'status': status_code,
                    'tried': tried,
                })
    
            html = response.content
            highlight = __get_highlight(
                html,
                header_xpath,
                paragraph_xpath,
                content_xpath,
            )
            
            if not (lang == 'ja' or lang == 'en'):
                translate = __Translator(from_lang=lang, to_lang='en')
                
                for key in highlight:
                    for i in range(0, len(highlight[key])):
                        highlight[key][i] = translate.translate(highlight[key][i])
            
            return __sort_dict({
                **__bad_page(
                    highlight,
                    separator,
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
                'url': response.url,
                'status': status_code,
                'tried': tried,
            })

        except Exception as error:                    
            if type(error) == __requests.exceptions.ConnectionError:
                if tried >= tries_reject:
                    return __sort_dict({
                        'active': None,
                        'checked': False,
                        'error': error,
                        'redirected': False,
                        'url': url,
                        'tried': tried
                    })
                __time.sleep(sleep)
                
            else :
                if tried >= tries_timeout:
                    return __sort_dict({
                        'active': None,
                        'checked': False,
                        'error': error,
                        'redirected': False,
                        'url': url,
                        'tried': tried
                    })
