from django.conf.urls import url
from django.urls import include, path, register_converter, converters
from . import views
from app.api.notify import notify
from app.api.linebots import replymessage

app_name = 'app'
register_converter(converters.UUIDConverter, 'uuid')
urlpatterns = [
   # url(r'^$', views.hello),
   url(r'^hello/', views.hello),#測試url使用
   url(r'^pychartsexample/',views.pychartsexample),#測試pycharts example使用
   url(r'^chart/',views.line_chart,name='line_chart'),#測試django-chartjs example使用
   url(r'^chartJSON/',views.line_chart_json,name='line_chart_json'),#測試django-chartjs example使用
   url(r'^callback/', replymessage.ReplyMessageAPIView.as_view()),
   url(r'^notify/(?P<uuid>[0-9A-Za-z_\-]+)',notify.NotifyAPIView.as_view()),
   url(r'^notify/',notify.LineNotifyAPIView.as_view()),
]