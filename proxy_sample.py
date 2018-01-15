# coding: utf-8

import requests
from datetime import datetime, timedelta


def read_google_10000_use_file():
    words = []
    file_path = '/home/pj/datum/GraduationProject/dataset/google-10000-english' \
                '/google-10000-english-no-swears.txt'
    with open(file_path, 'r') as f:
        words.append(f.readline()[:-1])
    return words


proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}
key = 'AIzaSyDAa3uq-6FvLYcnU0_KA3Z6TOXSFRXnEqU'
params = {
    'part': 'snippet',
    'q': 'boating',
    'type': 'video',
    'maxResults': '5',
    'key': key,
    'publishedAfter': (datetime.now() - timedelta(days=2)).isoformat('T')[:-7] + 'Z'
}


google_url = 'https://www.google.com'
search_url = "https://www.googleapis.com/youtube/v3/search"
video_url = 'https://www.youtube.com/watch?v=hMtVr9C_2HI'
sample_url = 'https://www.baidu.com/'
user_url = 'https://www.youtube.com/channel/UC0k173Oca1nPZurW2ITHlYw'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
    'x-chrome-uma-enabled': '1',
    'x-client-data': 'CIq2yQEIprbJAQj6nMoBCKmdygEIqKPKAQ==',

}
beg = datetime.now()
r = requests.get(search_url, proxies=proxies, params=params)
# r = requests.get(sample_url, proxies=proxies)
print(datetime.now() - beg)
with open('test.json', 'w') as f:
    f.write(r.text)
