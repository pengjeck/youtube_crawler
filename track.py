"""
track diff video's data and save to database
"""
# coding: utf-8
import time
from datetime import datetime
import sqlite3
from youtube import SearchPage, VideoPage
from database import SqlYoutube
from tempor import Tempor
from config import logger, YConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Pool
import sys


class Instance:
    """a track instance for adjust the params"""

    def __init__(self, words, index):
        self.db = SqlYoutube(index)
        self.video_ids = []
        self._words = words
        self._setup()
        self.track(is_first=True)

    def _setup(self):
        with Pool(YConfig.PROCESSES_NUM) as p:
            search_pages = p.map(SearchPage, self._words)

        for search_page in search_pages:
            # if this search page is empty
            if search_page.data is None:
                continue

            no_duplication_index = []
            for (index, vid) in enumerate(search_page.vids):
                try:
                    self.db.insert(vid, is_commit=False)
                    no_duplication_index.append(index)
                except sqlite3.IntegrityError as sqlite_ie:
                    logger.info('video id={} duplicated! msg:{}'.format(vid.video_id,
                                                                        sqlite_ie))
            self.db.conn.commit()
            self.video_ids.extend([search_page.vid_ids[index]
                                   for index in no_duplication_index])
        # remove some duplicate video in this
        self.video_ids = list(set(self.video_ids))

    def track(self, is_first=False):
        """
        track video's tempor data
        :param is_first: is the first time to run this data.
        :return:
        """
        # print('run track')
        if is_first:
            for video_id in self.video_ids:
                temp = Tempor(video_id, datetime.utcnow(), 0, 0, 0, 0)
                self.db.insert(temp, is_commit=False)
        else:
            beg = time.time()

            with Pool(YConfig.PROCESSES_NUM) as p:
                videos = p.map(VideoPage, self.video_ids)

            for video in videos:
                # assert isinstance(video, VideoPage)
                if not video.is_finish:
                    continue

                temp = Tempor(video.video_id, datetime.utcnow(), video.views,
                              video.likes, video.dislikes,
                              video.comments)
                self.db.insert(temp, is_commit=False)

            logger.info("[{}] round with {} video cost: {}".format(
                datetime.now(), len(self.video_ids),
                time.time() - beg))
        self.db.conn.commit()
        # print('tracked')

    def search_test(self):
        temp_video_ids = []
        for word in self._words:
            search_page = SearchPage(word)
            temp_video_ids.extend(search_page.vid_ids)
        print(list(set(temp_video_ids)))
        # self.video_ids = list(set(self.video_ids))


# 全局的变量
job_instance = None
base_words_path = ''


def tick():
    job_instance.track()


def get_words(index):
    file_path = '/home/pj/datum/GraduationProject/dataset/google-10000-english/parts/part{}_google_10000.txt'.format(
        index)
    with open(file_path, 'r') as f:
        return f.readline().split('|')


def single_scheduler(i):
    global job_instance
    words = get_words(i)
    job_instance = Instance(words, index)
    scheduler = BlockingScheduler()
    scheduler.add_executor('processpool')
    # scheduler.add_job(tick, 'interval', seconds=200)
    scheduler.add_job(tick, 'interval', seconds=YConfig.TRACK_SPAN)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('background process has exit!!!')
        scheduler.shutdown()


index = int(sys.argv[1])
# index = 0
single_scheduler(index)
