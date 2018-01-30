# coding: utf-8
import subprocess
import time
import atexit
from config import YConfig
import sys

command = [
    'pyenv/bin/python',
    'track.py',
    '1'
]

fls = []
beg_index = int(sys.argv[1])
end_index = int(sys.argv[2])
for i in range(beg_index, end_index):
    command[2] = str(i)
    fl = subprocess.Popen(command)
    fls.append(fl)
    print("{}th progress started pid={}".format(i, fl.pid))
    time.sleep(YConfig.BEFORE_TIMEDELTA.seconds)  # 7分钟重新请求一次
    # time.sleep(200)


def kills():
    for f in fls:
        f.kill()
    print('exit~ all')


atexit.register(kills)

while True:
    time.sleep(10000)
    print('part')
