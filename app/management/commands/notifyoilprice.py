from datetime import datetime

import pytz
import requests
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from fake_useragent import UserAgent
import xml.etree.ElementTree as ET
from app.models import NotifyModel

class Command(BaseCommand):
    def handle(self, *args, **options):
        # NotifyModel.objects.create(user_id='U8da04152b0c28d0e257d9fdc5bf0cc6a',token='HwORNCJWptQlvL2tbWMvY2JDUTP0omH1orRIZ0S0EUW')
        # NotifyModel.objects.filter(user_id='1313').delete()
        data = self.getdiffprice(1)#獲取目前油價的差價與日期
        print(data['price'], data['date'])
        oil_tag = "上漲" if data['price'] > 0 else "持平" if data['price'] == 0 else "下跌"
        today = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))
        refreshtime = datetime.strptime(data['date'], "%Y-%m-%d").astimezone(pytz.timezone('Asia/Taipei'))
        refreshtime7 = datetime.strptime(data['date'], "%Y-%m-%d").astimezone(pytz.timezone('Asia/Taipei')) + relativedelta(days=6.5)
        print(today,refreshtime,refreshtime7)
        users = NotifyModel.objects.all()
        for user in users:
            # user.notify_time = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))
            # user.save()
            if user.notify_time < refreshtime7:
                tital_tag = "\n***本週油價***\n" if today > refreshtime else "\n***下週油價***\n"
                self.sendMessageNotify(user.token, tital_tag + oil_tag + str(data['price']) + "元")
                user.notify_time = datetime.strptime(data['date'], "%Y-%m-%d").astimezone(
                    pytz.timezone('Asia/Taipei')) + relativedelta(days=7)
                user.save()
        print("成功")

    def sendMessageNotify(self,token,message):
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params = {"Message": message}
        res = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)

    '''
    獲取上週與下週價格差
    type:1:無鉛汽油92, 2:無鉛汽油95, 3:無鉛汽油98, 4:超級/高級柴油, 5:低硫燃料油(0.5%), 6:甲種低硫燃料油(0.5)
    '''
    def getdiffprice(self, type):
        oil_history_api = 'https://vipmember.tmtd.cpc.com.tw/opendata/ListPriceWebService.asmx/getCPCMainProdListPrice_Historical'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        if (type > 6 or type < 0):
            return 0
        res = requests.post(oil_history_api, data={"prodid": "2"}, headers=headers)
        root = ET.fromstring(res.content)
        oil_data = []
        oil_date = []
        for tagvalue,tagdate in zip(root.iter('參考牌價'),root.iter('牌價生效時間')):
            oil_data.append(tagvalue.text)
            oil_date.append(tagdate.text)
        result = {
            "date": oil_date[-1].split('T')[0],
            "price":round(float(oil_data[-1]) - float(oil_data[-2]), 2)
        }
        return result