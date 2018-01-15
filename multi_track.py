"""
track diff video's data and save to database with multiprocess
"""
# coding: utf-8
import subprocess
import time
import atexit

command = [
    '/home/pj/datum/GraduationProject/pyenv/bin/python',
    '/home/pj/datum/GraduationProject/code/youtube/track.py',
    '1'
]
fls = []
# TODO: 要改进的地方，检测程序是否已经退出，然后主程序退出的话，记得kill其他的程序。
for i in range(100):
    command[2] = str(i)
    fl = subprocess.Popen(command)
    fls.append(fl)
    print("{}th progress started pid={}".format(i, fl.pid))
    time.sleep(200)


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
