# coding: utf-8

import sqlite3
import os
from user import User
from video import Video
from tempor import Tempor
from config import logger, YConfig


class SqlYoutube:
    """database interface"""

    def __init__(self, index):
        if YConfig.IS_TESTING and os.path.isfile(YConfig.get_db_file(index)):
            os.remove(YConfig.get_db_file(index))

        self.conn = sqlite3.connect(YConfig.get_db_file(index))
        self.cur = self.conn.cursor()
        if YConfig.IS_TESTING:
            self.cur.execute("CREATE TABLE video (video_id TEXT PRIMARY KEY,\
                                                  user_id TEXT,\
                                                  title TEXT,\
                                                  upload_time timestamp,\
                                                  avatar_path TEXT,\
                                                  avatar_url TEXT, \
                                                  des TEXT)")
            self.cur.execute("CREATE TABLE user (user_id TEXT PRIMARY KEY,\
                                                 followers INTEGER,\
                                                 nickname TEXT,\
                                                 avatar_path TEXT,\
                                                 avatar_url TEXT,\
                                                 des TEXT)")
            self.cur.execute("CREATE TABLE tempor (video_id TEXT,\
                                                   time timestamp,\
                                                   views INTEGER,\
                                                   likes INTEGER,\
                                                   dislikes INTEGER,\
                                                   comments INTEGER)")

    def insert(self, obj, is_commit=False):
        """
        insert a object to database.
        """
        if isinstance(obj, Video):
            self._insert_video(obj, is_commit)
        elif isinstance(obj, User):
            self._insert_user(obj, is_commit)
        elif isinstance(obj, Tempor):
            self._insert_tempor(obj, is_commit)
        else:
            raise TypeError('insert should be Video, User, Tempor')

    def _insert_user(self, user_obj, is_commit=False):
        if not isinstance(user_obj, User):
            raise TypeError('expect User object')
        self.cur.execute("INSERT INTO user VALUES(?,?,?,?,?,?)", user_obj.dump())
        if is_commit:
            self.conn.commit()

    def _insert_video(self, video_obj, is_commit=False):
        if not isinstance(video_obj, Video):
            raise TypeError('expect Video object')
        self.cur.execute("INSERT INTO video VALUES(?,?,?,?,?,?,?)",
                         video_obj.dump())
        if is_commit:
            self.conn.commit()

    def _insert_tempor(self, tempor_obj, is_commit=False):
        if not isinstance(tempor_obj, Tempor):
            raise TypeError('expect tempor object')
        self.cur.execute("INSERT INTO tempor VALUES(?,?,?,?,?,?)", tempor_obj.dump())
        if is_commit:
            self.conn.commit()

    def remove_video(self, video_id):
        """
        remove from video table and tempor
        :param video_id: video id
        :return:
        """
        code_1 = self.remove_video_tempor(video_id)
        code_2 = self.remove_video_video(video_id)
        if code_1 == -1 or code_2 == -1:
            return -1

    def remove_video_tempor(self, video_id):
        """
        remove video from tempor table
        :param video_id:
        :return:
        """
        try:
            sql_lan = "delete from tempor where video_id=?"
            res = self.cur.execute(sql_lan, video_id)
            return res.rowcount
        except sqlite3.DatabaseError as db_e:
            logger.error('cannot delete video = {} from tempor table. msg:{}'.format(video_id, db_e))
            return -1

    def remove_video_video(self, video_id):
        """
        remove video from video table
        :param video_id:
        :return:
        """
        try:
            sql_lan = 'delete from video where video_id=?'
            res = self.cur.execute(sql_lan, video_id)
            return res.rowcount
        except sqlite3.DatabaseError as db_e:
            logger.error('cannot delete video = {} from video table msg:{}'.format(video_id, db_e))
            return -1


