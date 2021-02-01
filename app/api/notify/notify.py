import json
import os
from os.path import join

import requests
from django.http import HttpResponse, HttpResponseRedirect
from dotenv import load_dotenv
from rest_framework.views import APIView
from app.models import NotifyModel
from mylinebot.settings import BASE_DIR

dotenv_path = join(BASE_DIR, '.env')
load_dotenv(dotenv_path, override=True)
LINE_NOTIFY_CLIENT_ID = os.environ.get("LINE_NOTIFY_CLIENT_ID")
LINE_NOTIFY_CLIENT_SECERT = os.environ.get("LINE_NOTIFY_CLIENT_SECERT")
LINE_NOTIFY_REDIRECT_URI = os.environ.get("LINE_NOTIFY_REDIRECT_URI")

class LineNotifyAPIView(APIView):
    def post(self,request):
        print('post')
        print(request.data)
        try:
            newnotify = NotifyModel.objects.get(booking_uuid=request.data.__getitem__('state'))
            print(newnotify.booking_uuid + "連結正確")
        except NotifyModel.DoesNotExist:
            return HttpResponse("Good Roader Bot Notify連動失敗。請重新訂閱~")
        notify_seturl = 'https://notify-bot.line.me/oauth/token'
        print(request.data.__getitem__('state'))
        print(request.data.__getitem__('code'))
        payload = {
            'grant_type' : 'authorization_code',
            'code' : request.data.__getitem__('code'),
            'client_id' : LINE_NOTIFY_CLIENT_ID,
            'client_secret' : LINE_NOTIFY_CLIENT_SECERT,
            'redirect_uri' : LINE_NOTIFY_REDIRECT_URI,
        }
        res = requests.post(notify_seturl,data=payload)
        print(res.text)
        params = json.loads(res.text)
        if params['status'] == 200:
            try:
                newnotify = NotifyModel.objects.get(booking_uuid=request.data.__getitem__('state'))
                newnotify.booking_uuid = ""
                newnotify.token = params['access_token']
                newnotify.save()
                print(newnotify.booking_uuid + "已訂閱")
                headers = {
                    "Authorization": "Bearer " + params['access_token'],
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                params = {"message": "Good Roader Bot Notify設定成功"}
                r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)
                return HttpResponse("Good Roader Bot Notify連動完成。感謝訂閱，若要取消連動請輸入[取消訂閱]。")
            except NotifyModel.DoesNotExist:
                print(request.data.__getitem__('state')+"狀態失效")
        return HttpResponse("Good Roader Bot Notify連動失敗。請重新訂閱~")

class NotifyAPIView(APIView):
    def get(self,request, *args, **kwargs):
        print('get')
        uuid = kwargs['uuid']
        try:
            newnotify = NotifyModel.objects.get(booking_uuid=uuid)
            print(newnotify.booking_uuid + "連結存在")
        except NotifyModel.DoesNotExist:
            return HttpResponse("訂閱連結已過期")
        url = 'https://notify-bot.line.me/oauth/authorize?response_type=code&scope=notify&response_mode=form_post&client_id=' + LINE_NOTIFY_CLIENT_ID + '&redirect_uri='\
              + LINE_NOTIFY_REDIRECT_URI + '&state=' + uuid
        return HttpResponseRedirect(redirect_to=url)
        # return redirect('https://google.com.tw')