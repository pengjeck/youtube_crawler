# coding: utf-8
import re
from datetime import datetime
import json
import requests
from utilities import youtube_timedecoder, time_rfc3339, record_data
from database import Video
from config import logger, YConfig


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
            'publishedAfter': time_rfc3339(YConfig.BEFORE_TIMEDELTA)
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
                vid = Video(video_id=vid_id,
                            user_id='',
                            title=item['snippet']['title'],
                            upload_time=youtube_timedecoder(item['snippet']['publishedAt']),
                            avatar_path='',
                            avatar_url=avatar_url_parse(item, 'video'),
                            des=item['snippet']['description'])

                self.vids.append(vid)
                self.vid_ids.append(vid_id)
            except TypeError as type_e:
                record_data(item, 'parse_video.json')
                logger.error("[{}] error occur when parsing video, msg:{}".format(datetime.now(), type_e))
            except KeyError as key_e:
                record_data(item, 'parse_video.json')
                logger.error("[{}] error occur when parsing video, msg:{}".format(datetime.now(), key_e))


def parse_video_page(video_id):
    """
    解析视频页面
    :param video_id:
    :return:0：代表没有错误
            1：代表views没有错误
            2：代表views出现了错误，其他的不做判断
    """
    res = {
        'video_id': video_id,
        'code': 2,
        'views': -1,
        'likes': -1,
        'dislikes': -1
    }
    try:
        video_url = 'https://www.youtube.com/watch'
        params = {
            'v': video_id
        }
        req = requests.get(video_url, params=params,
                           proxies=YConfig.PROXIES,
                           timeout=YConfig.TIMEOUT)
        if req.status_code != 200:
            return res
        data = req.text
        # region for views and check some error
        try:
            raw_views = re.search('"view_count":"\d+"', data)
            if raw_views is None:
                if data.find('has been removed') != -1:
                    logger.error('video has been removed!!!')
                    return res
                elif data.find('live stream recording is not available') != -1:
                    logger.error('This live stream recording is not available.')
                    return res
                elif data.find('This video contains content from') != -1:
                    logger.error('this video contain some thing bad')
                    return res
                else:
                    logger.error('cannot find view_count in self.data')
                    return res
            res['views'] = int(raw_views.group(0)[14:-1])
            res['code'] = 1  # view没有错误
        except AttributeError:
            return res
        except ValueError:
            return res

            # endregion for view

        # region for likes
        raw_likes = re.search('like this video along with [\d,]+ other', data)
        raw_likes = raw_likes.group(0)
        data = re.search('\d+', raw_likes.replace(',', ''))
        if data is None:
            res['likes'] = -1
        else:
            res['likes'] = int(data.group(0))

        # endregion for dislikes

        # region for dislikes

        raw_dislikes = re.search('dislike this video along with [\d,]+ other', data)
        if raw_dislikes is None:
            res['dislikes'] = -1
        else:
            row_dislikes = raw_dislikes.group(0)
            res['dislikes'] = int(re.search('\d+', row_dislikes.replace(',', '')).group(0))

        # endregion for dislikes
        res['code'] = 0  # 没有错误
        return res
    except requests.HTTPError as http_e:
        logger.error('network error: Reason:{}'.format(http_e))
        res['code'] = 2
        return res
    except requests.ConnectionError as connection_e:
        logger.error('network error: Reason:{}'.format(connection_e))
        res['code'] = 2
        return res
    except requests.Timeout as timeout_e:
        logger.error('network error: Reason:{}'.format(timeout_e))
        res['code'] = 2
        return res
    except requests.exceptions.ChunkedEncodingError as chunked_e:
        logger.error('network error: Reason: {}'.format(chunked_e))
        res['code'] = 2
        return res
    except ValueError as v_e:
        logger.error('value error occur. Reason:{}'.format(v_e))
        return res
    except AttributeError as attr_e:
        logger.error('attribute error occur. reason: {}'.format(attr_e))
        return res


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
        data = requests.get(user_url)
        return data
