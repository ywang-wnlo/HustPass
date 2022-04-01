import getpass
import requests
from lxml import etree
from HustPass import HustPass


class PaperList(object):
    def __init__(self, cookies: requests.cookies.RequestsCookieJar) -> None:
        self._cookies = cookies

    def run(self) -> list:
        session = requests.session()
        session.cookies = self._cookies

        # 利用含有 cookie 的 session 登录
        session.get(
            'https://pass.hust.edu.cn/cas/login?service=http://yjs.hust.edu.cn/ssfw/login_cas.jsp')
        # 再利用已登录的 session 访问含有实际数据网站
        response = session.get(
            'http://yjs.hust.edu.cn/ssfw/xwgl/cggl/lwfbqkdj.do?bdshzt=0')
        response.encoding = 'utf8'

        # 利用 xpath 解析
        page = etree.HTML(response.text)
        table_list = page.xpath('//*[@id="form2"]/div/table')
        table = table_list[0]
        tr_list = table.xpath('.//tr')

        # 处理表头
        title = []
        th_list = tr_list.pop(0).xpath('./th[position()<=6]/text()')
        for th in th_list:
            title.append(th.strip())

        # 与实际数据组合
        paper_list = []
        for tr in tr_list:
            td_list = tr.xpath('./td[position()<=6]/text()')
            paper = {}
            num = 0
            for td in td_list:
                paper[title[num]] = td.strip()
                num += 1
            paper_list.append(paper)

        return paper_list


if __name__ == '__main__':
    hustPass = HustPass(user=input('账号：'), pwd=getpass.getpass('密码：'))
    cookies = hustPass.get_cookies()
    pageList = PaperList(cookies)
    pages = pageList.run()
    print(pages)
