# Credit:- "insta :-_echo.del.alma_"

import sys
import traceback
import json
import os
from datetime import datetime

print("🚀 STARTING IMPORTS - PHASE 1")

try:
    print("1. Importing Flask...")
    from flask import Flask, request, jsonify
    print("✅ Flask imported successfully")
except Exception as e:
    print(f"💥 FLASK IMPORT FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Importing asyncio...")
    import asyncio
    print("✅ asyncio imported successfully")
except Exception as e:
    print(f"💥 ASYNCIO IMPORT FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Importing Crypto...")
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    print("✅ Crypto imported successfully")
except Exception as e:
    print(f"💥 CRYPTO IMPORT FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Importing protobuf...")
    from google.protobuf.json_format import MessageToJson
    print("✅ Protobuf JSON imported successfully")
except Exception as e:
    print(f"💥 PROTOBUF JSON IMPORT FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Importing other utilities...")
    import binascii
    import aiohttp
    import requests
    import json
    import os
    print("✅ Utilities imported successfully")
except Exception as e:
    print(f"💥 UTILITIES IMPORT FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("6. Importing custom protobuf files...")
    import like_pb2
    import like_count_pb2
    import uid_generator_pb2
    print("✅ Custom protobuf imported successfully")
except Exception as e:
    print(f"💥 CUSTOM PROTOBUF IMPORT FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print("🎉 ALL IMPORTS SUCCESSFUL - Starting Flask app...")

app = Flask(__name__)

# ==================== SIMPLE TOKEN TRACKING (No Database) ====================

# In-memory storage (resets on server restart - good enough for demo)
used_tokens_today = {}

def get_used_tokens_today(target_uid, server_name):
    """Get tokens already used for this UID today (simplified)"""
    key = f"{target_uid}_{server_name}"
    today = datetime.now().strftime("%Y-%m-%d")
    
    if key in used_tokens_today and used_tokens_today[key]["date"] == today:
        return used_tokens_today[key]["tokens"]
    return []

def record_like_usage(target_uid, tokens_used, server_name):
    """Record which tokens were used for this UID (simplified)"""
    key = f"{target_uid}_{server_name}"
    today = datetime.now().strftime("%Y-%m-%d")
    
    if key not in used_tokens_today or used_tokens_today[key]["date"] != today:
        used_tokens_today[key] = {"date": today, "tokens": []}
    
    used_tokens_today[key]["tokens"].extend(tokens_used)

def get_remaining_tokens(available_tokens, used_tokens):
    """Get tokens that haven't been used today"""
    return [token for token in available_tokens if token not in used_tokens]

# ==================== CORE FUNCTIONALITY ====================

def get_headers(token):
    return {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB50"
    }

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
    except Exception as e:
        print(f"Token loading error: {e}")
        return [{"token": "default_token"}]

def encrypt_message(plaintext):
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%' 
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return binascii.hexlify(encrypted_message).decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""

def create_protobuf_message(user_id, region):
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        print(f"Protobuf creation error: {e}")
        return b""

def get_server_url(server_name, endpoint_type="like"):
    base_urls = {
        "IND": "https://client.ind.freefiremobile.com/",
        "BR": "https://client.us.freefiremobile.com/",
        "US": "https://client.us.freefiremobile.com/", 
        "SAC": "https://client.us.freefiremobile.com/",
        "NA": "https://client.us.freefiremobile.com/",
    }
    base_url = base_urls.get(server_name, "https://clientbp.ggblueshark.com/")
    return base_url + ("LikeProfile" if endpoint_type == "like" else "GetPlayerPersonalShow")

async def send_request(encrypted_uid, token, url):
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = get_headers(token)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers, timeout=30) as response:
                return response.status, token
    except Exception as e:
        print(f"Request error: {e}")
        return 500, token

async def send_multiple_requests(uid, server_name, like_count, available_tokens):
    try:
        region = server_name
        protobuf_message = create_protobuf_message(uid, region)
        encrypted_uid = encrypt_message(protobuf_message)
        
        url = get_server_url(server_name, "like")
        
        like_count = max(1, min(len(available_tokens), like_count))
        
        tasks = []
        for i in range(like_count):
            token_data = available_tokens[i]
            token = token_data["token"]
            tasks.append(send_request(encrypted_uid, token, url))
        
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        print(f"Multiple requests error: {e}")
        return []

def create_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.krishna_ = int(uid)
        message.teamXdarks = 1
        return message.SerializeToString()
    except Exception as e:
        print(f"UID protobuf error: {e}")
        return b""

def enc(uid):
    try:
        protobuf_data = create_protobuf(uid)
        encrypted_uid = encrypt_message(protobuf_data)
        return encrypted_uid
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""

def make_request(encrypt, server_name, token):
    try:
        url = get_server_url(server_name, "info")
        edata = bytes.fromhex(encrypt)
        headers = get_headers(token)

        response = requests.post(url, data=edata, headers=headers, verify=True, timeout=30)
        hex_data = response.content.hex()
        binary = bytes.fromhex(hex_data)
        return decode_protobuf(binary)
    except Exception as e:
        print(f"Make request error: {e}")
        return None

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except Exception as e:
        print(f"Protobuf decode error: {e}")
        return None

# ==================== FLASK ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        "message": "Free Fire Likes API - FULLY WORKING!",
        "status": "active",
        "usage": "/like?uid=USER_ID&server_name=SERVER&like_count=COUNT",
        "credits": {
            "Developer": "God",
            "Instagram": "_echo.del.alma_"
        }
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    try:
        # Support both 'uid' and 'user_id' parameters
        uid = request.args.get("uid") or request.args.get("user_id")
        server_name = request.args.get("server_name", "").upper()
        like_count = request.args.get("like_count", "10")
        
        print(f"📥 Received request - UID: {uid}, Server: {server_name}, Likes: {like_count}")
        
        # Input validation
        if not uid or not server_name:
            return jsonify({
                "error": "UID and server_name are required",
                "example": "/like?uid=123456&server_name=IND&like_count=10"
            }), 400
        
        try:
            uid = int(uid)
        except ValueError:
            return jsonify({"error": "UID must be a valid number"}), 400
        
        try:
            like_count = int(like_count)
            if like_count < 1 or like_count > 100:
                return jsonify({"error": "like_count must be between 1 and 100"}), 400
        except ValueError:
            return jsonify({"error": "like_count must be a valid number"}), 400

        # Process the request
        all_tokens_data = load_tokens(server_name)
        if not all_tokens_data:
            return jsonify({"error": "No tokens available for this server"}), 500
        
        all_tokens = [token_data["token"] for token_data in all_tokens_data]
        
        # Get tokens already used today (simplified)
        used_tokens_today_list = get_used_tokens_today(uid, server_name)
        available_tokens = get_remaining_tokens(all_tokens, used_tokens_today_list)
        
        print(f"🔑 Token Status - Total: {len(all_tokens)}, Used Today: {len(used_tokens_today_list)}, Available: {len(available_tokens)}")
        
        if not available_tokens:
            return jsonify({
                "status": "⏰ Daily Limit Reached",
                "message": "All available IDs have liked this profile today",
                "reset_time": "🕓 Resets at 4:00 AM IST"
            }), 400
        
        # Filter available tokens data
        available_tokens_data = [token_data for token_data in all_tokens_data if token_data["token"] in available_tokens]
            
        token = available_tokens_data[0]['token']
        encrypted_uid = enc(uid)
        
        if not encrypted_uid:
            return jsonify({"error": "Encryption failed"}), 500

        # Get initial like count
        print("📊 Getting initial like count...")
        before = make_request(encrypted_uid, server_name, token)
        if before is None:
            return jsonify({"error": "Failed to get initial profile information"}), 500
            
        before_json = json.loads(MessageToJson(before))
        before_like = before_json.get('AccountInfo', {}).get('Likes', 0)
        before_like = int(before_like) if before_like else 0
        
        # Get player info
        player_name = before_json.get('AccountInfo', {}).get('PlayerNickname', 'Unknown Player')
        
        print(f"📊 Initial likes: {before_like}, Player: {player_name}")
        
        # Calculate actual likes to send (limited by available tokens)
        actual_likes_to_send = min(like_count, len(available_tokens))
        
        # Send likes
        print(f"🚀 Sending {actual_likes_to_send} likes...")
        results = asyncio.run(send_multiple_requests(uid, server_name, actual_likes_to_send, available_tokens_data))
        
        # Extract successful tokens
        successful_tokens = [token for status, token in results if status == 200]
        successful_count = len(successful_tokens)
        
        # Record usage (simplified)
        record_like_usage(uid, successful_tokens, server_name)
        
        print(f"✅ Likes sent - Successful: {successful_count}/{actual_likes_to_send}")
        
        # Get updated like count
        print("📊 Getting updated like count...")
        after = make_request(encrypted_uid, server_name, token)
        if after is None:
            return jsonify({"error": "Failed to get updated profile information"}), 500
            
        after_json = json.loads(MessageToJson(after))
        after_like = int(after_json['AccountInfo']['Likes'])
        
        like_given = after_like - before_like
        
        # Calculate already delivered (from previous requests today)
        already_delivered = len(used_tokens_today_list)
        
        # Build response in your exact format
        result = {
            "status": "✅ Success" if like_given > 0 else "⚠️ No Change",
            "player_info": {
                "name": player_name,
                "uid": f"🆔 {uid}",
                "server": f"🌍 {server_name}"
            },
            "Like_analytics": {
                "before": f"📊 {before_like}",
                "after": f"📈 {after_like}",
                "added": f"✅ +{like_given}",
                "requested": f"🎯 {like_count}",
                "already delivered": f"🚀 {already_delivered + successful_count}"
            },
            "Management": {
                "total likes request per day": f"🔑 {len(all_tokens)}",
                "used_today": f"⏰ {already_delivered + successful_count}",
                "remaining_today": f"🔄 {len(available_tokens) - successful_count}",
                "reset_time": "🕓 4:00 AM IST"
            },
            "next_actions": {
                "remaining_likes": f"📨 {len(available_tokens) - successful_count} likes are available now",
                "available_tomorrow": f"🌅 {already_delivered + successful_count} likes will be available tomorrow"
            },
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_"
            }
        }
        
        print("🎉 Request completed successfully!")
        return jsonify(result)
        
    except Exception as e:
        print(f"💥 Error in handle_requests: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_"
            }
        }), 500

# For Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
