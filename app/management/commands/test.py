import json
import os
from os.path import join

from django.core.management.base import BaseCommand,CommandError
import requests
from dotenv import load_dotenv
from fake_useragent import UserAgent
from linebot import LineBotApi

import xml.etree.ElementTree as ET

from mylinebot.settings import BASE_DIR

dotenv_path = join(BASE_DIR, '.env')
load_dotenv(dotenv_path, override=True)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

class Command(BaseCommand):
    def handle(self, *args, **options):
        """set line bot rich menu example"""
        # self.delet_all_richmenu()
        # self.create_richmenu("Menu.png")
        return
    def create_richmenu(self,image_path,):
        create_rich_url = "https://api.line.me/v2/bot/richmenu"#創建richMenu格式設定API
        headers = {
            "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        body = {
            "size": {"width": 2500, "height": 1386},
            "selected": "false",
            "name": "richmenu-1",
            "chatBarText": "開啟小幫手",
            "areas": [
                {
                    "bounds": {"x": 0, "y": 0, "width": 833, "height": 693},
                    "action": {"type": "message", "label": "文字", "text": "油價"}
                },
                {
                    "bounds": {"x": 833, "y": 0, "width": 833, "height": 693},
                    "action": {"type": "message", "label": "文字", "text": "查詢"}
                },
                {
                    "bounds": {"x": 1666, "y": 0, "width": 833, "height": 693},
                    "action": {"type": "message", "label": "文字", "text": "計算"}
                    # "action": {"type": "uri", "label": "網址",
                    #            "uri": "https://www.cpc.com.tw/"}
                    # "action": {"type": "postback", "label": "選單", "data": "action=changeMenu2"}
                },
                {
                    "bounds": {"x": 0, "y": 693, "width": 833, "height": 693},
                    "action": {"type": "message", "label": "文字", "text": "趨勢"}
                },
                {
                    "bounds": {"x": 833, "y": 693, "width": 833, "height": 693},
                    "action": {"type": "message", "label": "文字", "text": "訂閱"}
                },
                {
                    "bounds": {"x": 1666, "y": 693, "width": 833, "height": 693},
                    "action": {"type": "message", "label": "文字", "text": "幫助"}
                    # "action": {"type": "uri", "label": "關於",
                    #            "uri": "https://google.com.tw"}
                }
            ]
        }
        res = requests.post(create_rich_url,headers = headers,data = json.dumps(body).encode('utf-8'))
        print(res.text)

        richMenuId = json.loads(res.text)["richMenuId"] #將字串轉為字典取出key為richMenuId的值
        upload_img_url = "https://api-data.line.me/v2/bot/richmenu/" + richMenuId + "/content" #上傳richMenu圖片API
        headers = {
            "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN,
            "Content-Type": "image/png"
        }
        with open(image_path, 'rb') as f:
            data = f.read()#將圖片讀出為2進制碼
        res = requests.post(upload_img_url, headers=headers, data=data)
        print(res.text)

        set_rich_url = "https://api.line.me/v2/bot/user/all/richmenu/" + richMenuId #設定預設richMenu api
        headers = {
            "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN,
        }
        res = requests.post(set_rich_url,headers=headers)
        print(res.text)

    def delet_all_richmenu(self):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        rich_menu_list = line_bot_api.get_rich_menu_list()
        for key in rich_menu_list:
            line_bot_api.delete_rich_menu(key.rich_menu_id)
            print(key.rich_menu_id + "is delete")

    def replyMessage(self):
        print('replyMessage')
        return

    def replyPostback(self):
        print('replyPostback')
        return

    def getOilPrice(self):
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
            "date": root[1][0][1][10].text,
        }
        # for tagname in root[1][0].findall('產品編號'):
        #     print(tagname.text)
        for tagname, tagvalue in zip(root.iter('產品名稱'), root.iter('參考牌價')):
            oil_data[tagname.text] = tagvalue.text

        return oil_data