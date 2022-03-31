#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import getpass
from urllib.parse import urljoin, urlparse
import requests


class HustPass(object):
    def __init__(self, user, pwd, debug=False) -> None:
        self._user = user
        self._pwd = pwd
        self._debug = debug
        self._session = requests.session()
        self._last_url = None
        self._next_urls = []
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
        login_url = 'https://pass.hust.edu.cn/cas/login'
        self._headers['Host'] = 'pass.hust.edu.cn'
        self._headers['Referer'] = 'https://pass.hust.edu.cn/'
        login_response = self._session.get(login_url, headers=self._headers)
        login_response.encoding = 'utf8'
        post_data_list = re.findall(
            r'name="(\S+)" value="(\S+)"', login_response.text)
        self._post_data.update(dict(post_data_list))

        code_suburl = re.findall(
            r'img src="(\S+)" class="ide_code_image"', login_response.text)[0]
        self._next_urls.append(urljoin(login_response.url, code_suburl))

        post_suburl = re.findall(
            r'id="loginForm" action="(\S+)"', login_response.text)[0]
        self._next_urls.append(urljoin(login_response.url, post_suburl))

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
        code_url = self._next_urls.pop(0)
        self._headers['Host'] = 'pass.hust.edu.cn'
        self._headers['Referer'] = 'https://pass.hust.edu.cn/cas/login'
        code_response = self._session.get(code_url, headers=self._headers)
        with open('code.gif', 'wb') as f:
            f.write(code_response.content)
        self._post_data['code'] = input('请手动查看 code.gif 并输入验证码：')

        if self._debug:
            print(sys._getframe().f_code.co_name, self._post_data)

    def post_login(self) -> None:
        post_url = self._next_urls.pop(0)
        self._headers['Host'] = 'pass.hust.edu.cn'
        self._headers['Referer'] = 'http://pass.hust.edu.cn'
        post_response = self._session.post(
            post_url, headers=self._headers, data=self._post_data, allow_redirects=False)
        self._next_urls.append(post_response.headers['Location'])

        if self._debug:
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def stage1_redirect(self) -> None:
        redirect_url = self._next_urls.pop(0)
        parse = urlparse(redirect_url)
        self._headers['Host'] = parse.hostname
        self._headers['Referer'] = None
        redirect_response = self._session.get(
            redirect_url, headers=self._headers, allow_redirects=False)
        redirect_response.encoding = 'utf8'
        refresh_suburl = re.findall(r'url=(\S+)"', redirect_response.text)[0]
        self._next_urls.append(urljoin(redirect_response.url, refresh_suburl))
        self._last_url = redirect_url

        if self._debug:
            with open('stage1_redirect.html', 'wb') as f:
                f.write(redirect_response.content)
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def stage2_refresh(self) -> None:
        refresh_url = self._next_urls.pop(0)
        parse = urlparse(refresh_url)
        self._headers['Host'] = parse.hostname
        self._headers['Referer'] = self._last_url
        refresh_response = self._session.get(
            refresh_url, headers=self._headers, allow_redirects=False)
        self._next_urls.append(refresh_response.headers['Location'])

        if self._debug:
            print(refresh_response.headers['Location'])
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def handle_redirect(self) -> requests.Response:
        redirect_url = self._next_urls.pop(0)
        parse = urlparse(redirect_url)
        self._headers['Host'] = parse.hostname
        self._headers['Referer'] = self._last_url
        redirect_response = self._session.get(
            redirect_url, headers=self._headers, allow_redirects=False)
        return redirect_response

    def stage3_redirect(self) -> None:
        response = self.handle_redirect()
        self._next_urls.append(response.headers['Location'])

        if self._debug:
            print(response.headers['Location'])
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def stage4_redirect(self) -> None:
        response = self.handle_redirect()
        self._next_urls.append(response.headers['Location'])

        if self._debug:
            print(response.headers['Location'])
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def stage5_redirect(self) -> None:
        response = self.handle_redirect()
        response.encoding = 'utf8'
        refresh_suburl = re.findall(r'url=(\S+)"', response.text)[0]
        self._next_urls.append(urljoin(response.url, refresh_suburl))
        self._last_url = response.url

        if self._debug:
            with open('stage5_redirect.html', 'wb') as f:
                f.write(response.content)
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def stage6_refresh(self) -> None:
        refresh_url = self._next_urls.pop(0)
        parse = urlparse(refresh_url)
        self._headers['Host'] = parse.hostname
        self._headers['Referer'] = self._last_url
        refresh_response = self._session.get(
            refresh_url,  headers=self._headers, allow_redirects=False)

        if self._debug:
            with open('stage6_refresh.html', 'wb') as f:
                f.write(refresh_response.content)
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def get_cookies(self) -> requests.cookies.RequestsCookieJar:
        return self._session.cookies

    def run(self) -> dict:
        self.get_base_post_data()
        self.get_rsa()
        self.handle_code()
        self.post_login()
        self.stage1_redirect()
        self.stage2_refresh()
        self.stage3_redirect()
        self.stage4_redirect()
        self.stage5_redirect()
        self.stage6_refresh()
        return self.get_cookies()


if __name__ == '__main__':
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'), debug=True)
    cookies = hustPass.run()
    print('pass.hust.edu.cn:', cookies.get_dict(domain='pass.hust.edu.cn'))
    print('one.hust.edu.cn:', cookies.get_dict(domain='one.hust.edu.cn'))
