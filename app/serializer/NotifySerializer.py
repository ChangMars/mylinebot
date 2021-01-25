from rest_framework import serializers
from app.models import NotifyModel

class NotifySerializer(serializers.ModelSerializer):

    class Meta:
        model = NotifyModel
        fields = '__all__'
        # fields = ('name', 'location')