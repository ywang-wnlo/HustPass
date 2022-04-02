import re
# import json
import getpass
import datetime
import requests
# from lxml import etree
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
            'qid': '1001101101',  # 学生财务信息
            # 'qid': '1002108101', # 学生个人查询
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
        zyflist = re.findall(r'zyflistSource = \[(.+?)\];', response.text, re.DOTALL)
        zyflist = zyflist[0]
        code2text_list = re.findall(r"label: '(\S+)', value: '(\S+)'", zyflist)
        code2text_dict = {}
        for code2text in code2text_list:
            code2text_dict[code2text[1]] = code2text[0]

        # 再利用已登录的 session 访问含有实际数据网站
        data = {
            'filterscount': '0',
            'groupscount': '0',
            'pagenum': '0',
            'pagesize': '20',
            'recordstartindex': '0',
            'recordendindex': '20',
            'condition': '{"year_s":"","year_e":""}' # 起始年月
        }
        response = session.post('http://foa.fiscal.hust.edu.cn/wcsys6.0/getXszyfmx.action', data=data)
        data_dict = response.json()
        xszyfmx_list = data_dict['xszyfmx']

        self.process_data(xszyfmx_list, code2text_dict)

    @staticmethod
    def process_data(xszyfmx_list, code2text_dict):
        # 获取当前日期，只处理近两个月的数据
        today = datetime.date.today()
        this_month = datetime.date(today.year, today.month, 1)
        # print(this_month)

        if this_month.month == 1:
            diff_year = 1
            diff_month = -11
        else:
            diff_year = 0
            diff_month = 1
        last_month = datetime.date(today.year - diff_year, today.month - diff_month, 1)
        # print(last_month)

        # 处理数据
        data_list = []
        for xszyfmx in xszyfmx_list:
            one_line = {}
            for key, value in xszyfmx.items():
                if key in code2text_dict.keys():
                    one_line[code2text_dict[key]] = value
            data_list.append(one_line)
            input_date = datetime.date.fromisoformat(one_line['录入日期'])
            one_line['录入日期'] = input_date
            credit_date = datetime.date.fromisoformat(one_line['凭证日期'])
            one_line['凭证日期'] = credit_date
            if input_date < last_month:
                break
            # print(one_line['年'], one_line['月'], one_line['发放项目'], one_line['实发金额'], one_line['录入日期'], one_line['凭证日期'], one_line['摘要'])

        # with open('data.json', 'w') as f:
        #     json.dump(data_list, f, ensure_ascii=False)

        month_data_dict = {
            '本月': {
                'input_count': 0,
                'input_money_count': 0,
                'credit_count': 0,
                'credit_money_count': 0,
            },
            '上月': {
                'input_count': 0,
                'input_money_count': 0,
                'credit_count': 0,
                'credit_money_count': 0,
            },
        }
        for data in data_list:
            if data['录入日期'] > this_month:
                month_data = month_data_dict['本月']
            else:
                month_data = month_data_dict['上月']
            month_data['input_count'] += 1
            month_data['input_money_count'] += data['实发金额']
            if data['凭证日期'] <= today:
                month_data['credit_count'] += 1
                month_data['credit_money_count'] += data['实发金额']

        for key, value in month_data_dict.items():
            print('{} 录入 {} 笔，共 {} 元，其中 {} 笔 {} 元已生成凭证，还剩 {} 笔 {} 元未到账'.format(
                key, value['input_count'], value['input_money_count'], value['credit_count'],
                value['credit_money_count'], value['input_count'] - value['credit_count'], 
                value['input_money_count'] - value['credit_money_count'])
                )

        print('以下为近两月明细：')
        for data in data_list:
            if data['录入日期'] > this_month:
                print('本月：', end='')
            else:
                print('上月：', end='')
            print('【{}】 \t{}\t元 \t{} 录入，{} 生成凭据，摘要：{}'.format(
                data['发放项目'].split('-')[0], data['实发金额'], data['录入日期'], data['凭证日期'], data['摘要']))

if __name__ == '__main__':
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'))
    cookies = hustPass.get_cookies()
    checkMoneyStatus = CheckMoneyStatus(cookies)
    checkMoneyStatus.run()
