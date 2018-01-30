# coding: utf-8

import sys
import time


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


def track(pid, times=100000, time_span=1):
    for _ in range(times):
        print(get_status(pid)['VmRSS'])
        time.sleep(time_span)


track(14730)
