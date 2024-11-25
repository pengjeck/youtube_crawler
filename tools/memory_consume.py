# coding: utf-8
import time
import sys
import os

print(os.getpid())

my_list = []
for i in range(1000):
    for j in range(1000):
        my_list.append(j)
    time.sleep(2)
    print(sys.getsizeof(my_list))
