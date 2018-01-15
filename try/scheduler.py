"""
Demonstrates how to schedule a job to be run in a process pool on 3 second intervals.
"""
# coding: utf-8

from datetime import datetime
import time
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


def tick():
    time.sleep(3)
    print('Tick! The time is: %s' % datetime.now())


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_executor('processpool')
    scheduler.add_job(tick, 'interval', seconds=10)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
