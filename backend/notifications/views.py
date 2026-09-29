from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Trigger,NotificationTemplate,NotificationLog,PushSubscription
from .serializers import TriggerSerializer,NotificationTemplateSerializer,NotificationLogSerializer
from .services import send

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request): return Response({"status":"ok"})

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    email = str(request.data.get("email", "")).strip().lower()
    password = str(request.data.get("password", ""))

    user = User.objects.filter(email__iexact=email).first()

    if not user or not user.check_password(password):
        return Response(
            {"error": "Email or password is incorrect."},
            status=400,
        )

    if not user.is_active:
        return Response(
            {"error": "User account is inactive."},
            status=400,
        )

    login(request, user)

    return Response({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    })

@api_view(["POST"])
def logout_view(request):
    logout(request); return Response({"success":True})

@api_view(["GET"])
@permission_classes([AllowAny])
def me(request):
    return Response({
        "authenticated": request.user.is_authenticated,
        "email": request.user.email if request.user.is_authenticated else "",
        "first_name": request.user.first_name if request.user.is_authenticated else "",
    })
@api_view(["GET","POST"])
def triggers(request):
    if request.method=="GET": return Response(TriggerSerializer(Trigger.objects.prefetch_related("templates"),many=True).data)
    s=TriggerSerializer(data=request.data); s.is_valid(raise_exception=True); s.save(); return Response(s.data,201)

@api_view(["GET","POST","PUT","PATCH"])
def template_list(request):
    if request.method=="GET": return Response(NotificationTemplateSerializer(NotificationTemplate.objects.all(),many=True).data)
    if request.method=="POST":
        s=NotificationTemplateSerializer(data=request.data); s.is_valid(raise_exception=True); s.save(); return Response(s.data,201)
    obj=NotificationTemplate.objects.get(id=request.data["id"]); s=NotificationTemplateSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save(); return Response(s.data)

@api_view(["POST"])
def test_send(request):
    t=NotificationTemplate.objects.get(id=request.data["template_id"])
    recipient=str(request.data.get("recipient","")).strip()
    ctx={
    "first_name": getattr(request.user, "first_name", "") or "User",
    "email": getattr(request.user, "email", ""),
    }
    if t.channel=="web_push": recipient="browser"
    try:
        pid=send(t,recipient,ctx)
        log=NotificationLog.objects.create(trigger=t.trigger,channel=t.channel,recipient=recipient,status="success",provider_id=pid,message="Sent successfully.")
        return Response({"success":True,"provider_id":pid,"log_id":log.id})
    except Exception as e:
        NotificationLog.objects.create(trigger=t.trigger,channel=t.channel,recipient=recipient,status="failed",message=str(e))
        return Response({"success":False,"error":str(e)},status=400)

@api_view(["GET"])
def logs(request): return Response(NotificationLogSerializer(NotificationLog.objects.order_by("-created_at")[:100],many=True).data)

@api_view(["GET"])
def push_public_key(request):
    return Response({"public_key":settings.VAPID_PUBLIC_KEY})

@api_view(["POST"])
def push_subscribe(request):
    s=request.data
    endpoint=s.get("endpoint"); keys=s.get("keys",{})
    if not endpoint or not keys.get("p256dh") or not keys.get("auth"): return Response({"error":"Invalid subscription"},400)
    PushSubscription.objects.update_or_create(endpoint=endpoint,defaults={"p256dh":keys["p256dh"],"auth":keys["auth"]})
    return Response({"success":True})
