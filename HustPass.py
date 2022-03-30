#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import getpass
import requests

class HustPass(object):
    def __init__(self, user, pwd, debug=False) -> None:
        self._user = user
        self._pwd = pwd
        self._debug = debug
        self._session = requests.session()
        self._headers = {
            'Host': None,
            'Referer': None,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        }

    def get_base_post_data(self) -> dict:
        self._headers['Host'] = 'pass.hust.edu.cn'
        self._headers['Referer'] = 'https://pass.hust.edu.cn/'
        login_response = self._session.get(
            'https://pass.hust.edu.cn/cas/login', headers=self._headers)
        login_response.encoding = 'utf8'
        post_data_list = re.findall(
            r'name="(\S+)" value="(\S+)"', login_response.text)
        post_data = dict(post_data_list)
        post_data['ul'] = len(self._user)
        post_data['pl'] = len(self._pwd)

        if self._debug:
            with open('login.html', 'wb') as f:
                f.write(login_response.content)
            print(post_data)

        return post_data

    def get_rsa(self) -> str:
        return 'ABCDEFG'

    def handle_code(self) -> str:
        return '0000'

    def get_cookies(self, post_data) -> dict:
        return {}

    def run(self) -> dict:
        post_data = self.get_base_post_data()

        rsa = self.get_rsa()
        post_data['rsa'] = rsa

        code = self.handle_code()
        post_data['code'] = code

        return self.get_cookies(post_data)


if __name__ == '__main__':
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'), debug=True)
    cookies = hustPass.run()
    print(cookies)
