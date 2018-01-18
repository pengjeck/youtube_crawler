"""
youtube request module
"""
# coding: utf-8
import re
import time
from datetime import datetime
import json
import requests
from utilities import youtube_timedecoder, time_rfc3339, record_data
from video import Video
from config import logger, YConfig
from myexception import VideoRemoved


def avatar_url_parse(item, avatar_type):
    """
    :param item: json object
    :param avatar_type: select from in (video, user)
    """
    if avatar_type == 'video':
        thumbnails = item['snippet']['thumbnails']
        if 'high' in thumbnails:
            return thumbnails['high']['url']
        elif 'medium' in thumbnails:
            return thumbnails['medium']['url']
        else:
            return thumbnails['default']['url']
    elif avatar_type == 'user':
        pass


class SearchPage:
    """
    处理请求YouTube搜索页面的返回数据
    """

    def __init__(self, query_string):
        self.query_string = query_string
        self._max_results = YConfig.SEARCH_PAGE_SIZE
        self._after_delta = YConfig.BEFORE_TIMEDELTA
        self.data = None
        self.vid_ids = []
        self.vids = []
        self.key_index = 0

        self.search()
        if self.data is not None:
            self.parse_video()  # 简单的解析视频

    def http_request(self):
        """
        http get for search video page
        :return: 1=>再试一次,0=>没有错误,-1=>不要试了gg算了
        """
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': self.query_string,
            'type': 'video',
            'maxResults': self._max_results,
            'key': YConfig.KEYS[self.key_index],
            'publishedAfter': time_rfc3339(self._after_delta)
        }
        try:
            req = requests.get(search_url, params=params,
                               proxies=YConfig.PROXIES,
                               timeout=YConfig.TIMEOUT)
            self.data = json.loads(req.text)
            if 'error' in self.data:
                error_code = self.data['error']['code']
                if error_code == 403:
                    self.key_index = (self.key_index + 1) % 11
                    return 1  # 示意再试一次
                else:
                    logger.error('error when request search page. error code: {}'.format(error_code))
                    self.data = None
                    return -1
            if 'kind' in self.data and self.data['kind'] != 'youtube#searchListResponse':
                self.data = None
                return 1

            return 0  # 没有错误
        except requests.HTTPError as http_e:
            logger.error('network error when request search. msg:{}'.format(http_e))
            return 1
        except requests.Timeout:
            logger.error('timeout when request search!!!')
            return 1
        except requests.ConnectionError:
            logger.error('connection error when request search!!!')
            return 1
        except requests.exceptions.ChunkedEncodingError as chunk_e:
            logger.error('requests.exceptions.ChunkedEncodingError occur {}'.format(chunk_e))
            return 1

    def search(self):
        """
        search video
        """
        r_code = self.http_request()
        if r_code == 1:
            r_code = self.http_request()
            if r_code != 0:
                self.data = None
        elif r_code == -1:
            pass
        elif r_code == 0:
            pass

    def parse_video(self):
        """
        解析search中video数据
        """
        for item in self.data['items']:
            # youtube api 有时候会返回错误的数据
            if item['id']['kind'] != 'youtube#video':
                continue
            try:
                vid_id = item['id']['videoId']
                vid = Video(vid_id)
                vid.avatar_url = avatar_url_parse(item, 'video')
                vid.des = item['snippet']['description']
                vid.title = item['snippet']['title']
                vid.upload_time = youtube_timedecoder(item['snippet']['publishedAt'])
                self.vids.append(vid)
                self.vid_ids.append(vid_id)
            except TypeError as type_e:
                record_data(item, 'parse_video.json')
                logger.error("[{}] error occur when parsing video, msg:{}".format(datetime.now(), type_e))
            except KeyError as key_e:
                record_data(item, 'parse_video.json')
                logger.error("[{}] error occur when parsing video, msg:{}".format(datetime.now(), key_e))


