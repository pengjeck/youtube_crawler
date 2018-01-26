# coding: utf-8
import subprocess
import time
import atexit
from config import YConfig

command = [
    'python',
    '/home/pj/youtube_crawler/track.py',
    '1'
]
fls = []

for i in range(100):
    command[2] = str(i)
    fl = subprocess.Popen(command)
    fls.append(fl)
    print("{}th progress started pid={}".format(i, fl.pid))
    time.sleep(YConfig.BEFORE_TIMEDELTA)  # 7分钟重新请求一次


def kills():
    for f in fls:
        f.kill()
    print('exit~ all')


atexit.register(kills)

while True:
    q = input()
    if q == 'q':
        break

print('end')
