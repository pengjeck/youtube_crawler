# coding: utf-8
from datetime import datetime
import sqlite3
from youtube import SearchPage, parse_video_page
from database import get_session, Tempor
from config import logger, YConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Pool
import sys
import os


class Instance:
    """a track instance for adjust the params"""

    def __init__(self, words, part_index):
        self.sess = get_session(part_index)
        self.video_ids = []
        self._setup(words)
        self.track(is_first=True)

    def _setup(self, words):
        with Pool(YConfig.PROCESSES_NUM) as p:
            search_pages = p.map(SearchPage, words)

        for search_page in search_pages:
            # if this search page is empty
            if search_page.data is None:
                continue

            no_duplication_index = []
            for (part_index, vid) in enumerate(search_page.vids):

                try:
                    self.sess.merge(vid)
                    no_duplication_index.append(part_index)
                except sqlite3.IntegrityError as sqlite_ie:
                    logger.info('video id={} duplicated! msg:{}'.format(vid.video_id,
                                                                        sqlite_ie))
            self.sess.commit()
            self.video_ids.extend([search_page.vid_ids[i]
                                   for i in no_duplication_index])
        # remove some duplicate video in this
        self.video_ids = list(set(self.video_ids))
        self.sess.commit()

    def track(self, is_first=False):
        """
        track video's tempor data
        :param is_first: is the first time to run this data.
        :return:
        """
        if is_first:
            now = datetime.utcnow()
            for video_id in self.video_ids:
                self.sess.add(Tempor(video_id=video_id,
                                     time=now,
                                     views=0,
                                     likes=0,
                                     dislikes=0,
                                     comments=0))
        else:
            now = datetime.utcnow()
            with Pool(YConfig.PROCESSES_NUM) as p:
                video_pages = p.map(parse_video_page, self.video_ids)

            for video_page in video_pages:
                temp = Tempor(video_id=video_page['video_id'],
                              time=now,
                              views=video_page['views'],
                              likes=video_page['likes'],
                              dislikes=video_page['dislikes'],
                              comments=-1)
                self.sess.add(temp)
        self.sess.commit()


def get_words(part_index):
    file_path = YConfig.GOOGLE10000.format(part_index)
    with open(file_path, 'r') as f:
        return f.readline().split('|')


# 全局的变量
job_instance = None


def tick():
    job_instance.track()


def single_scheduler(i):
    global job_instance
    words = get_words(i)
    job_instance = Instance(words, index)
    del words
    scheduler = BlockingScheduler()
    scheduler.add_executor('processpool')
    # scheduler.add_job(tick, 'interval', seconds=200)
    scheduler.add_job(tick, 'interval', seconds=YConfig.TRACK_SPAN)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('process has exit!!!')
        scheduler.shutdown()


index = int(sys.argv[1])
# index = 1
single_scheduler(index)
