from math import radians, cos, sin, sqrt, atan2
from pyecharts import options as opts
import xml.etree.ElementTree as ET
import requests
from fake_useragent import UserAgent
from pyecharts.charts import Line

'''
獲取目前的汽油價格
'''
def getOilPrice():
    oil_api = 'https://vipmember.tmtd.cpc.com.tw/opendata/ListPriceWebService.asmx/getCPCMainProdListPrice_English'
    user_agent = UserAgent().random
    headers = {
        "User-Agent": user_agent
    }
    res = requests.get(oil_api, headers=headers)
    # print(res.content)
    root = ET.fromstring(res.content)
    # print(root[1][0][1][0].text)
    oil_data = {
        "date": root[1][0][1][10].text.split('T')[0],
    }
    # for tagname in root[1][0].findall('產品編號'):
    #     print(tagname.text)
    for tagname, tagvalue in zip(root.iter('產品名稱'), root.iter('參考牌價')):
        oil_data[tagname.text] = tagvalue.text
    return oil_data


'''
獲取上週與下週價格差
type:1:無鉛汽油92, 2:無鉛汽油95, 3:無鉛汽油98, 4:超級/高級柴油, 5:低硫燃料油(0.5%), 6:甲種低硫燃料油(0.5)
'''


def getdiffprice(type):
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
    for tagvalue in root.iter('參考牌價'):
        oil_data.append(tagvalue.text)
    return round(float(oil_data[-1]) - float(oil_data[-2]), 2)


'''
獲取歷史價格
type:1:無鉛汽油92, 2:無鉛汽油95, 3:無鉛汽油98, 4:超級/高級柴油, 5:低硫燃料油(0.5%), 6:甲種低硫燃料油(0.5)
'''
def gethistoryprice(type, isdate):
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


'''將資料化成折線圖'''
def drawCharts():
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
    line = Line()
    date_x = gethistoryprice(3, True)
    line.add_xaxis(date_x)
    price_92 = gethistoryprice(1, False)
    line.add_yaxis("92無鉛汽油", price_92)
    price_95 = gethistoryprice(2, False)
    line.add_yaxis("95無鉛汽油", price_95)
    price_98 = gethistoryprice(3, False)
    line.add_yaxis("98無鉛汽油", price_98)
    price_99 = gethistoryprice(4, False)
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
    line.render("template/oil_history_price_rander.html")
    return '/oil_history_price_rander/'


'''經緯度計算最短距離'''
def get_distance(ulng1, ulat1, olng2, olat2):
    R = 6373.0
    lat1 = radians(ulat1)
    lon1 = radians(ulng1)
    lat2 = radians(olat2)
    lon2 = radians(olng2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    print("Result:", distance)
    return distance