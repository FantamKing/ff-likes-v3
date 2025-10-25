# -*- coding: utf-8 -*-
# Credit:- "insta :-_echo.del.alma_"
# Developed by God

import sys
import traceback

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

print("🎉 ALL IMPORTS SUCCESSFUL - Starting God's Plan...")

app = Flask(__name__)

# ==================== MAIN FUNCTIONALITY ====================

def get_headers(token):
    return {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2022.3.21f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB56"
    }

def load_tokens(server_name):
    try:
        if server_name == "IND":
            with open("token_ind.json", "r") as f:
                data = json.load(f)
                # Handle both array and object formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "token" in data:
                    return [data]  # Convert object to array
                else:
                    return [{"token": "default_token"}]
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
                return response.status
    except Exception as e:
        print(f"Request error: {e}")
        return 500

async def send_multiple_requests(uid, server_name, like_count):
    try:
        region = server_name
        protobuf_message = create_protobuf_message(uid, region)
        encrypted_uid = encrypt_message(protobuf_message)
        
        url = get_server_url(server_name, "like")
        tokens = load_tokens(server_name)
        
        like_count = max(1, min(100, like_count))
        
        tasks = []
        for i in range(like_count):
            token = tokens[i % len(tokens)]["token"]
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
        
        # Check if response is successful
        if response.status_code != 200:
            print(f"API returned status: {response.status_code}")
            return None
            
        hex_data = response.content.hex()
        if not hex_data:
            print("Empty response from API")
            return None
            
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
        "message": "God's Plan is Active! 🙏",
        "status": "Divine Intervention Ready",
        "usage": "/like?uid=USER_ID&server_name=SERVER&like_count=COUNT",
        "note": "Daily tracking disabled - MongoDB integration coming soon",
        "credits": {
            "Developer": "👑 God",
            "Instagram": "📱 _echo.del.alma_"
        }
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    try:
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
            like_count = int(like_count)
            if like_count < 1 or like_count > 100:
                return jsonify({"error": "like_count must be between 1 and 100"}), 400
        except ValueError:
            return jsonify({"error": "UID and like_count must be valid numbers"}), 400

        # Process the request (NO DAILY TRACKING)
        data = load_tokens(server_name)
        if not data:
            return jsonify({"error": "No tokens available for this server"}), 500
            
        token = data[0]['token']
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
        
        # Get initial profile info
        initial_name = before_json.get('AccountInfo', {}).get('PlayerNickname', 'Unknown')
        initial_level = before_json.get('AccountInfo', {}).get('Level', 'N/A')
        
        print(f"📊 Initial likes: {before_like}, Player: {initial_name}, Level: {initial_level}")
        
        # Send likes
        print(f"🚀 Sending {like_count} likes...")
        results = asyncio.run(send_multiple_requests(uid, server_name, like_count))
        print(f"✅ Likes sent - Results: {results}")
        
        # Get updated like count
        print("📊 Getting updated like count...")
        after = make_request(encrypted_uid, server_name, token)
        if after is None:
            return jsonify({"error": "Failed to get updated profile information"}), 500
            
        after_json = json.loads(MessageToJson(after))
        after_like = int(after_json['AccountInfo']['Likes'])
        player_id = int(after_json['AccountInfo']['UID'])
        name = str(after_json['AccountInfo']['PlayerNickname'])
        
        # Get additional profile info
        level = after_json['AccountInfo'].get('Level', 'N/A')
        exp = after_json['AccountInfo'].get('Exp', 'N/A')
        avatar = after_json['AccountInfo'].get('Avatar', 'N/A')
        
        like_given = after_like - before_like
        status = 1 if like_given > 0 else 2
        
        result = {
            "status": status,
            "player_info": {
                "name": name,
                "uid": player_id,
                "server": server_name,
                "level": level,
                "experience": exp,
                "avatar": avatar
            },
            "Like_analytics": {
                "before": f"📊 {before_like}",
                "after": f"📈 {after_like}",
                "added": f"✅ +{like_given}",
                "requested": f"🎯 {like_count}"
            },
            "note": "Daily tracking disabled - MongoDB integration coming soon",
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

# Debug route
@app.route('/debug-request/<uid>/<server_name>')
def debug_request(uid, server_name):
    """Debug route to see what's happening with the request"""
    try:
        data = load_tokens(server_name.upper())
        if not data:
            return jsonify({"error": "No tokens available"})
            
        token = data[0]['token']
        encrypted_uid = enc(uid)
        
        if not encrypted_uid:
            return jsonify({"error": "Encryption failed"})
        
        url = get_server_url(server_name.upper(), "info")
        edata = bytes.fromhex(encrypted_uid)
        headers = get_headers(token)
        
        response = requests.post(url, data=edata, headers=headers, verify=True, timeout=30)
        
        debug_info = {
            "url": url,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body_preview": response.text[:500] if response.text else "Empty response",
            "response_hex": response.content.hex()[:100] + "..." if response.content else "No content"
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            "error": f"Debug request failed: {str(e)}",
            "traceback": traceback.format_exc()
        })

# For Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
