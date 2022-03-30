#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import getpass
import requests

class HustPass(object):
    def __init__(self, user, pwd, debug=False) -> None:
        self._user = user
        self._pwd = pwd
        self._debug = debug
        self._session = requests.session()
        self._post_data = {
            'ul': len(self._user),
            'pl': len(self._pwd)
        }
        self._headers = {
            'Host': None,
            'Referer': None,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        }

    def get_base_post_data(self) -> None:
        self._headers['Host'] = 'pass.hust.edu.cn'
        self._headers['Referer'] = 'https://pass.hust.edu.cn/'
        login_response = self._session.get(
            'https://pass.hust.edu.cn/cas/login', headers=self._headers)
        login_response.encoding = 'utf8'
        post_data_list = re.findall(
            r'name="(\S+)" value="(\S+)"', login_response.text)
        self._post_data.update(dict(post_data_list))

        if self._debug:
            with open('login.html', 'wb') as f:
                f.write(login_response.content)
            print(sys._getframe().f_code.co_name, self._post_data)

    def get_rsa(self) -> None:
        node_cmd = 'node des {} {} {}'.format(
            self._user, self._pwd, self._post_data['lt'])
        with os.popen(node_cmd) as nodejs:
            self._post_data['rsa'] = nodejs.read().replace('\n', '')

        if self._debug:
            print(sys._getframe().f_code.co_name, self._post_data)

    def handle_code(self) -> None:
        pass

    def get_cookies(self) -> dict:
        return {}

    def run(self) -> dict:
        self.get_base_post_data()
        self.get_rsa()
        self.handle_code()
        return self.get_cookies()


if __name__ == '__main__':
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'), debug=True)
    cookies = hustPass.run()
    print(cookies)
