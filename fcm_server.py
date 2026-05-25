"""
FCM Backend Server
==================
Jalankan: python fcm_server.py
Lalu buka fcm_cms.html di browser
Install: pip install flask flask-cors google-auth requests
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
import requests
import os

app = Flask(__name__)
CORS(app)

PROJECT_ID = "klik-ngoerah"
SERVICE_ACCOUNT_FILE = "serviceAccount.json"

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    req = google.auth.transport.requests.Request()
    credentials.refresh(req)
    return credentials.token

def build_and_send(payload):
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp

@app.route('/send', methods=['POST'])
def send_to_token():
    body = request.json
    token = body.get('token')
    title = body.get('title')
    message_body = body.get('body')
    data = body.get('data', {})
    if not token or not title or not message_body:
        return jsonify({'error': 'token, title, body wajib diisi'}), 400
    payload = {
        "message": {
            "token": token,
            "notification": {"title": title, "body": message_body},
            "android": {
                "priority": "high",
                "notification": {
                    "sound": "default",
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                }
            },
        }
    }
    if data:
        payload["message"]["data"] = {k: str(v) for k, v in data.items()}
    resp = build_and_send(payload)
    print(f"STATUS: {resp.status_code}")
    print(f"RESPONSE: {resp.json()}")
    if resp.status_code == 200:
        return jsonify({'success': True, 'response': resp.json()})
    else:
        return jsonify({'error': resp.json()}), resp.status_code

@app.route('/send-topic', methods=['POST'])
def send_to_topic():
    body = request.json
    topic = body.get('topic', 'semua_user')
    title = body.get('title')
    message_body = body.get('body')
    data = body.get('data', {})
    if not title or not message_body:
        return jsonify({'error': 'title dan body wajib diisi'}), 400
    payload = {
        "message": {
            "topic": topic,
            "notification": {"title": title, "body": message_body},
            "android": {
                "priority": "high",
                "notification": {
                    "sound": "default",
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                }
            },
        }
    }
    if data:
        payload["message"]["data"] = {k: str(v) for k, v in data.items()}
    resp = build_and_send(payload)
    if resp.status_code == 200:
        return jsonify({'success': True, 'response': resp.json()})
    else:
        return jsonify({'error': resp.json()}), resp.status_code

if __name__ == '__main__':
    print("=" * 50)
    print("FCM Backend Server running di port 5000!")
    print("Endpoint:")
    print("  POST /send        → kirim ke 1 device (by token)")
    print("  POST /send-topic  → kirim ke semua user (by topic)")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
