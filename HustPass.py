#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import getpass
import requests

class HustPass(object):
    def __init__(self, user, pwd) -> None:
        self._user = user
        self._pwd = pwd
        self._session = requests.session()
        self._headers = {
            'Host': None,
            'Referer': None,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        }

    def get_base_post_data(self) -> dict:
        post_data = {
            'ul': len(self._user),
            'pl': len(self._pwd),
        }
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
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'))
    cookies = hustPass.run()
    print(cookies)
