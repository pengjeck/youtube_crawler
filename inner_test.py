# coding: utf-8

# from youtube import YouTube

# y = YouTube()
# data = y.search('name')
# # data = y.video(['hMtVr9C_2HI'])
# y.save2file(data)
# from youtube import VideoPage, SearchPage

# import requests

# proxies = {
#     'http': 'socks5://127.0.0.1:1080',
#     'https': 'socks5://127.0.0.1:1080'
# }

# video_url = 'https://www.youtube.com/watch'
# params = {
#     'v': '2LJeleeZj-E'
# }
# data = requests.get(video_url, params=params, proxies=proxies)
# with open('test.json', 'w') as f:
#     f.write(data.text)
# VideoPage('2LJeleeZj-E')

# s = SearchPage('the')


from track import single_scheduler

from utilities import read_google_10000_english
from track import single_scheduler
import time
import sys
from multiprocessing import Process

words = read_google_10000_english('all')

for i in range(10):
    words_10 = words[i * 10: (i + 1) * 10]
    p = Process(single_scheduler, kwargs={'words': words_10, 'index': i})
    p.daemon = True
    p.start()

if len(sys.argv) != 3:
    print('error, must give 2 range in (0, 100) bound; given {}'.format(len(sys.argv)))
    exit()
else:
    print(sys.argv)
    for i in range(int(sys.argv[1]), int(sys.argv[2])):
        beg = time.time()
        word_100 = words[i * 100:(i + 1) * 100]
        single_scheduler(word_100, i)
        print("the {}th process is running!".format(i + 1))
        time.sleep(600 - (time.time() - beg))  # 10分钟走一波
