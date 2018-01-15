# coding: utf-8

google_10000_path = '/home/pj/datum/GraduationProject/dataset/google-10000-english/google-10000-english.txt'

google_1000 = open(google_10000_path, 'r')


def read_google_10000_english(num):
    """
    get diff word from google 10000 english database
    :params num: word's number wanting to use
    """
    if not isinstance(num, (str, int)):
        raise TypeError('expect "all" string or num')

    res = []
    if num == 'all':
        with open(google_10000_path, 'r') as google_f:
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
        with open(google_10000_path, 'r') as google_f:
            for _ in range(num):
                line = google_f.readline().strip()
                res.append(line)
    return res


all_words = read_google_10000_english('all')
part_path = 'parts/part{}_google_10000.txt'

for i in range(100):
    with open(part_path.format(i), 'x') as f:
        f.write('|'.join(all_words[i * 100: (i + 1) * 100]))

google_1000.close()
