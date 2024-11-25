# coding: utf-8

# from youtube import YouTube

# y = YouTube()
# data = y.search('name')
# # data = y.video(['hMtVr9C_2HI'])
# y.save2file(data)
# from youtube import VideoPage, SearchPage
import requests
from config import YConfig, logger


def http_request(video_id):
    video_url = 'https://www.youtube.com/watch?'
    params = {
        'v': video_id
    }
    try:
        req = requests.get(video_url, params=params,
                           proxies=YConfig.PROXIES,
                           timeout=YConfig.TIMEOUT)
        print(req)
        return 0
    except requests.HTTPError as http_e:
        logger.error('network error when request video page. Reason:{}'.format(http_e))
        return -1
    except requests.Timeout as timeout_e:
        logger.error('time out when request video page. {}'.format(timeout_e))
        return -1
    except requests.ConnectionError as connection_e:
        logger.error('connection error occur when request video page. {}'.format(connection_e))
        return -1
    except requests.exceptions.ChunkedEncodingError as chunk_e:
        logger.error('requests.exceptions.ChunkedEncodingError occur {}'.format(chunk_e))
        return 1


req = http_request('yXWGzzwV4zA')
