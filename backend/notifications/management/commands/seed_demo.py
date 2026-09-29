from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Trigger,NotificationTemplate
class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        User=get_user_model()
        u,created=User.objects.get_or_create(email="admin@notifyhub.local",defaults={"username":"admin","first_name":"Akarshit","is_staff":True,"is_superuser":True})
        if created: u.set_password("Admin@12345"); u.save()
        for name,key,verb in [("Login","login","logged in"),("Logout","logout","logged out")]:
            t,_=Trigger.objects.get_or_create(key=key,defaults={"name":name,"description":f"User {verb} to NotifyHub."})
            bodies={
             "whatsapp":f"Hello {{{{first_name}}}}, you {verb} to NotifyHub.",
             "email":f"Hello {{{{first_name}}}}, you {verb} to NotifyHub.",
             "web_push":f"Hello {{{{first_name}}}}, you {verb} to NotifyHub.",
            }
            for ch,body in bodies.items():
                NotificationTemplate.objects.update_or_create(trigger=t,channel=ch,defaults={
                    "name":f"{name} {ch.replace('_',' ').title()}","subject":f"{name} Notification","body":body})
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: admin@notifyhub.local / Admin@12345"))
