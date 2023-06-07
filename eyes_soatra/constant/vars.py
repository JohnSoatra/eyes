from lxml import etree as __etree

main_tags = (
    'title',
    'h1',
    'h2'
)

header_xpaths = [
    '//title',
    '//h1',
    '//h2',
    '//h3',
    '//h4',
    '//h5',
    '//h6',
    '//p',

    '//table',
    '//div',
    '//span',

    '//ul',
    '//dl',
    '//li',
    '//dt',
    '//dd',

    '//tr',
    '//th',
    '//td',
]

description_xpath = [
    '//p',
    
    '//div',
    '//span',
    
    '//li',
    '//dd',
    
    '//tr',
    '//th',
    '//td',
]

priority_tag = [
    'p'
]

priority_header_tag = [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
]

remove_tags = [
    __etree.Comment,
    'script',
    'link',
    'style',
    'button',
]

full_stops = (
    '.',
    '。',
)

xpath_prefix = (
    '/',
    '.'
)

tag_stop = (
    '[',
    ')'
)

protocols = (
    'http://',
    'https://',
)