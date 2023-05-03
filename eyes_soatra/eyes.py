#!python3
from eyes_soatra.depends.depends_404 import depends as __depends_no_data
from eyes_soatra.depends.depends_no_data import depends as __depends_404
from translate import Translator as __Translator
from requests_html import HTML as __HTML
import requests as __requests
import jellyfish as __jellyfish
import re as __re

# Suppress only the single warning from urllib3 needed.
__requests.packages.urllib3.disable_warnings()
__requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    __requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

# private global variables

__headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
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
# //h1[self::*//text()]/following-sibling::p[1]|//h1[self::*//text()]/following-sibling::*//p[1]|//*[({self::div or self::span}) and self::*//h1[self::*//text()] and self::*/*[last()=1]]/following-sibling::*[1][{self::div or self::span}]//p[1]
# ---------------------- helpers

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
        
        for header in header_list:
            header = __strip(header)
            
            if len(header) >= __header_min_length:
                header_texts.append(header)
    
    for xpath in __paragraph_xpaths + (paragraph_xpath if type(paragraph_xpath) == list else []):
        paragraph_list = html.xpath(f'({xpath})//text()')
        
        for paragraph in paragraph_list:
            paragraph = __strip(paragraph)
            
            if len(paragraph) >= __paragraph_min_length:
                paragraph_texts.append(paragraph)

        if len(paragraph_texts):
            break
    
    for xpath in __content_xpaths + (content_xpath if type(content_xpath) == list else []):
        content_list = html.xpath(f'({xpath})//text()')
        
        for content in content_list:
            content = __strip(content)
            
            if len(content) > 0:
                content_texts.append(content)

        if len(content_texts):
            break

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
                        s2 = __jellyfish.jaro_winkler_similarity(depend, token_header)
                        
                        points = (s1 + s2) / 2
                        
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
                        s2 = __jellyfish.jaro_winkler_similarity(depend, token_paragraph)
                        
                        points = (s1 + s2) / 2
                        
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
    timeout=10,
    verify=False,
    depends=None,
    separator=None,
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
    try:
        response = __requests.get(
            url,
            timeout=timeout,
            allow_redirects=allow_redirects,
            verify=verify,
            headers=__headers,
            **requests_options
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
                'error': f'Client error responses',
                'redirected': redirected,
                'url': response.url,
                'status': status_code
            })
            
        if status_code >= 500 and status_code <= 599:
            return __sort_dict({
                'active': False,
                'checked': False,
                **expired_obj,
                'error': f'Server error responses',
                'redirected': redirected,
                'url': response.url,
                'status': status_code
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
            'status': status_code
        })

    except Exception as error:
        return __sort_dict({
            'active': False,
            'checked': False,
            'error': error,
            'redirected': False,
            'url': url,
        })
