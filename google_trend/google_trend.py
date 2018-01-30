# coding: utf-8
import requests
import json
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from datetime import datetime
from sqlalchemy import Column, Integer, create_engine, TEXT, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Instance:
    def __init__(self):
        engine = create_engine('sqlite:///google.db')
        self.ids = None
        self.titles = None
        db_session = sessionmaker(bind=engine)
        self.session = db_session()

    @staticmethod
    def get_ids():
        url1 = 'https://trends.google.com/trends/api/stories/latest'
        params1 = {
            'hl': 'en-US',
            'tz': '-480',
            'cat': 'all',
            'fi': '15',
            'fs': '15',
            'geo': 'US',
            'ri': '300',
            'rs': '15',
            'sort': '0'
        }
        try:
            r1 = requests.get(url1, params=params1, timeout=10)
            if r1.status_code != 200:
                return {
                    'code': 1,
                    'res': []
                }

            r1_data = json.loads(r1.text[5:])
            return {
                'code': 0,
                'res': r1_data['trendingStoryIds'][:99]
            }
        except requests.HTTPError:
            return {
                'code': 1,
                'res': []
            }
        except requests.ConnectionError:
            return {
                'code': 1,
                'res': []
            }

    def get_titles(self):
        """
        通过视频、新闻的id获取标题
        :return:
        """
        url2 = 'https://trends.google.com/trends/api/stories/summary'
        params2 = {
            'hl': 'en-US',
            'tz': '-480',
            'id': self.ids
        }
        res = []
        for i in range(len(self.ids) // 25):
            params2['id'] = self.ids[i * 25: (i + 1) * 25]
            try:
                r2 = requests.get(url2, params=params2, timeout=10)
                data = json.loads(r2.text[5:])
                for item in data['trendingStories']:
                    res.append(item['title'])

            except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
                pass

        params2['id'] = self.ids[len(self.ids) // 25 * 25:]
        r2 = requests.get(url2,
                          params=params2,
                          timeout=10)
        data = json.loads(r2.text[5:])

        for item in data['trendingStories']:
            res.append(item['title'])

        return res

    def update(self):
        date = datetime.utcnow()
        self.ids = Instance.get_ids()['res']
        self.titles = self.get_titles()

        for title in self.titles:
            self.session.add(Trend(title=title, date=date))
        self.session.commit()


Base = declarative_base()


class Trend(Base):
    __tablename__ = 'trend'
    id = Column(Integer, primary_key=True)
    title = Column(TEXT(), nullable=True)
    date = Column(DateTime(), nullable=True)


def tick():
    instance.update()


if __name__ == '__main__':
    instance = Instance()
    # instance.update()
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=300)

    try:
        scheduler.start()
    except (SystemExit, KeyboardInterrupt):
        print('exit')
        scheduler.shutdown()
