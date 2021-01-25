import uuid as uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

def get_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()))

class UserProfile(models.Model):#資料模組定義與創建綁定資料表(自定義範例)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField('name', max_length=128, blank=True)
    birthday = models.DateField(blank=True)
    location = models.CharField('location', max_length=50, blank=True)
    money = models.IntegerField('money', default=0, blank=True)
    experience = models.IntegerField('experience', default=0, blank=True)
    service = models.CharField('service', max_length=128, blank=True)
    reply_time = models.IntegerField('reply_time', default=0, blank=True)
    rate = models.DecimalField('rate', default=0, max_digits=2, decimal_places=1, blank=True)
    description = models.CharField('description', max_length=128, blank=True)
    skill = models.CharField('skill', max_length=128, blank=True)
    license = models.CharField('license', max_length=128, blank=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return "{}'s profile".format(self.user.__str__())

class TestModel(models.Model):#資料模組定義與創建綁定資料表(自定義範例)
    name = models.CharField('name', max_length=128, blank=True)
    birthday = models.DateField(blank=True)
    class Meta:
        verbose_name = 'Test Model'

    def __str__(self):
        return "{}'s test".format(self.name.__str__())

class NotifyModel(models.Model):#linebot資料模組定義
    user_id = models.CharField('none', primary_key=True, null=False, max_length=512)
    booking_uuid = models.CharField('',null=False, max_length=512)
    token = models.CharField('error',null=False,max_length=512)
    create_time = models.DateTimeField(default=timezone.now)
    notify_time = models.DateTimeField(default=timezone.now)
    class Meta:
        verbose_name = 'Notify Model'

    def __str__(self):
        return "{}'s notify".format(self.user_id.__str__())

class GasStationInfo(models.Model):#加油站資訊
    id = models.CharField('N/A',primary_key=True, null=False, max_length=20)
    type = models.IntegerField(default=0)
    name = models.CharField('N/A', null=False, max_length=20)
    city = models.CharField('N/A', null=False, max_length=20)
    town = models.CharField('N/A', null=False, max_length=20)
    address = models.CharField('N/A', null=False, max_length=50)
    phone = models.CharField('N/A', null=False, max_length=20)
    servicenum = models.CharField('N/A', null=False, max_length=20)
    isbusiness = models.BooleanField(default=False)
    ishighway = models.BooleanField(default=False)
    is92 = models.BooleanField(default=False)
    is95 = models.BooleanField(default=False)
    is98 = models.BooleanField(default=False)
    isgas = models.BooleanField(default=False)
    iscoal = models.BooleanField(default=False)
    isdiesel = models.BooleanField(default=False)
    ismember = models.BooleanField(default=False)
    isselfcard = models.BooleanField(default=False)
    isselfdiesel = models.BooleanField(default=False)
    isEI = models.BooleanField(default=False)
    iseasycard = models.BooleanField(default=False)
    isipasscard = models.BooleanField(default=False)
    ishappycash = models.BooleanField(default=False)
    isetag = models.BooleanField(default=False)
    ismaintain = models.BooleanField(default=False)
    isaddwater = models.BooleanField(default=False)
    isaddair = models.BooleanField(default=False)
    isElectricity = models.BooleanField(default=False)
    washtype = models.CharField('N/A', null=False, max_length=20)
    bussinesstime = models.CharField('N/A', null=False, max_length=20)
    longitude = models.FloatField(default=False)
    latitude = models.FloatField(default=False)
    class Meta:
        verbose_name = 'Gas Station Info'

    def __str__(self):
        return "{}'s gasstationinfo".format(self.id.__str__())

class SearchLog(models.Model):#加油站資訊
    user_id = models.CharField(default='none', primary_key=True, null=False, max_length=512)
    isgogoro = models.BooleanField(default=False)
    isself = models.BooleanField(default=False)
    name = models.CharField('N/A', null=False, max_length=20)
    city = models.CharField('N/A', null=False, max_length=20)
    town = models.CharField('N/A', null=False, max_length=20)
    address = models.CharField('N/A', null=False, max_length=50)
    phone = models.CharField('N/A', null=False, max_length=20)
    servicenum = models.CharField('N/A', null=False, max_length=20)
    isbusiness = models.BooleanField(default=False)
    ishighway = models.BooleanField(default=False)
    is92 = models.BooleanField(default=False)
    is95 = models.BooleanField(default=False)
    is98 = models.BooleanField(default=False)
    isgas = models.BooleanField(default=False)
    iscoal = models.BooleanField(default=False)
    isdiesel = models.BooleanField(default=False)
    ismember = models.BooleanField(default=False)
    isselfcard = models.BooleanField(default=False)
    isselfdiesel = models.BooleanField(default=False)
    isEI = models.BooleanField(default=False)
    iseasycard = models.BooleanField(default=False)
    isipasscard = models.BooleanField(default=False)
    ishappycash = models.BooleanField(default=False)
    isetag = models.BooleanField(default=False)
    ismaintain = models.BooleanField(default=False)
    isaddwater = models.BooleanField(default=False)
    isaddair = models.BooleanField(default=False)
    isElectricity = models.BooleanField(default=False)
    washtype = models.CharField('N/A', null=False, max_length=20)
    bussinesstime = models.CharField('N/A', null=False, max_length=20)
    longitude = models.FloatField(default=False)
    latitude = models.FloatField(default=False)
    class Meta:
        verbose_name = 'Search Log'

    def __str__(self):
        return "{}'s serachlog".format(self.user_id.__str__())

class GogoroStationInfo(models.Model):#Gogoro電池資訊站
    Id = models.CharField('N/A',primary_key=True, null=False, max_length=50)
    LocName = models.CharField('N/A', null=False, max_length=100)
    Longitude = models.FloatField(default=False)
    Latitude = models.FloatField(default=False)
    ZipCode = models.IntegerField(default=0)
    Address = models.CharField('N/A', null=False, max_length=100)
    District = models.CharField('N/A', null=False, max_length=100)
    City = models.CharField('N/A', null=False, max_length=100)
    State = models.IntegerField(default=0)
    StorePhoto = models.CharField('N/A', null=False, max_length=100)
    RId = models.CharField('N/A', null=False, max_length=100)
    class Meta:
        verbose_name = 'Gogoro Station Info'

    def __str__(self):
        return "{}'s gogorostationinfo".format(self.id.__str__())
