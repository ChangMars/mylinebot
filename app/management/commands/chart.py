import os
import re

import requests
from django.core.management import BaseCommand
from fake_useragent import UserAgent
from pyecharts.charts import Line
from pyecharts import options as opts
import xml.etree.ElementTree as ET
import datetime
from datetime import datetime as df

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.drawCharts()
        return

    def gethistoryprice(self, type, isdate):
        oil_history_api = 'https://vipmember.tmtd.cpc.com.tw/opendata/ListPriceWebService.asmx/getCPCMainProdListPrice_Historical'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        res = requests.post(oil_history_api, data={"prodid": type}, headers=headers)
        root = ET.fromstring(res.content)
        date = []
        price = []
        for tagdate, tagvalue in zip(root.iter('牌價生效時間'), root.iter('參考牌價')):
            date.append(tagdate.text.split('T')[0])
            price.append(tagvalue.text)
        return date if isdate == True else price
    def fileprocess(self):
        filesname = os.listdir('template/')
        conformfiles = []
        for filename in filesname:#過濾符合的檔案名稱刪除過期檔案
            rename = re.search('oil_history_price_(.*)\.html', filename)
            if rename != None :
                if (df.strptime(rename[1],"%Y_%m_%d") + datetime.timedelta(days = 6)).date() < df.today().date() :
                    os.remove(filename)
                else:
                    conformfiles.append(filename)

        print(conformfiles)
        return conformfiles


    def drawCharts(self):
        '''柱狀圖'''
        # bar = Bar()
        # bar.add_xaxis(oil_data_x)
        # bar.add_yaxis("Oil_Price", oil_data_y)
        # bar.set_global_opts(title_opts=opts.TitleOpts(title="Oil_Price"),
        #                     datazoom_opts=opts.DataZoomOpts(type_="inside"),
        #                     yaxis_opts=opts.AxisOpts(name="Price"),
        #                     xaxis_opts=opts.AxisOpts(name="Date"),
        #                     )
        '''折線圖'''
        conformfiles = self.fileprocess()
        # if conformfiles != []:
        #     print('template/' + conformfiles[0])
        #     os.system('template/' + conformfiles[0])
        line = Line()
        date_x = self.gethistoryprice(3, True)
        line.add_xaxis(date_x)
        price_92 = self.gethistoryprice(1, False)
        line.add_yaxis("92無鉛汽油", price_92)
        price_95 = self.gethistoryprice(2, False)
        line.add_yaxis("95無鉛汽油", price_95)
        price_98 = self.gethistoryprice(3, False)
        line.add_yaxis("98無鉛汽油", price_98)
        price_99 = self.gethistoryprice(4, False)
        line.add_yaxis("超級柴油", price_99)
        line.set_global_opts(title_opts=opts.TitleOpts(title="油價趨勢圖"),
                             datazoom_opts=opts.DataZoomOpts(
                                 type_="slider",
                                 range_start=100,
                                 range_end=80,
                             ),
                             yaxis_opts=opts.AxisOpts(
                                 name='價格',
                                 # type_="value",
                                 # axistick_opts=opts.AxisTickOpts(is_show=True),
                                 # splitline_opts=opts.SplitLineOpts(is_show=True),
                             ),
                             xaxis_opts=opts.AxisOpts(name="日期"),
                             )
        nowdate = df.strptime(date_x[-1], "%Y-%m-%d").strftime("%Y_%m_%d")
        line.render("template/oil_history_price_%s.html" % (nowdate))
        os.system('template/oil_history_price_%s.html' % (nowdate))