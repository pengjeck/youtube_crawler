"""
config module
"""
# coding: utf-8

import logging
import time
import os
from datetime import timedelta


class YConfig:
    """
    youtube crawler config file
    """
    DB_FILE = '/home/pj/dataset/youtube/database/youtube_{}.db'

    @staticmethod
    def get_db_file(index):
        """
        get different index's database file path
        :param index:
        :return:
        """
        # 建立100个数据库，这里的设定是，不同的数据库可能跟踪到了相同视频信息
        return YConfig.DB_FILE.format(index)

    USER_AVATAR_PATH = '/home/pj/dataset/youtube/user_avatar/'
    VIDEO_AVATAR_PATH = '/home/pj/dataset/youtube/video_avatar/'
    LOGGING_PATH = '/home/pj/dataset/youtube/logging/'

    GOOGLE10000 = '/home/pj/youtube_crawler/google_10000/part{}_google_10000.txt'
    IS_TESTING = True

    # key 应该是够用的
    KEYS = [
        'AIzaSyDAa3uq-6FvLYcnU0_KA3Z6TOXSFRXnEqU',  # video recommendation
        'AIzaSyCQWdKweqaCVGyEpgQa5d8_4OR-RczPJE4',  # pensirApp
        'AIzaSyA1z6VLsmr8k8LvFViFTQ5Oz3Z21rCc5Io',  # My Project
        'AIzaSyAQHRMz1MSv2RgoREeluZitmsmJhn_Jpt0',  # 2
        'AIzaSyArkDhQRSIpR2-_8bqHL0v937zysW8fsVs',  # 3
        'AIzaSyBt8hvxDcYUneEbJFWvpmV34YO23LklFZs',  # 4
        'AIzaSyAWQw5K2SuzIEI42wogBDwFDIAuZeYPE0o',  # 5
        'AIzaSyCIm7BK-KxkEktj8neHSvAmDo5UVW7sZHE',  # 6
        'AIzaSyDLnH4pmQTE9s0nuh1ApYs-RyD9qCOCc1Q',  # 7
        'AIzaSyCC1joQQWQzjss0Lf4eP52jhRUTYfUdj5I',  # 8
        'AIzaSyDWwi4ccCyJyJ3KSFMxd-gl1A19ZKjVh4o'  # 9
    ]

    SEARCH_PAGE_SIZE = 15  # youtube search api page size

    TRACK_SPAN = 900  # 15 * 60 = 900 minute. 默认15分钟记录一次
    TIMEOUT = 3  # 4秒的超时时间

    BEFORE_TIMEDELTA = timedelta(minutes=7)  # 7分钟

    PROCESSES_NUM = 30  # pool(30)

    @staticmethod
    def logging_file():
        """
        get logging file full path
        """
        return os.path.join(YConfig.LOGGING_PATH, '{}.txt'.format(int(time.time())))


logger = logging.getLogger('base')
formatter = logging.Formatter('%(asctime)s - %(message)s')

fh = logging.FileHandler(YConfig.logging_file())
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
