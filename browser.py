#!/usr/bin/env python
# -*- coding: utf-8

import pickle
import os
import sys
import requests


class Browser(object):
    """
    浏览器
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.90 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        self.root_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    def load_cookies(self, path):
        with open(path, 'rb') as f:
            self.session.cookies = requests.utils.cookiejar_from_dict(pickle.load(f))

    def save_cookies(self, path):
        with open(path, 'wb') as f:
            cookies_dic = requests.utils.dict_from_cookiejar(self.session.cookies)
            pickle.dump(cookies_dic, f)

    def get(self, url, params):
        """
        http get
        """
        pass
        try:
            response = self.session.get(url, params=params, timeout=200)
            return response
        except Exception as e:
            print(repr(e))

    def post(self, url, data):
        """
        http post
        """
        try:
            response = self.session.post(url, data=data, timeout=200)
            return response
        except Exception as e:
            print(repr(e))
