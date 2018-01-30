# coding: utf-8
from youtube import SearchPage
from utilities import record_data


class SearchTest:
    def __init__(self, q):
        self.q = q

    def test_search(self):
        search_page = SearchPage(self.q)
        # print(search_page.data)
        record_data(search_page.data)


s = SearchTest('the')
s.test_search()
