import json
import os
import re
from os.path import join

import requests
from django.forms import model_to_dict
from django.http import HttpResponse
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage, BoxComponent, TextComponent, BubbleContainer, \
    CarouselContainer, BlockStyle, BubbleStyle, QuickReply, QuickReplyButton, LocationAction, PostbackAction
from rest_framework.views import APIView

from app.api.module.oilinfo import getOilPrice, get_distance, drawCharts, getdiffprice
from app.models import NotifyModel, get_uuid, GasStationInfo, SearchLog, GogoroStationInfo
from mylinebot.settings import BASE_DIR

dotenv_path = join(BASE_DIR, '.env')
load_dotenv(dotenv_path, override=True)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

class ReplyMessageAPIView(APIView):
    def post(self, request):
        print(request.data)
        if (request.data.__contains__('events')):  # 判斷是否有events key
            switcher = {
                "message": self.replyMessage,
                "postback": self.replyPostback,
            }
            print(request.data['events'][0]['type'])
            func = switcher.get(request.data['events'][0]['type']) if switcher.__contains__(
                request.data['events'][0]['type']) else None
            if func != None:
                func(request)
            else:
                line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
                line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(text='請發送正確的請求'))
        return HttpResponse(request.data)

    def get(self):
        print("test")

    def replyMessage(self,request):
        print('replyMessage')
        switcherfunc = {
            "油價": self.replyOil,
            "趨勢": self.replyOilTrend,
            "訂閱": self.replyBooking,
            "取消訂閱": self.replyUnbooking,
            "查詢": self.replySearch,
            "計算": self.replyCal,
            "幫助": self.replyHelp,
        }
        if (request.data['events'][0]['message'].__contains__('text')):  # 判斷是否有text
            func = switcherfunc.get(request.data['events'][0]['message']['text']) if switcherfunc.__contains__(
                request.data['events'][0]['message']['text']) else self.replyCalResult
        elif (request.data['events'][0]['message'].__contains__('address')): #判斷是否傳送location
            func = self.replySearchResult
        else:
            func = None
        if func != None:
            func(request)
        # else:
            # line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
            # line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(text='請發送正確的指令'))
        return

    def replyPostback(self,request):
        print('replyPostback')
        defconditions = {'ok': '回上一頁^','cancel':'清除選擇','isElectricity':'充電站', 'isself': '自營站','isselfcard': '自助汽油',
                         'isselfdiesel': '自助柴油','ismember': '會員卡', 'iseasycard': '悠遊卡','isipasscard': '一卡通',
                         'ishappycash': 'Happy卡', 'isetag': 'Etag', 'isaddwater': '加水站','isaddair': '打氣站'}
        if (request.data['events'][0]['postback'].__contains__('data')):  # 判斷是否有data
            tagdata = request.data['events'][0]['postback']['data']
            userId = request.data['events'][0]['source']['userId']
            print(userId,tagdata)
            if tagdata == 'Condition':
                '''條件查詢開始_判斷之前是否有查詢尚未完成'''
                try:
                    '''查詢者已存在_送出未選擇過條件'''
                    oldserach_user = SearchLog.objects.get(user_id=userId)
                    print(userId + "<使用者查詢過>")
                    for key, value in model_to_dict(oldserach_user).items():
                        if value == True:
                            print(key)
                            del defconditions[key]  # 去除已經選過條件
                    self.replySearchForCondition(defconditions, request)
                except SearchLog.DoesNotExist:
                    '''查詢者不存在送出所有條件'''
                    self.replySearchForCondition(defconditions,request)
            elif tagdata == 'ok': #回上一頁
                self.replySearch(request,True)
            elif tagdata == 'cancel': #清除條件
                try:
                    '''查詢者存在，刪除查詢紀錄，送出所有條件'''
                    oldserach_user = SearchLog.objects.get(user_id=userId)
                    oldserach_user.delete()
                    self.replySearchForCondition(defconditions, request)
                except SearchLog.DoesNotExist:
                    '''查詢者未存在，送出所有條件'''
                    self.replySearchForCondition(defconditions, request)
            elif defconditions.get(tagdata) != None:
                '''查詢者選擇條件'''
                try:
                    '''更新資料庫查詢者新查詢選項'''
                    dicvalue = {tagdata:True}
                    SearchLog.objects.filter(user_id=userId).update(**dicvalue) #更新資料庫
                    oldserach_user = SearchLog.objects.get(user_id=userId)
                    print(userId + "<使用者查詢過>")
                    for key,value in model_to_dict(oldserach_user).items():
                        if value == True:
                            print(key)
                            del defconditions[key]#去除已經選過條件
                    print(defconditions)

                except SearchLog.DoesNotExist:
                    '''資料庫內創建新查詢者，並送出未選擇過條件'''
                    SearchLog.objects.create(user_id=userId)
                    dicvalue = {tagdata: True}
                    SearchLog.objects.filter(user_id=userId).update(**dicvalue)  # 更新資料庫
                    newserach_user = SearchLog.objects.get(user_id=userId)
                    print(userId + "<使用者查詢過>")
                    for key, value in model_to_dict(newserach_user).items():
                        if value == True:
                            print(key)
                            del defconditions[key]  # 去除已經選過條件
                    print(userId + "<使用者未查詢過>")

                self.replySearchForCondition(defconditions, request)
            elif tagdata == 'Gogoro':
                try:
                    '''查詢者存在，刪除查詢紀錄，送出所有條件'''
                    oldserach_user = SearchLog.objects.get(user_id=userId)
                    oldserach_user.isgogoro = True
                    oldserach_user.save()
                except SearchLog.DoesNotExist:
                    '''查詢者未存在，送出所有條件'''
                    newserach_user = SearchLog.objects.create(user_id=userId)
                    newserach_user.isgogoro = True
                    newserach_user.save()
                self.replySearchForGogoro(request)

    def replyOil(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        oil_data = getOilPrice()
        oil_data['price'] = price = getdiffprice(1)
        oil_data['tag'] = '上漲' if price > 0 else '持平' if price == 0 else '下跌'
        oil_data['bagColor'] = '#AD5A5A' if price > 0 else '#BEBEBE' if price == 0 else '#02C874'
        print(oil_data)
        contents = []
        contents.append(self.makeBubbleContainer(oil_data))
        line_bot_api.reply_message(request.data['events'][0]['replyToken'],
                                   FlexSendMessage(alt_text="油價", contents=CarouselContainer(contents=contents)))

    def replyOilTrend(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        charthtml = 'https://' + request.headers['Host'] + drawCharts()
        line_bot_api.reply_message(request.data['events'][0]['replyToken'],
                                   TextSendMessage(text=charthtml))

    def replyBooking(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        str = '請點擊網址完成訂閱'
        rand_uuid = get_uuid().__str__()
        charthtml = str + 'https://' + request.headers['Host'] + "/app/notify/" + rand_uuid
        userId = request.data['events'][0]['source']['userId']
        print(userId)
        try:
            oldnotify_user = NotifyModel.objects.get(user_id=userId)
            oldnotify_user.booking_uuid = rand_uuid
            oldnotify_user.save()
            print(userId + "使用者訂閱過")
        except NotifyModel.DoesNotExist:
            newnotify_user = NotifyModel.objects.create(user_id=userId)
            newnotify_user.booking_uuid = rand_uuid
            newnotify_user.save()
            print(userId + "使用者尚未訂閱過")
        line_bot_api.reply_message(request.data['events'][0]['replyToken'],TextSendMessage(text=charthtml))

    def replyUnbooking(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_notify_unbooking_url = 'https://notify-api.line.me/api/revoke'
        userId = request.data['events'][0]['source']['userId']
        strResult = 'Error'
        try:
            oldnotify_user = NotifyModel.objects.get(user_id=userId)
            if oldnotify_user.token != 'error':
                headers = {
                    "Authorization": "Bearer " + oldnotify_user.token,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                res = requests.post(line_notify_unbooking_url, headers=headers)
                if json.loads(res.text)['status'] == 200:
                    oldnotify_user.delete()
                    # oldnotify_user.token = 'error'
                    # oldnotify_user.save()
                    strResult = '取消訂閱成功，歡迎再次的訂閱'
                print(userId + "使用者訂閱過")
            else:
                strResult = '您尚未訂閱，請輸入[訂閱]來訂閱'
        except NotifyModel.DoesNotExist:
            strResult = '您尚未訂閱，請輸入[訂閱]來訂閱'
            print(userId + "使用者尚未訂閱過")
        print("完成取消訂閱")
        line_bot_api.reply_message(request.data['events'][0]['replyToken'],TextSendMessage(text=strResult))

    def replySearch(self,request,isback = False):
        if(isback == False):
            userId = request.data['events'][0]['source']['userId']
            try:
                oldnotify_user = SearchLog.objects.get(user_id=userId)
                print(userId + "<使用者查詢過>")
                messagetext = 'https://www.google.com/maps/search/?api=1&query={0},{1}'.format(oldnotify_user.latitude,oldnotify_user.longitude)
            except SearchLog.DoesNotExist:
                messagetext = "請選擇您的查詢條件"
        else:
            messagetext = "請選擇您的查詢條件"
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'],TextSendMessage(
            text=messagetext,
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(
                            label="送出地標查詢",
                        )
                    ),
                    QuickReplyButton(
                        action=PostbackAction(
                            label="選擇條件",
                            data="Condition",
                        )
                    ),
                    QuickReplyButton(
                        action=PostbackAction(
                            label="Gogoro電池站查詢",
                            data="Gogoro",
                        )
                    ),
                ]
            )
        ))

    def replySearchForCondition(self,conditions,request):
        print('replySearchForCondition')
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        items = self.makeQuickReplyButton(conditions)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(
            text="可複選",quick_reply=QuickReply(items=items)))

    def replySearchForGogoro(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(
            text="請送出您目前的地標",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=LocationAction(
                            label="送出地標查詢",
                        )
                    ),
                    QuickReplyButton(
                        action=PostbackAction(
                            label="回上一頁",
                            data="ok",
                        )
                    ),
                ]
            )
        ))

    def replySearchResult(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        userId = request.data['events'][0]['source']['userId']
        lon = request.data['events'][0]['message']['longitude']
        lat = request.data['events'][0]['message']['latitude']
        distance = 10000
        lontmp = 0
        lattmp = 0
        try:
            '''查詢'''
            oldserach_user = SearchLog.objects.get(user_id=userId)
            if(oldserach_user.isgogoro == True):
                for f in GogoroStationInfo.objects.all():
                    if (distance > get_distance(lon, lat, f.Longitude, f.Latitude)):
                        distance = get_distance(lon, lat, f.Longitude, f.Latitude)
                        lontmp = f.Longitude
                        lattmp = f.Latitude
                        print(lattmp, lontmp)
                    print(f.Latitude, f.Longitude)
                oldserach_user.isgogoro = False
            else:
                dictresult = {}
                for key, value in model_to_dict(oldserach_user).items():
                    if key == 'isself' and value == True:
                        dictresult['type'] = 1
                    elif value == True:
                        dictresult[key] = value
                print(dictresult)
                for f in GasStationInfo.objects.filter(**dictresult):
                    if (distance > get_distance(lon, lat, f.longitude, f.latitude)):
                        distance = get_distance(lon, lat, f.longitude, f.latitude)
                        lontmp = f.longitude
                        lattmp = f.latitude
                        print(lattmp, lontmp)
                    print(f.latitude, f.longitude)
            oldserach_user.latitude = lattmp
            oldserach_user.longitude = lontmp
            oldserach_user.save()#紀錄最近查詢點

        except SearchLog.DoesNotExist:
            newserach_user = SearchLog.objects.create(user_id=userId)
            for f in GasStationInfo.objects.all():
                if(distance > get_distance(lon,lat,f.longitude,f.latitude)):
                    distance = get_distance(lon,lat,f.longitude,f.latitude)
                    lontmp = f.longitude
                    lattmp = f.latitude
                    print(lattmp,lontmp)
                print(f.latitude, f.longitude)
            newserach_user.latitude = lattmp
            newserach_user.longitude = lontmp
            newserach_user.save()  # 紀錄最近查詢點

        googlemap_url = 'https://www.google.com/maps/search/?api=1&query={0},{1}'.format(lattmp, lontmp)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(text=googlemap_url))

    def replyCal(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(
            text='輸入格式範例:\n'
                 's20l=自助加油20公升多少金額\n'
                 's200=自助加油200元多少公升\n'
                 '20l=人工加油20公升多少金額\n'
                 '200=人工加油200元多少公升\n'
        ))

    def replyCalResult(self,request):
        strtext = request.data['events'][0]['message']['text']  # 取得message text
        oil_data = getOilPrice()
        Unleaded_Gasoline_98 = float(oil_data['98 Unleaded Gasoline'])
        Unleaded_Gasoline_95 = float(oil_data['95 Unleaded Gasoline'])
        Unleaded_Gasoline_92 = float(oil_data['92 Unleaded Gasoline'])
        CPC_Gas_Stations = float(oil_data['Premium Diesel'])
        if (re.match('s[1-9]\d*\.\d*l$|s0\.\d*l$|s[1-9]\d*l$', strtext) != None):
            '''自助公升to元'''
            ml = float(re.split('s(.*)l', strtext)[1])
            Unleaded_Gasoline_98 = round(ml * (Unleaded_Gasoline_98 - 0.8),2)
            Unleaded_Gasoline_95 = round(ml * (Unleaded_Gasoline_95 - 0.8),2)
            Unleaded_Gasoline_92 = round(ml * (Unleaded_Gasoline_92 - 0.8),2)
            CPC_Gas_Stations = round(ml * (CPC_Gas_Stations - 0.8),2)
            strtext = '98:{0}元\n95:{1}元\n92:{2}元\n柴油:{3}元\n'.format(
                Unleaded_Gasoline_98,Unleaded_Gasoline_95,Unleaded_Gasoline_92,CPC_Gas_Stations)
        elif (re.match('s[1-9]\d*$', strtext) != None):
            '''自助元to公升'''
            dollar = int(re.split('s(.*)', strtext)[1])
            Unleaded_Gasoline_98 = round(dollar / (Unleaded_Gasoline_98 - 0.8),2)
            Unleaded_Gasoline_95 = round(dollar / (Unleaded_Gasoline_95 - 0.8),2)
            Unleaded_Gasoline_92 = round(dollar / (Unleaded_Gasoline_92 - 0.8),2)
            CPC_Gas_Stations = round(dollar / (CPC_Gas_Stations - 0.8),2)
            strtext = '98:{0}公升\n95:{1}公升\n92:{2}公升\n柴油:{3}公升\n'.format(
                Unleaded_Gasoline_98, Unleaded_Gasoline_95, Unleaded_Gasoline_92, CPC_Gas_Stations)
        elif (re.match('^\d*\.\d*l$|^0\.\d*[1-9]\d*l$|^\d*l$', strtext) != None):
            '''公升to元'''
            ml = float(re.split('(.*)l', strtext)[1])
            Unleaded_Gasoline_98 = round(ml * (Unleaded_Gasoline_98),2)
            Unleaded_Gasoline_95 = round(ml * (Unleaded_Gasoline_95),2)
            Unleaded_Gasoline_92 = round(ml * (Unleaded_Gasoline_92),2)
            CPC_Gas_Stations = round(ml * (CPC_Gas_Stations),2)
            strtext = '98:{0}元\n95:{1}元\n92:{2}元\n柴油:{3}元\n'.format(
                Unleaded_Gasoline_98, Unleaded_Gasoline_95, Unleaded_Gasoline_92, CPC_Gas_Stations)
        elif (re.match('^\d*$', strtext) != None):
            '''元to公升'''
            dollar = int(strtext)
            Unleaded_Gasoline_98 = round(dollar / (Unleaded_Gasoline_98),2)
            Unleaded_Gasoline_95 = round(dollar / (Unleaded_Gasoline_95),2)
            Unleaded_Gasoline_92 = round(dollar / (Unleaded_Gasoline_92),2)
            CPC_Gas_Stations = round(dollar / (CPC_Gas_Stations),2)
            strtext = '98:{0}公升\n95:{1}公升\n92:{2}公升\n柴油:{3}公升\n'.format(
                Unleaded_Gasoline_98, Unleaded_Gasoline_95, Unleaded_Gasoline_92, CPC_Gas_Stations)
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(text=strtext))

    def replyHelp(self,request):
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_bot_api.reply_message(request.data['events'][0]['replyToken'], TextSendMessage(
            text='功能說明:\n'
                 '油價=即時油價查詢\n'
                 '趨勢=歷史油價趨勢圖\n'
                 '查詢=中油加油站&Gogoro電池交換站查詢功能\n'
                 '訂閱=透過LineNotify通知每週油價漲跌價格\n'
                 '計算=公升與金額計算轉換，讓您省下浪費的錢\n'
        ))

    def makeBubbleContainer(self,result):
        date = result['date']
        future_price = result['price']
        future_tag = result['tag']
        bagColor = result['bagColor']
        Unleaded_Gasoline_98 = result['98 Unleaded Gasoline']
        Unleaded_Gasoline_95 = result['95 Unleaded Gasoline']
        Unleaded_Gasoline_92 = result['92 Unleaded Gasoline']
        CPC_Gas_Stations = result['Premium Diesel']
        header_contents = [
            BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(size='md', color='#3C3C3C',text='%s 油價' % (date),align='center',weight='bold'),
                    TextComponent(size='xxl', color='#3C3C3C', text='%s %s' % (future_tag, future_price),
                                  align='center',weight='bold'),
                ]
            )
        ]

        body_contents = [
            BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='98無鉛',align='center'),
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='95無鉛', align='center'),
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='92無鉛', align='center'),
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='超級柴油', align='center'),
                ]
            ),
        ]

        footer_contents = [
            BoxComponent(
                layout='horizontal',
                paddingAll='lg',
                contents=[
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='%s' % (Unleaded_Gasoline_98), align='center'),
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='%s' % (Unleaded_Gasoline_95), align='center'),
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='%s' % (Unleaded_Gasoline_92), align='center'),
                    TextComponent(size='sm', color='#6C6C6C', flex=1, text='%s' % (CPC_Gas_Stations), align='center'),
                ]
            )
        ]

        # footer_contents.append(SpacerComponent(separator = 'true'))

        return BubbleContainer(
            # direction='ltr',
            styles= BubbleStyle(
                header= BlockStyle(background_color = bagColor),
            ),
            size='mega',
            header=BoxComponent(
                layout='vertical',
                contents=header_contents
            ),
            body=BoxComponent(
                layout='vertical',
                contents=body_contents,
                padding_all='12px'
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=footer_contents,
            ),
        )

    def makeQuickReplyButton(self,result):
        item = []
        for key,value in result.items():
            item.append(
                QuickReplyButton(
                    action=PostbackAction(
                        label=value,
                        data=key,
                    )
                )
            )
        return item
