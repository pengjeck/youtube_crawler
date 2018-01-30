# coding: utf-8

import sys
import time

progress_pid = sys.argv[1]


def get_status(pid):
    status = {}
    with open('/proc/{}/status'.format(pid), 'r') as f:
        while True:
            line = f.readline()
            if len(line) < 1:
                break
            parts = line.split(':')
            status[parts[0]] = parts[1].strip()
    return status


def track(pid, times=100, time_span=100):
    for _ in range(times):
        now = time.time()
        print("now: {}\n vmrss:{} \n rssanon:{}\n rssfile:{}".format(now,
                                                                     get_status(pid)['VmRSS'],
                                                                     get_status(pid)['RssAnon'],
                                                                     get_status(pid)['RssFile']))
        time.sleep(time_span)


track(2781)
