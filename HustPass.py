#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import time
import getpass
import requests
from requests.cookies import cookiejar_from_dict
from urllib.parse import urljoin

import ddddocr
from PIL import Image


class HustPass(object):
    def __init__(self, user, pwd, debug=False) -> None:
        self._user = user
        self._pwd = pwd
        self._debug = debug
        self._session = requests.session()
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

    def _get_base_post_data(self) -> None:
        # get https://pass.hust.edu.cn/cas/login
        # get post data: lt execution _eventId
        # set Cookie [pass.hust.edu.cn] Language JSESSIONID BIGipServerpool-icdc-cas2
        login_url = 'https://pass.hust.edu.cn/cas/login'
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

    def _get_rsa(self) -> None:
        # get post data: rsa
        node_cmd = 'node des {} {} {}'.format(
            self._user, self._pwd, self._post_data['lt'])
        with os.popen(node_cmd) as nodejs:
            self._post_data['rsa'] = nodejs.read().replace('\n', '')

        if self._debug:
            print(sys._getframe().f_code.co_name, self._post_data)

    def _ocr_handle_code(self) -> None:
        ocr = ddddocr.DdddOcr(show_ad=False)
        with Image.open('code.gif') as im:
            num = 0
            try:
                while True:
                    # ????????????
                    im.save('code.png')

                    # OCR ??????
                    with open('code.png', 'rb') as f:
                        tmp = f.read()
                        code = ocr.classification(tmp)
                    os.remove('code.png')
                    if len(code) == 4:
                        code = code.replace('o', '0') # ???????????? 4 ????????????????????????
                        self._post_data['code'] = code
                        break

                    # ???????????????
                    num += 1
                    im.seek(num)
            except EOFError:
                pass  # ?????????????????????

    def _handle_code(self, times) -> None:
        # get post data: code
        code_url = self._next_urls.pop(0)
        code_response = self._session.get(code_url, headers=self._headers)
        with open('code.gif', 'wb') as f:
            f.write(code_response.content)

        if times > 2:
            self._ocr_handle_code()
        else:
            self._post_data['code'] = input('OCR ?????????????????????????????? code.gif ?????????????????????')

        if self._debug:
            print(sys._getframe().f_code.co_name, self._post_data)

    def _post_login(self) -> None:
        # post https://pass.hust.edu.cn/cas/login;jsessionid=abcdefgabcdefgabcdefgabcdefgabcd-abcdefgabcdefgabcde!1234567890
        # set Cookie [pass.hust.edu.cn] Language CASTGC
        # ?????? CASTGC ??????????????? cookie???????????????
        # ???????????? http://one.hust.edu.cn/
        # set Cookie [one.hust.edu.cn] BIGipServerpool-one cookiesession1
        post_url = self._next_urls.pop(0)
        self._session.post(post_url, headers=self._headers, data=self._post_data)

        if self._debug:
            print(sys._getframe().f_code.co_name,
                  self._session.cookies.get_dict())

    def get_cookies(self, bak='cookie.bak') -> requests.cookies.RequestsCookieJar:
        if 0 == len(self._session.cookies.values()):
            if os.path.exists(bak) and (time.time() - os.path.getmtime(bak) < 3600):
                with open(bak, 'r') as f:
                    cookie = json.load(f)
                self._session.cookies = cookiejar_from_dict(cookie)
                if self._valid():
                    print('?????? cookie ???????????????')
                    return self._session.cookies
                else:
                    print('?????? cookie ?????????????????????????????????...')
                    self._session.cookies = cookiejar_from_dict({})
            self._login()

        if self._valid():
            with open(bak, 'w') as f:
                json.dump(self._session.cookies.get_dict(domain='pass.hust.edu.cn'), f)

        return self._session.cookies

    def _valid(self) -> bool:
        # use Cookie get http://one.hust.edu.cn/dcp/forward.action?path=/portal/portal&p=home
        session = requests.session()
        session.cookies = self._session.cookies
        if self._debug:
            print('pass.hust.edu.cn:', session.cookies.get_dict(domain='pass.hust.edu.cn'))
            print('one.hust.edu.cn:', session.cookies.get_dict(domain='one.hust.edu.cn'))

        response = session.get('http://one.hust.edu.cn/dcp/forward.action?path=/portal/portal&p=home')
        response.encoding = 'utf8'
        if self._debug:
            with open('valid.html', 'wb') as f:
                f.write(response.content)

        try:
            name_id = re.findall(r'usernameandidnumber="(\S+)"', response.text)[0]
        except IndexError:
            print('?????? cookie ???????????????????????????????????????')
            print('??????????????????????????????????????????????????? issue ???')
            ret = False
        else:
            print(f'{name_id} ??????????????? cookie ?????????')
            ret = True
        return ret

    def _login(self) -> None:
        try_max_times = 5
        while True:
            self._get_base_post_data()
            self._get_rsa()
            self._handle_code(try_max_times)
            try:
                self._post_login()
            except KeyError:
                print('???????????????! ????????????...')
                pass
            except Exception as err:
                print(type(err), err.args)
            else:
                os.remove('code.gif')
                break
            try_max_times -= 1


if __name__ == '__main__':
    hustPass = HustPass(user=input('?????????'), pwd=getpass.getpass('?????????'))
    cookies = hustPass.get_cookies()
    print(cookies.get_dict(domain='pass.hust.edu.cn'))
