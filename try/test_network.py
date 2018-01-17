# coding: utf-8
import time
import requests
from datetime import datetime
import atexit

proxies = {
    'http': 'socks5://127.0.0.1:1081',
    'https': 'socks5://127.0.0.1:1081'
}
url = 'http://www.youtube.com'

f = open('log_youtube.txt', 'a')


def add_record(msg):
    line = "{} : {}".format(datetime.now(), msg)
    f.write(line)


def send(video_id):
    global count
    video_url = 'https://www.youtube.com/watch?'
    params = {
        'v': video_id
    }
    try:
        req = requests.get(video_url, params=params,
                           proxies=proxies,
                           timeout=1)
        count += 1
        print('{}th round finished!'.format(count))
    except requests.Timeout:
        add_record('time out')
    except requests.HTTPError:
        add_record('http error')
    except requests.ConnectionError:
        add_record('connection error')
    except requests.exceptions.ChunkedEncodingError:
        add_record('chunked encoding error')


def if_exit():
    f.close()


atexit.register(if_exit)
count = 0
while True:
    send('yXWGzzwV4zA')
    time.sleep(1)
