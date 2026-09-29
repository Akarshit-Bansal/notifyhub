from django.contrib import admin
from .models import Trigger,NotificationTemplate,PushSubscription,NotificationLog
admin.site.register([Trigger,NotificationTemplate,PushSubscription,NotificationLog])
