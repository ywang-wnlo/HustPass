#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import getpass

class HustPass(object):
	def __init__(self, user, pwd) -> None:
		self.__user = user
		self.__pwd = pwd

	def run(self) -> None:
		pass

if __name__ == '__main__':
	hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'))
	hustPass.run()
