import json

import requests
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand
from fake_useragent import UserAgent
from app.models import GasStationInfo, GogoroStationInfo

'https://vipmember.tmtd.cpc.com.tw/mbwebs/service_store.aspx?StnID=' #加油站資訊網站

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("getgogorostationinfo command start")
        self.getGogoroStationInfo()


    '''更新加油站基本資料'''
    def getGogoroStationInfo(self):
        gasstaion_url = 'https://webapi.gogoro.com/api/vm/list'
        user_agent = UserAgent().random
        headers = {
            "User-Agent": user_agent
        }
        res = requests.get(gasstaion_url, headers=headers)
        gogoroj = json.loads(res.text)
        for item in gogoroj:
            try:
                olddata = GogoroStationInfo.objects.get(Id = item['Id'])
                olddata.LocName = item['LocName']
                olddata.Longitude = item['Longitude']
                olddata.Latitude = item['Latitude']
                olddata.ZipCode = item['ZipCode']
                olddata.Address = item['Address']
                olddata.District = item['District']
                olddata.City = item['City']
                olddata.State = item['State']
                olddata.StorePhoto = item['StorePhoto']
                olddata.RId = item['RId']
                olddata.save()
                print(item['Id'] + "更新成功")
            except GogoroStationInfo.DoesNotExist:
                newdata = GogoroStationInfo.objects.create(Id = item['Id'])
                newdata.LocName = item['LocName']
                newdata.Longitude = item['Longitude']
                newdata.Latitude = item['Latitude']
                newdata.ZipCode = item['ZipCode']
                newdata.Address = item['Address']
                newdata.District = item['District']
                newdata.City = item['City']
                newdata.State = item['State']
                newdata.StorePhoto = item['StorePhoto']
                newdata.RId = item['RId']
                newdata.save()
                print(item['Id'] + "新增成功")
