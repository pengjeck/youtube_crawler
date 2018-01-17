"""
toolbox
"""
# conding: utf-8
import json
from datetime import datetime
import re
from config import YConfig


def time_rfc3339(delta, now=None):
    """
    get rfc3339 time format
    :param delta:
    :param now: now
    :return: string
    """
    if now is None:
        now = datetime.utcnow()
    return (now - delta).isoformat('T')[:-7] + 'Z'


# def to_utc(date):
#     """convert datetime's timezone to utc"""
#     return date.astimezone(timezone('utc'))


def youtube_timedecoder(time_str):
    """
    parse youtube time string
    :param time_str: time string for parse
    """
    try:
        parts = re.split('[-T:.]+', time_str)[:-1]
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        hour = int(parts[3])
        minute = int(parts[4])
        second = int(parts[5])
        return datetime(year, month, day, hour, minute, second)
    except TypeError:
        return None


def json2file(data, filename='test.json'):
    """
    :param data: json
    :param filename:
    :return:
    """
    if isinstance(data, str):
        data = json.loads(data)
    with open(filename, 'w') as f:
        json.dump(data, f)


def record_data(data, type='json', filename='default'):
    """
    record lastest data before exception appear.
    """
    if filename == 'default':
        if type == 'json':
            filename = 'json.json'
        elif type == 'html':
            filename = 'html.html'
        else:
            raise ValueError('record data s file type must be json or html')

    if isinstance(data, str):
        with open(filename, 'w') as f:
            f.write(data)
    elif isinstance(data, dict):
        with open(filename, 'w') as f:
            json.dump(data, f)
    else:
        with open(filename, 'w') as f:
            f.write(str(data))


def read_google_10000_english(num):
    """
    get diff word from google 10000 english database
    :params num: word's number wanting to use
    """
    if not isinstance(num, (str, int)):
        raise TypeError('expect "all" string or num')

    res = []
    if num == 'all':
        with open(YConfig.GOOGLE10000ENGLISH, 'r') as google_f:
            while True:
                line = google_f.readline().strip()
                if len(line) < 1:
                    break
                else:
                    res.append(line)
    else:
        if num < 0:
            raise ValueError('"num" expect a positive number')

        if num >= 10000:
            num = 'all'
        with open(YConfig.GOOGLE10000ENGLISH, 'r') as google_f:
            for _ in range(num):
                line = google_f.readline().strip()
                res.append(line)
    return res


def read_google_10000_range(beg_index, end_index):
    """
    read google 10000 range from beg_index to end_index
    :param beg_index:
    :param end_index:
    :return:
    """
    if end_index < beg_index:
        raise ValueError('end_index must bigger than beg_index')

    if end_index > 10000:
        raise ValueError('end_index must smaller than 10000')
    if end_index == beg_index:
        return []

    res = []
    with open(YConfig.GOOGLE10000ENGLISH, 'r') as google_f:
        count = 0
        while True:
            line = google_f.readline()
            count += 1
            if count >= beg_index:
                res.append(line)

            if count == end_index:
                break
    return res
