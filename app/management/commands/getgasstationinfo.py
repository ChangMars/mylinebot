import requests
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand
from fake_useragent import UserAgent
from app.models import GasStationInfo

'https://vipmember.tmtd.cpc.com.tw/mbwebs/service_store.aspx?StnID=' #加油站資訊網站

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("getgasstationinfo command start")
        self.getGasStationInfo()
        self.getGasStationWater()
        self.getGasStationAir()
        self.getGasStationElectricity()

    '''更新加油站基本資料'''
    def getGasStationInfo(self):
        gasstaion_url = 'https://vipmember.tmtd.cpc.com.tw/opendata/STNWebService.asmx/getStationInfo_XML?'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        res = requests.get(gasstaion_url,headers=headers)
        root = ET.fromstring(res.content)
        for id,type,name,city,town,address,phone,servicenum,isbusiness,ishighway,is92,is95,is98,isgas,iscoal,isdiesel,ismember,\
                isselfcard,isselfdiesel,isEI,iseasycard,isipasscard,ishappycash,longitude,latitude,bussinesstime,washtype,isetag,ismaintain\
            in zip(root.iter('站代號')
                , root.iter('類別')
                , root.iter('站名')
                , root.iter('縣市')
                , root.iter('鄉鎮區')
                , root.iter('地址')
                , root.iter('電話')
                , root.iter('服務中心')
                , root.iter('營業中')
                , root.iter('國道高速公路')
                , root.iter('無鉛92')
                , root.iter('無鉛95')
                , root.iter('無鉛98')
                , root.iter('酒精汽油')
                , root.iter('煤油')
                , root.iter('超柴')
                , root.iter('會員卡')
                , root.iter('刷卡自助')
                , root.iter('自助柴油站')
                , root.iter('電子發票')
                , root.iter('悠遊卡')
                , root.iter('一卡通')
                , root.iter('HappyCash')
                , root.iter('經度')
                , root.iter('緯度')
                , root.iter('營業時間')
                , root.iter('洗車類別')
                , root.iter('etag申裝儲值時間')
                , root.iter('保養間時間')):
            print("start")
            try:
                gasstation = GasStationInfo.objects.get(id=id.text)
                gasstation.type = True if type.text == '自營站' else False
                gasstation.name = name.text
                gasstation.city = city.text
                gasstation.town = town.text
                gasstation.address = address.text
                gasstation.phone = phone.text
                gasstation.servicenum = servicenum.text
                gasstation.isbusiness = True if isbusiness.text == '1' else False
                gasstation.ishighway = True if ishighway.text != '0' else False
                gasstation.is92 = True if is92.text == 'True' else False
                gasstation.is95 = True if is95.text == 'True' else False
                gasstation.is98 = True if is98.text == 'True' else False
                gasstation.isgas = True if isgas.text == 'True' else False
                gasstation.iscoal = True if iscoal.text != '0' else False
                gasstation.isdiesel = True if isdiesel.text == 'True' else False
                gasstation.ismember = True if ismember.text == 'True' else False
                gasstation.isselfcard = True if isselfcard.text == 'True' else False
                gasstation.isselfdiesel = True if isselfdiesel.text == 'True' else False
                gasstation.isEI = True if isEI.text == 'True' else False
                gasstation.iseasycard = True if iseasycard.text == 'True' else False
                gasstation.isipasscard = True if isipasscard.text == 'True' else False
                gasstation.ishappycash = True if ishappycash.text == 'True' else False
                gasstation.isetag = True if isetag.text != ' ' else False
                gasstation.ismaintain = True if isbusiness.text == '1' else False
                gasstation.washtype = washtype.text
                gasstation.bussinesstime = bussinesstime.text
                gasstation.longitude = float(longitude.text)
                gasstation.latitude = float(latitude.text)
                gasstation.save()
                """更新資料庫資訊"""
            except GasStationInfo.DoesNotExist:
                """創建一筆加油站資料"""
                gasstation = GasStationInfo.objects.create(id=id.text)
                gasstation.type = True if type.text == '自營站' else False
                gasstation.name = name.text
                gasstation.city = city.text
                gasstation.town = town.text
                gasstation.address = address.text
                gasstation.phone = phone.text
                gasstation.servicenum = servicenum.text
                gasstation.isbusiness = True if isbusiness.text == '1' else False
                gasstation.ishighway = True if ishighway.text != '0' else False
                gasstation.is92 = True if is92.text == 'True' else False
                gasstation.is95 = True if is95.text == 'True' else False
                gasstation.is98 = True if is98.text == 'True' else False
                gasstation.isgas = True if isgas.text == 'True' else False
                gasstation.iscoal = True if iscoal.text != '0' else False
                gasstation.isdiesel = True if isdiesel.text == 'True' else False
                gasstation.ismember = True if ismember.text == 'True' else False
                gasstation.isselfcard = True if isselfcard.text == 'True' else False
                gasstation.isselfdiesel = True if isselfdiesel.text == 'True' else False
                gasstation.isEI = True if isEI.text == 'True' else False
                gasstation.iseasycard = True if iseasycard.text == 'True' else False
                gasstation.isipasscard = True if isipasscard.text == 'True' else False
                gasstation.ishappycash = True if ishappycash.text == 'True' else False
                gasstation.isetag = True if isetag.text != ' ' else False
                gasstation.ismaintain = True if isbusiness.text == '1' else False
                gasstation.washtype = washtype.text
                gasstation.bussinesstime = bussinesstime.text
                gasstation.longitude = float(longitude.text)
                gasstation.latitude = float(latitude.text)
                gasstation.save()
                print("新增一筆加油站資料")

    '''更新加油站是否可加水'''
    def getGasStationWater(self):
        gasstaion_url = 'https://vipmember.tmtd.cpc.com.tw/opendata/addwaterstn.asmx/getaddwaterstnData_XML'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        res = requests.get(gasstaion_url, headers=headers)
        root = ET.fromstring(res.content)
        for id in root.iter('站代號'):
            print(id.text)
            try:
                gasstation = GasStationInfo.objects.get(id=id.text)
                gasstation.isaddwater = True
                gasstation.save()
            except GasStationInfo.DoesNotExist:
                print("DoesNotExist")

    '''更新加油站是否可打氣'''
    def getGasStationAir(self):
        gasstaion_url = 'https://vipmember.tmtd.cpc.com.tw/opendata/inflationstn.asmx/getinflationstnData_XML'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        res = requests.get(gasstaion_url, headers=headers)
        root = ET.fromstring(res.content)
        for id in root.iter('站代號'):
            print(id.text)
            try:
                gasstation = GasStationInfo.objects.get(id=id.text)
                gasstation.isaddair = True
                gasstation.save()
            except GasStationInfo.DoesNotExist:
                print("DoesNotExist")

    def getGasStationElectricity(self):
        gasstaion_url = 'https://vipmember.tmtd.cpc.com.tw/opendata/electriccharging.asmx/getelectricchargingData_XML'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        res = requests.get(gasstaion_url, headers=headers)
        root = ET.fromstring(res.content)
        for id in root.iter('站代號'):
            print(id.text)
            try:
                gasstation = GasStationInfo.objects.get(id=id.text)
                gasstation.isElectricity = True
                gasstation.save()
            except GasStationInfo.DoesNotExist:
                print("DoesNotExist")