class VideoPage:
    """
    parse video page content
    """

    def __init__(self, video_id):
        self.video_id = video_id
        self.time = None
        self.views = -1
        self.likes = -1
        self.dislikes = -1
        self.comments = -1
        self.data = ''
        self.is_finish = False
        self.is_removed = False

        self.setup()

    def setup(self):
        """setup"""
        try:
            code = self.http_request()
            if code == 1:
                # 再试一次
                time.sleep(1)
                re_code = self.http_request()
                if re_code == 0:
                    self.parse()
                    self.is_finish = True
                else:
                    self.is_finish = False
            elif code == 0:
                self.parse()
                self.is_finish = True
            else:
                self.is_finish = False
        except ValueError as v_e:
            logger.error('value error occur. Reason:{}'.format(v_e))
            self.is_finish = False
        except VideoRemoved as vr_e:
            self.is_finish = False
            self.is_removed = True
            logger.error('video removed. video id = {}. Reason:{}'.format(self.video_id, vr_e))

    def http_request(self):
        video_url = 'https://www.youtube.com/watch'
        params = {
            'v': self.video_id
        }
        try:
            req = requests.get(video_url, params=params,
                               proxies=YConfig.PROXIES,
                               timeout=YConfig.TIMEOUT)
            self.data = req.text
            return 0
        except requests.HTTPError as http_e:
            logger.error('network error when request video page. Reason:{}'.format(http_e))
            return -1
        except requests.Timeout:
            logger.error('time out when request video page. ')
            return -1
        except requests.ConnectionError:
            logger.error('connection error occur when request video page')
            return 1
        except requests.exceptions.ChunkedEncodingError as chunk_e:
            logger.error('requests.exceptions.ChunkedEncodingError occur {}'.format(chunk_e))
            return 1

    def parse(self):
        # 解析
        self.parse_views()
        self.parse_likes()
        self.parse_dislikes()
        self.parse_comments()

    def parse_views(self):
        """parse view count to self.views"""
        try:
            row_views = re.search('"view_count":"\d+"', self.data)
            if row_views is None:
                if self.data.find('has been removed') != -1:
                    raise VideoRemoved('this video has been removed by the user.')
                elif self.data.find('live stream recording is not available') != -1:
                    raise ValueError('This live stream recording is not available.')
                elif self.data.find('This video contains content from') != -1:
                    raise VideoRemoved('this video contain some thing bad')
                else:
                    raise ValueError('cannot find view_count in self.data')
            row_views = row_views.group(0)[14:-1]
            self.views = int(row_views)
        except AttributeError:
            logger.error('attribution error occur when parsing view')
            record_data(self.data, type='html')

    def parse_likes(self):
        """parse like count to self.likes"""
        try:
            row_likes = re.search('like this video along with [\d,]+ other', self.data)
            if row_likes is None:
                if self.data.find('has been removed') != -1:
                    raise VideoRemoved('this video has been removed by the user.')
                elif self.data.find('live stream recording is not available') != -1:
                    raise ValueError('This live stream recording is not available.')
                else:
                    raise ValueError('cannot find likes in self.data')
            row_likes = row_likes.group(0)
            data = re.search('\d+', row_likes.replace(',', ''))
            if data is None:
                raise ValueError('cannot find likes in sub self.data')

            self.likes = int(data.group(0))
        except AttributeError:
            logger.error('attribution error occur when parsing likes')
            record_data(self.data, type='html')

    def parse_dislikes(self):
        """parse dislike count to self.dislikes"""
        try:
            row_dislikes = re.search('dislike this video along with [\d,]+ other', self.data)
            if row_dislikes is None:
                raise ValueError('cannot find dislikes in self.data')
            row_dislikes = row_dislikes.group(0)
            self.dislikes = int(re.search('\d+', row_dislikes.replace(',', '')).group(0))
        except AttributeError:
            logger.error('attribution error occur when parsing dislikes')
            record_data(self.data, type='html')

    def parse_comments(self):
        """
        do not finish this method
        """
        self.comments = -1


class UserPage:
    def __init__(self, user_id):
        pass

    def setup(self):
        pass

    def user(self, user_id):
        """
        get user's informat
        :param user_id: user's id
        """
        user_url = 'https://www.youtube.com/channel/{}'.format(user_id)
        data = requests.get(user_url, proxies=YConfig.PROXIES)
        return data
