# coding: utf-8

import sqlite3
from config import YConfig


class Video:
    video_id = ''  # id
    views = -1  # 浏览量
    likes = -1  # 点赞数
    dislikes = -1  # 踩
    user_id = ''
    video_title = ''
    video_upload_time = ''
    video_avatar = ''

    def __init__(self, video_id):
        self.video_id = video_id
    
    def insert(self):
        pass

conn = sqlite3.connect(YConfig.DB_FILE)  # 连接到内存数据库
cur = conn.cursor()
cur.execute(
    'CREATE TABLE video (video_id TEXT, views INTEGER, likes INTEGER, dislikes INTEGER)')

p = Video('123')
cur.execute("INSERT INTO video VALUES (?)", (p,))
print(cur.fetchone()[0])
