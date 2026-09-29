from rest_framework import serializers
from .models import Trigger,NotificationTemplate,NotificationLog
class TriggerSerializer(serializers.ModelSerializer):
    templates=serializers.SerializerMethodField()
    def get_templates(self,obj): return NotificationTemplateSerializer(obj.templates.all(),many=True).data
    class Meta: model=Trigger; fields="__all__"
class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta: model=NotificationTemplate; fields="__all__"
class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta: model=NotificationLog; fields="__all__"
