import time

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.models import TestModel
from app.serializer import TestSerializer
from app.celery_task import task

class TestViewSet(viewsets.ModelViewSet):
    '''
    header
    Authorization: Token key
    '''
    # permission_classes = [IsAuthenticated]#設定使用API權限方式
    serializer_class = TestSerializer#設定序列化類別

    '''
    如果 detail True的話 一定要有pk的參數 
    '''
    @action(detail=False, methods=['get'])#設定api呼叫方式
    def a(self, request, pk=None):
        data=TestModel.objects.all()
        print(data)
        print(request.data)
        print(pk)
        task.sendnotify.delay()
        return Response({'s': 1}, status=status.HTTP_200_OK)


