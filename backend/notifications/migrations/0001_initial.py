from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True; dependencies=[]
    operations=[
      migrations.CreateModel(name="Trigger",fields=[
       ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
       ("name",models.CharField(max_length=100)),("key",models.SlugField(unique=True)),("description",models.TextField(blank=True)),
       ("active",models.BooleanField(default=True)),("whatsapp_enabled",models.BooleanField(default=True)),
       ("email_enabled",models.BooleanField(default=True)),("web_push_enabled",models.BooleanField(default=True))]),
      migrations.CreateModel(name="NotificationTemplate",fields=[
       ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
       ("channel",models.CharField(choices=[("whatsapp","WhatsApp"),("email","Email"),("web_push","Web Push")],max_length=20)),
       ("name",models.CharField(max_length=150)),("subject",models.CharField(blank=True,max_length=255)),("body",models.TextField()),
       ("active",models.BooleanField(default=True)),
       ("trigger",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="templates",to="notifications.trigger"))]),
      migrations.CreateModel(name="PushSubscription",fields=[
       ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
       ("endpoint",models.URLField(unique=True)),("p256dh",models.TextField()),("auth",models.TextField()),
       ("created_at",models.DateTimeField(auto_now_add=True))]),
      migrations.CreateModel(name="NotificationLog",fields=[
       ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
       ("channel",models.CharField(max_length=20)),("recipient",models.CharField(max_length=255)),
       ("status",models.CharField(max_length=10)),("provider_id",models.CharField(blank=True,max_length=255)),
       ("message",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),
       ("trigger",models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,to="notifications.trigger"))]),
      migrations.AddConstraint(model_name="notificationtemplate",constraint=models.UniqueConstraint(fields=("trigger","channel"),name="one_template_channel"))
    ]
