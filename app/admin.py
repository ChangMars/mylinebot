from django.contrib import admin

# Register your models here.
from app.models import UserProfile, TestModel

admin.site.register(UserProfile)#在Django admin中註冊此模組
admin.site.register(TestModel)
