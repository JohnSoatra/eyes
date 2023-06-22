#!python3
from eyes_soatra.constant.user.user_agents import User_Agents as __agents
from eyes_soatra.constant.area.id import ids as __area_ids
from eyes_soatra.constant.classes import colors as __colors
from eyes_soatra.funcs.view_page import view_page as __view_page
from eyes_soatra.funcs.utils.string import clean_url as __clean_url
from eyes_soatra.funcs.utils.console import clear_console as __clear_console
from eyes_soatra.funcs.utils.console import print_process as __print_process
from eyes_soatra.funcs.utils.time import passed as __passed
from threading import Thread as __Thread

import random as __random
import requests as __requests
import time as __time

__MAX_THREAD_LENGTH = 100
__MAX_WAIT_TIME = 60 * 5

__areas_with_url = []
__got_area_length = 0
__url_length = 0
__checked_url_length = 0
__changes = []

def __end_work(callback, area_length):
    global __areas_with_url
    global __got_area_length
    global __changes
    global __url_length
    global __checked_url_length

    print(f'\n{__colors.OK_GREEN if len(__changes) else ""}--- changed = {len(__changes)}{__colors.END_COLOR}')
    print(f'{__colors.END_COLOR}--- got areas = {len(__areas_with_url)} ({area_length})\n')

    if callback:
        callback(__areas_with_url, __changes)

    __areas_with_url = []
    __got_area_length = 0
    __changes = []
    __url_length = 0
    __checked_url_length = 0
    

def __inform_changes(
    inform_endpoint,
    inform_token,
    data,
    url_inactive,
    wait_time,
):
    changes = { **data, 'url_inactive': url_inactive }
    __changes.append(changes)
    
    if inform_endpoint and inform_token:
        start_time = int(__time.time())
        
        while True:
            try:
                tried += 1
                user_agent = __random.choice(__agents)

                res = __requests.post(
                    url=f'{inform_endpoint}',
                    data=changes,
                    headers = {
                        'Authorization': f'Bearer {inform_token}',
                        'USER-AGENT': user_agent,
                        'ACCEPT' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'ACCEPT-ENCODING' : 'gzip, deflate, br',
                        'ACCEPT-LANGUAGE' : 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,km-KH;q=0.6,km;q=0.5,ja-JP;q=0.4,ja;q=0.3',
                        'REFERER' : 'https://www.google.com/'
                    }
                )

                if res.status_code != 200:
                    return None
                
                data = res.json()
                break

            except:
                if __passed(wait_time or __MAX_WAIT_TIME, start_time):
                    break

def __get_area(
    request_endpoint,
    request_token,
    id,
    random,
    wait_time
):
    tried = 0
    start_time = int(__time.time())

    while True:
        try:
            tried += 1
            user_agent = __random.choice(__agents)

            res = __requests.get(
                url=f'{request_endpoint}/{id}?random={random}',
                headers = {
                    'Authorization': f'Bearer {request_token}',
                    'USER-AGENT': user_agent,
                    'ACCEPT' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'ACCEPT-ENCODING' : 'gzip, deflate, br',
                    'ACCEPT-LANGUAGE' : 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,km-KH;q=0.6,km;q=0.5,ja-JP;q=0.4,ja;q=0.3',
                    'REFERER' : 'https://www.google.com/'
                },
            )
            
            if res.status_code != 200:
                return None
            
            data = res.json()

            if data['status'] and data['data']['urls']:
                return data

            return None

        except:
            if __passed(wait_time or __MAX_WAIT_TIME, start_time):
                break

def __check_changes(area, show_process):
    global __checked_url_length    
    urls = area['data']['urls']

    for i in range(0, len(urls)):
        url = urls[i]
        url = url['url']
        res = __view_page(url)
        __checked_url_length += 1
        __print_process(
            __checked_url_length,
            __url_length,
            show_process,
            prefix='--- checking url: '
        )

        if res['active'] == False:
            if i < len(urls) - 1:
                __checked_url_length += len(urls) - (i + 1)
                __print_process(
                    __checked_url_length,
                    __url_length,
                    show_process,
                    prefix='--- checking url: '
                )

            return url

    return None

def __worker_get_areas(
    request_endpoint,
    request_token,    
    random,
    area_ids,
    area_length,
    start,
    end,
    show_process,
    wait_time,
):
    global __got_area_length
    global __url_length

    for index in range(start, end):
        area_id = area_ids[index]
        area = __get_area(
            request_endpoint,
            request_token,
            area_id,
            random,
            wait_time
        )
        __got_area_length += 1
        __print_process(
            __got_area_length,
            area_length,
            show_process,
            prefix='--- getting url: ',
        )

        if area:
            __areas_with_url.append(area)
            __url_length += len(area['data']['urls'])

def __worker_check_url(
    inform_endpoint,
    inform_token,
    start,
    end,
    show_process,
    wait_time,
):    
    for i in range(start, end):
        area = __areas_with_url[i]
        changed_url = __check_changes(area, show_process)

        if changed_url != None:
            __inform_changes(
                inform_endpoint,
                inform_token,
                area,
                changed_url,
                wait_time
            )

def watch_changes(
    request_endpoint,
    request_token,
    loop=True,
    show_process=True,
    area_ids=None,
    area_length=None,
    random=3,
    rest=0.5,
    wait_time=None,
    max_thread=None,
    inform_endpoint=None,
    inform_token=None,
    callback=None,
):
    request_endpoint = __clean_url(request_endpoint)
    inform_endpoint = inform_endpoint and __clean_url(inform_endpoint)
    area_ids = area_ids or (__random.sample(__area_ids, area_length) if area_length else __area_ids)
    max_thread = max_thread or __MAX_THREAD_LENGTH
    joined = False

    try:
        while loop or not joined:
            __clear_console()
            
            length = len(area_ids)
            row = length if length < max_thread else max_thread
            token = int(length / row)
            threads = []
            joined = True

            for i in range(0, row):
                start = i * token
                end = (start + token) if i < (row - 1) else length
                thread = __Thread(
                    target=__worker_get_areas,
                    kwargs={
                        'request_endpoint': request_endpoint,
                        'request_token': request_token,
                        'random': random,
                        'area_ids': area_ids,
                        'area_length': length,
                        'start': start,
                        'end': end,
                        'show_process': show_process,
                        'wait_time': wait_time,
                    },
                )
                threads.append(thread)

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            length = len(__areas_with_url)

            if length:
                row = length if length < max_thread else max_thread
                token = int(length / row)
                threads = []

                for i in range(0, row):
                    start = i * token
                    end = (start + token) if i < (row - 1) else length
                    thread = __Thread(
                        target=__worker_check_url,
                        kwargs={
                            'inform_endpoint': inform_endpoint,
                            'inform_token': inform_token,
                            'start': start,
                            'end': end,
                            'show_process': show_process,
                            'wait_time': wait_time,
                        },
                    )
                    threads.append(thread)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

            else:
                __print_process(
                    1,
                    1,
                    show_process,
                    prefix='--- checking url: '
                )

            __end_work(callback, len(area_ids))

            if loop:
                __time.sleep(rest * 60)

    except KeyboardInterrupt:
        __end_work(callback, len(area_ids))
