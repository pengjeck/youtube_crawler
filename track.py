# coding: utf-8
import time
from datetime import datetime
import sqlite3
from youtube import SearchPage, VideoPage
from database import get_session, Tempor
from config import logger, YConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Pool
import sys
import objgraph
import os
from sqlalchemy.orm.exc import FlushError
from pympler import tracker


class Instance:
    """a track instance for adjust the params"""

    def __init__(self, words, part_index):
        self.sess = get_session(part_index)
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
            objgraph.show_growth()
            with Pool(YConfig.PROCESSES_NUM) as p:
                videos = p.map(VideoPage, self.video_ids)
            objgraph.show_growth()

            now = datetime.utcnow()
            for video in videos:
                if video.is_removed:
                    self.video_ids.remove(video.video_id)
                    continue

                if not video.is_finish:
                    continue

                temp = Tempor(video_id=video.video_id,
                              time=now,
                              views=video.views,
                              likes=video.likes,
                              dislikes=video.dislikes,
                              comments=video.comments)
                self.sess.add(temp)

        self.sess.commit()


def get_words(part_index):
    file_path = YConfig.GOOGLE10000.format(part_index)
    with open(file_path, 'r') as f:
        return f.readline().split('|')


# 全局的变量
job_instance = None
base_words_path = ''
profile_path = 'dataset/profile.txt'


def tick():
    print("===========================")
    time1 = tk.create_summary()
    job_instance.track()
    time2 = tk.create_summary()
    tk.print_diff(time1, time2)
    print("---------------------------")
    objgraph.show_growth()


def single_scheduler(i):
    global job_instance
    words = get_words(i)
    job_instance = Instance(words, index)
    scheduler = BlockingScheduler()
    scheduler.add_executor('processpool')
    scheduler.add_job(tick, 'interval', seconds=100)
    # scheduler.add_job(tick, 'interval', seconds=YConfig.TRACK_SPAN)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('process has exit!!!')
        scheduler.shutdown()


tk = tracker.SummaryTracker()
print(os.getpid())
# index = int(sys.argv[1])
index = 1
single_scheduler(index)
