import random
import datetime
import requests
from lxml import etree


class CheckElectricUsage(object):
    # @programId: 宿舍区
    # @txtyq: 宿舍楼栋
    # @Txtroom: 房间号
    def __init__(self, programId: str, txtyq: str, Txtroom: str) -> None:
        self._programId = programId
        self._txtyq = txtyq
        self._Txtroom = Txtroom

    def run(self) -> None:
        data = {
            '__EVENTTARGET': None,
            '__EVENTARGUMENT': None,
            '__LASTFOCUS': None,
            '__VIEWSTATE': '/wEPDwULLTE4NDE5OTM2MDEPZBYCAgMPZBYIAgEPEA8WBh4NRGF0YVRleHRGaWVsZAUM5qW85qCL5Yy65Z+fHg5EYXRhVmFsdWVGaWVsZAUM5qW85qCL5Yy65Z+fHgtfIURhdGFCb3VuZGdkEBUGBuS4nOWMugnnlZnlrabnlJ8G6KW/5Yy6BumfteiLkQbntKvoj5gLLeivt+mAieaLqS0VBgbkuJzljLoJ55WZ5a2m55SfBuilv+WMugbpn7Xoi5EG57Sr6I+YAi0xFCsDBmdnZ2dnZxYBAgNkAgUPEA8WBh8ABQbmpbzlj7cfAQUG5qW85Y+3HwJnZBAVHQnlraboi5HmpbwL6Z+16IuRMTDmoIsL6Z+16IuRMTHmoIsL6Z+16IuRMTLmoIsL6Z+16IuRMTPmoIsL6Z+16IuRMTTmoIsL6Z+16IuRMTXmoIsL6Z+16IuRMTbmoIsL6Z+16IuRMTfmoIsL6Z+16IuRMTjmoIsL6Z+16IuRMTnmoIsK6Z+16IuRMeagiwvpn7Xoi5EyMOagiwvpn7Xoi5EyMeagiwvpn7Xoi5EyMuagiwvpn7Xoi5EyM+agiwvpn7Xoi5EyNOagiwvpn7Xoi5EyNeagiwvpn7Xoi5EyNuagiwvpn7Xoi5EyN+agiwrpn7Xoi5Ey5qCLCumfteiLkTPmoIsK6Z+16IuRNOagiwrpn7Xoi5E15qCLCumfteiLkTbmoIsK6Z+16IuRN+agiwrpn7Xoi5E45qCLCumfteiLkTnmoIsLLeivt+mAieaLqS0VHQnlraboi5HmpbwL6Z+16IuRMTDmoIsL6Z+16IuRMTHmoIsL6Z+16IuRMTLmoIsL6Z+16IuRMTPmoIsL6Z+16IuRMTTmoIsL6Z+16IuRMTXmoIsL6Z+16IuRMTbmoIsL6Z+16IuRMTfmoIsL6Z+16IuRMTjmoIsL6Z+16IuRMTnmoIsK6Z+16IuRMeagiwvpn7Xoi5EyMOagiwvpn7Xoi5EyMeagiwvpn7Xoi5EyMuagiwvpn7Xoi5EyM+agiwvpn7Xoi5EyNOagiwvpn7Xoi5EyNeagiwvpn7Xoi5EyNuagiwvpn7Xoi5EyN+agiwrpn7Xoi5Ey5qCLCumfteiLkTPmoIsK6Z+16IuRNOagiwrpn7Xoi5E15qCLCumfteiLkTbmoIsK6Z+16IuRN+agiwrpn7Xoi5E45qCLCumfteiLkTnmoIsCLTEUKwMdZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dkZAITDzwrAA0AZAIVDzwrAA0AZBgDBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAgUMSW1hZ2VCdXR0b24xBQxJbWFnZUJ1dHRvbjIFCUdyaWRWaWV3MQ9nZAUJR3JpZFZpZXcyD2dkynAdnQVomSSCl036JueTrE+lHLM=',
            '__EVENTVALIDATION': '/wEWKwLt0PODAgLorceeCQLc1sToBgL+zpWoBQK50MfoBgKj5aPiDQLtuMzrDQLrwqHzBQKX+9a3BAK/j9m4DALWzqKWBQLWzrbxDALWzprcCwLWzu6nAwLWzvKCCgLWzsbtAQLWzqrJCALWzr4UAtbOwswCAtbO1pcKApeK3tEBAsvlxIAPAsvlqOwGAsvlvLcOAsvlgJIFAsvllP0MAsvl+NgLAsvlzKMDAsvl0I4KAoyh8MwLAqG4kqcOAsbXtBIC++7WjAoCkITL5wwCtZPt0gYCmsWqkQ4Cv9zMCwKUlLDaCAL61dqrBgLSwpnTCALSwtXkAgLs0fbZDALs0Yq1BVT5qtuIcXHeOVkVJJhNo4N/aUWz',
            'programId': self._programId,
            'txtyq': self._txtyq,
            'Txtroom': self._Txtroom,
            'ImageButton1.x': random.randint(10, 90),
            'ImageButton1.y': random.randint(5, 25),
            'TextBox2': None,
            'TextBox3': None,
        }
        response = requests.post('http://202.114.18.218/Main.aspx', data=data)
        response.encoding = 'utf8'
        # with open('main.html', 'wb') as f:
        #     f.write(response.content)

        data_list = self.getTableData(response.text, 'GridView1')
        print(data_list)
        data_list = self.getTableData(response.text, 'GridView2')
        print(data_list)

    @staticmethod
    def getTableData(html: str, table_id: str) -> list:
        page = etree.HTML(html)
        tr_list = page.xpath(f'//table[@id="{table_id}"]//tr')
        if len(tr_list) == 0:
            return None

        th_list = tr_list[0].xpath('.//th/text()')
        key_list = []
        for th in th_list:
            key_list.append(th.strip())

        data_list = []
        for tr in tr_list[1:]:
            td_list = tr.xpath('.//td/text()')
            data = {}
            for i in range(len(td_list)):
                data[key_list[i]] = td_list[i]
            data_list.append(data)

        return data_list


if __name__ == '__main__':
    checkElectricUsage = CheckElectricUsage('韵苑', '韵苑5栋', '520')
    checkElectricUsage.run()
