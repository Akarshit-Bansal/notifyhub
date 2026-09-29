# NotifyHub — Fresh Build (No Meta)

This version deliberately does **not** use Meta.

Channels:
- WhatsApp: Twilio WhatsApp Sandbox, using an approved Twilio Content Template
- Email: Postmark API
- Web Push: native browser Push API + VAPID (`pywebpush`), no OneSignal

The project has a real admin login, trigger/channel matrix, editable templates, test-send buttons, browser push subscription, and delivery logs.

## 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000
```

Admin login:
- email: admin@notifyhub.local
- password: Admin@12345

Change the password before deployment.

## 2. Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

## 3. WhatsApp — Twilio, not Meta

Use your Twilio WhatsApp Sandbox.

Required:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_WHATSAPP_FROM
- TWILIO_WHATSAPP_CONTENT_SID

The Sandbox only permits business-initiated messages with its pre-approved templates. Put the HX... Content SID shown by your Twilio Sandbox in `TWILIO_WHATSAPP_CONTENT_SID`.

For the built-in Appointment Reminder template, Twilio documents an example Content SID:
`HXb5b62575e6e4ff6129ad7c8efe1f983e`

If your Sandbox exposes a different SID, use the SID shown in your account.

For free-form session text, first message the Sandbox from the recipient WhatsApp. The 24-hour customer-service window is controlled by Twilio/WhatsApp; this project therefore uses the approved ContentSid path so Test Send does not depend on that window.

## 4. Email — Postmark

Put these in backend/.env:

POSTMARK_SERVER_TOKEN=...
POSTMARK_FROM_EMAIL=verified-sender@example.com

The sender must be accepted/verified by your Postmark account.

## 5. Web Push — native browser push

Generate VAPID keys once:

```powershell
pip install py-vapid
python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print('PRIVATE=',v.private_key.pem().decode()); print('PUBLIC=',v.public_key.public_bytes().decode())"
```

Put the values in `.env`:

```env
VAPID_PRIVATE_KEY=...
VAPID_PUBLIC_KEY=...
VAPID_CLAIMS_EMAIL=mailto:admin@example.com
```

The frontend gets the public key from `/api/push/public-key/`, subscribes the browser, and stores the subscription in Django. Test Send then sends through `pywebpush`.

## 6. Important

Do not commit `.env`.
Do not paste API tokens into GitHub.
The frontend never receives provider secrets.

## Deployment

Backend:
- Render
- set all backend environment variables
- build: `pip install -r requirements.txt && python manage.py migrate`
- start: `gunicorn config.wsgi:application`

Frontend:
- Vercel
- build: `npm run build`
- environment: `VITE_API_URL=https://YOUR-RENDER-URL`

