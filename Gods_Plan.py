# Free Fire Likes API - God's Plan
# Developer: God | Instagram: _echo.del.alma_

from flask import Flask, request, jsonify
import asyncio
import aiohttp
import requests
import json

app = Flask(__name__)

# Simple in-memory storage
used_tokens_today = {}
TOTAL_TOKENS = 100

def get_used_tokens_today(target_uid, server_name):
    key = f"{target_uid}_{server_name}"
    return used_tokens_today.get(key, [])

def record_like_usage(target_uid, tokens_used, server_name):
    key = f"{target_uid}_{server_name}"
    if key not in used_tokens_today:
        used_tokens_today[key] = []
    used_tokens_today[key].extend(tokens_used)

def load_tokens(server_name):
    try:
        if server_name == "IND":
            with open("token_ind.json", "r") as f:
                return json.load(f)
        elif server_name in {"BR", "US", "SAC", "NA"}:
            with open("token_br.json", "r") as f:
                return json.load(f)
        else:
            with open("token_bd.json", "r") as f:
                return json.load(f)
    except:
        return [{"token": "default_token"}]

async def send_request(token, url):
    try:
        headers = {
            'User-Agent': "Dalvik/2.1.0",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=b"test", headers=headers, timeout=10) as response:
                return response.status, token
    except:
        return 500, token

async def send_multiple_requests(uid, server_name, like_count, available_tokens):
    try:
        url = "https://client.ind.freefiremobile.com/LikeProfile"
        tasks = []
        for i in range(min(like_count, len(available_tokens))):
            token_data = available_tokens[i]
            token = token_data["token"]
            tasks.append(send_request(token, url))
        return await asyncio.gather(*tasks)
    except:
        return []

@app.route('/')
def home():
    return jsonify({
        "message": "Free Fire Likes API - God's Plan",
        "status": "active"
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    try:
        uid = request.args.get("uid") or request.args.get("user_id")
        server_name = request.args.get("server_name", "").upper()
        like_count = request.args.get("like_count", "5")
        
        if not uid or not server_name:
            return jsonify({"error": "UID and server_name are required"}), 400
        
        # Mock response for testing
        result = {
            "name": "TestPlayer",
            "uid": f"🆔 {uid}",
            "server": f"🌍 {server_name}",
            "status": "success",
            "player_info": f"👤 TestPlayer | 🆔 {uid} | 🌍 {server_name}",
            "Like_analytics": {
                "before": "📊 53921",
                "after": "📈 53970",
                "added": "✅ +49",
                "requested": f"🎯 {like_count}",
                "already delivered": "🚀 51"
            },
            "Management": {
                "total likes request per day": "🔑 100",
                "used_today": "⏰ 90",
                "remaining_today": "🔄 10",
                "reset_time": "🕓 4:00 AM IST"
            },
            "next_actions": {
                "remaining_likes": "📨 10 likes are available now",
                "available_tomorrow": "🌅 90 likes will be available tomorrow"
            },
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_"
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel handler - SIMPLE VERSION
def handler(request, context):
    return app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
