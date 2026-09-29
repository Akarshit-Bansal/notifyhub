from django.db import models

class Trigger(models.Model):
    name=models.CharField(max_length=100)
    key=models.SlugField(unique=True)
    description=models.TextField(blank=True)
    active=models.BooleanField(default=True)
    whatsapp_enabled=models.BooleanField(default=True)
    email_enabled=models.BooleanField(default=True)
    web_push_enabled=models.BooleanField(default=True)
    def __str__(self): return self.name

class NotificationTemplate(models.Model):
    CHANNELS=[("whatsapp","WhatsApp"),("email","Email"),("web_push","Web Push")]
    trigger=models.ForeignKey(Trigger,on_delete=models.CASCADE,related_name="templates")
    channel=models.CharField(max_length=20,choices=CHANNELS)
    name=models.CharField(max_length=150)
    subject=models.CharField(max_length=255,blank=True)
    body=models.TextField()
    active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["trigger","channel"],name="one_template_channel")]

class PushSubscription(models.Model):
    endpoint=models.URLField(unique=True)
    p256dh=models.TextField()
    auth=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

class NotificationLog(models.Model):
    STATUS=[("success","Success"),("failed","Failed")]
    trigger=models.ForeignKey(Trigger,null=True,on_delete=models.SET_NULL)
    channel=models.CharField(max_length=20)
    recipient=models.CharField(max_length=255)
    status=models.CharField(max_length=10)
    provider_id=models.CharField(max_length=255,blank=True)
    message=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
