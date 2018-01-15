# coding: utf-8

# import subprocess
# p = subprocess.run(['python', 'time_consume.py'])
import multiprocessing
import time


def foo():
    name = multiprocessing.current_process().name
    print('Starting {}'.format(name))
    time.sleep(3)
    print('Ending {}'.format(name))


background_process = multiprocessing.Process(name='background_process',
                                             target=foo)
background_process.daemon = True
NO_background_process = multiprocessing.Process(name='NO_background_process',
                                                target=foo)

NO_background_process.daemon = False

background_process.start()
NO_background_process.start()

