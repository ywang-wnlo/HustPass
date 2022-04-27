import re
import getpass
import datetime
import requests
from HustPass import HustPass


class CheckMoneyStatus(object):
    def __init__(self, cookies: requests.cookies.RequestsCookieJar) -> None:
        self._cookies = cookies

    def run(self) -> None:
        session = requests.session()
        session.cookies = self._cookies

        # 利用含有 cookie 的 session 登录
        # 含有三次重定向
        # 第一次重定向时，设置 [foa.fiscal.hust.edu.cn] 的 JSESSIONID
        response = session.get(
            'https://pass.hust.edu.cn/cas/login?service=http://foa.fiscal.hust.edu.cn/casNeusoftLogin.action')
        # with open('login.html', 'wb') as f:
        #     f.write(response.content)

        # data = {
        #     # 'Sysid': '0000', # 常用
        #     'Sysid': '1001', # 网上查询
        #     # 'Sysid': '1002', # 收入申报
        #     # 'Sysid': '1015', # 网上报销
        #     'num': '7',
        # }
        # response = session.post('http://foa.fiscal.hust.edu.cn/getMyMenu.action', data=data)
        # with open('qid.html', 'wb') as f:
        #     f.write(response.content)
        # response.encoding = 'utf8'
        # json_dict = response.json()
        # html = json_dict['Menu']
        # page = etree.HTML(html)
        # a_list = page.xpath('//a')
        # qid_dict = {}
        # for a in a_list:
        #     qid = a.xpath('./@id')[0].replace('qid', '')
        #     text = a.xpath('.//text()')[0].strip()
        #     qid_dict[text] = qid
        # print(qid_dict)

        data = {
            # 'qid': '1001101101', # 学生财务信息
            'qid': '1002108101', # 学生个人查询
        }
        response = session.post(
            'http://foa.fiscal.hust.edu.cn/toNewPage.action', data=data)
        # with open('toNewPage.html', 'wb') as f:
        #     f.write(response.content)
        response.encoding = 'utf8'
        json_dict = response.json()
        url = json_dict['url']
        # print(url)

        # 含有一次重定向
        # 设置 [foa.fiscal.hust.edu.cn/wcsys6.0] 的 JSESSIONID
        response = session.get(url)
        response.encoding = 'utf8'
        # with open('NewPage.html', 'wb') as f:
        #     f.write(response.content)

        # 获取可以查询的项目列表
        data = {
            'json': 'HZKJDX'
        }
        response = session.post('http://foa.fiscal.hust.edu.cn/wscx6/getAllFfxmlist.action', data=data)
        data_dict = response.json()
        ffxmdm_list = data_dict['data']

        # 再利用已登录的 session 访问含有实际数据网站
        all_data_list = []
        for ffxmdm in ffxmdm_list:
            data = {
                'json': '[{"csmc":"nian","val":"2022"},{"csmc":"ffxmdm","val":"' +
                        ffxmdm['xmdm'] + '"},{"csmc":"schoolname","val":"HZKJDX"}]'
            }
            # nian 和 schoolname 对应的 val 无实际意义，但是必须有
            response = session.post('http://foa.fiscal.hust.edu.cn/wscx6/getZyfxsbb.action', data=data)
            data_dict = response.json()
            data_list = data_dict['data']
            if type(data_list) is list:
                all_data_list.extend(data_list)

        self.process_data(all_data_list)

    @staticmethod
    def process_data(all_data_list):
        # 获取当前日期，只处理近两个月的数据
        today = datetime.date.today()
        this_month = {
            'year': today.year,
            'month': today.month
        }

        if this_month['month'] == 1:
            diff_year = 1
            diff_month = -11
        else:
            diff_year = 0
            diff_month = 1
        last_month = {
            'year': today.year - diff_year,
            'month': today.month - diff_month
        }

        month_data_dict = {
            '本月': {
                'got_count': 0,
                'got_money_count': 0,
                'pending_count': 0,
                'pending_money_count': 0,
            },
            '上月': {
                'got_count': 0,
                'got_money_count': 0,
                'pending_count': 0,
                'pending_money_count': 0,
            },
        }

        data_list = []
        for data in all_data_list:
            month_data = None
            if int(data['nian']) == this_month['year'] and int(data['yue']) == this_month['month']:
                month_data = month_data_dict['本月']
                data_list.append(data)
            elif int(data['nian']) == last_month['year'] and int(data['yue']) == last_month['month']:
                month_data = month_data_dict['上月']
                data_list.append(data)
            if month_data:
                if data['state'] == '发放成功':
                    month_data['got_count'] += 1
                    month_data['got_money_count'] += data['je']
                else:
                    month_data['pending_count'] += 1
                    month_data['pending_money_count'] += data['je']

        print()
        for key, value in month_data_dict.items():
            print('{} 已发放 {} 笔，共 {} 元，还剩 {} 笔 {} 元未到账'.format(
                key, value['got_count'], value['got_money_count'], value['pending_count'], value['pending_money_count']))

        print('\n以下为本月明细：')
        for data in data_list:
            if int(data['yue']) == this_month['month']:
                print("|-", end='')
                print(data['bmmc'], end='\t')
                print(data['je'], end='\t')
                print(data['state'], end='\t')
                print(data['bz'])
        print('\n以下为上月明细：')
        for data in data_list:
            if int(data['yue']) == last_month['month']:
                print("|-", end='')
                print(data['bmmc'], end='\t')
                print(data['je'], end='\t')
                print(data['state'], end='\t')
                print(data['bz'])

if __name__ == '__main__':
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'))
    cookies = hustPass.get_cookies()
    checkMoneyStatus = CheckMoneyStatus(cookies)
    checkMoneyStatus.run()
