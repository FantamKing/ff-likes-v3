# Credit:- "insta :-_echo.del.alma_"
# Developer: God
# This is the main Like API - God's Plan 🙏
# Instagram: _echo.del.alma_

import sys
import traceback

print("🚀 THINKING GOD'S PLAN -")
print("🙏 Planned by God | Instagram: _echo.del.alma_")

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

print("🎉 ALL IMPORTS SUCCESSFUL - Starting God's Plan API...")
print("🌟 God's Plan is activated - Free Fire Likes API Ready!")
print("📱 Instagram: _echo.del.alma_")

app = Flask(__name__)

# ==================== GOD'S PLAN - LIKES FUNCTIONALITY ====================

def get_headers(token):
    """God's Plan - Header Configuration """
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
    """God's Plan - Token Loading System 🙏"""
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
    """God's Plan - Encryption System 🙏"""
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
    """God's Plan - Protobuf Message Creation 🙏"""
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        print(f"Protobuf creation error: {e}")
        return b""

def get_server_url(server_name, endpoint_type="like"):
    """God's Plan - Server URL Management 🙏"""
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
    """God's Plan - Single Request Handler 🙏"""
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
    """God's Plan - Multiple Requests Handler 🙏"""
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
    """God's Plan - UID Protobuf Creation 🙏"""
    try:
        message = uid_generator_pb2.uid_generator()
        message.krishna_ = int(uid)
        message.teamXdarks = 1
        return message.SerializeToString()
    except Exception as e:
        print(f"UID protobuf error: {e}")
        return b""

def enc(uid):
    """God's Plan - UID Encryption 🙏"""
    try:
        protobuf_data = create_protobuf(uid)
        encrypted_uid = encrypt_message(protobuf_data)
        return encrypted_uid
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""

def make_request(encrypt, server_name, token):
    """God's Plan - Profile Information Request 🙏"""
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
    """God's Plan - Protobuf Decoding 🙏"""
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except Exception as e:
        print(f"Protobuf decode error: {e}")
        return None

# ==================== GOD'S PLAN - FLASK ROUTES ====================

@app.route('/')
def home():
    """God's Plan - Main API Route 🙏"""
    return jsonify({
        "message": "Free Fire Likes API - GOD'S PLAN 🙏",
        "status": "active",
        "version": "God's Plan v1.0",
        "usage": "/like?uid=USER_ID&server_name=SERVER&like_count=COUNT",
        "developer_notes": "This is God's Plan - giving everyone likes!",
        "credits": {
            "Developer": "👑 God",
            "Instagram": "📱 _echo.del.alma_",
            "message": "Planned by God 🙏"
        }
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    """God's Plan - Like Request Handler 🙏"""
    try:
        # Support both 'uid' and 'user_id' parameters
        uid = request.args.get("uid") or request.args.get("user_id")
        server_name = request.args.get("server_name", "").upper()
        like_count = request.args.get("like_count", "10")
        
        print(f"📥 God's Plan - Received request: UID: {uid}, Server: {server_name}, Likes: {like_count}")
        
        # Input validation
        if not uid or not server_name:
            return jsonify({
                "error": "UID and server_name are required for God's Plan",
                "example": "/like?uid=123456&server_name=IND&like_count=10",
                "credits": {
                    "Developer": "👑 God",
                    "Instagram": "📱 _echo.del.alma_",
                    "message": "God's needs proper parameters 🙏"
                }
            }), 400
        
        try:
            uid = int(uid)
        except ValueError:
            return jsonify({
                "error": "UID must be a valid number for God's Plan",
                "credits": {
                    "Developer": "👑 God", 
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 400
        
        try:
            like_count = int(like_count)
            if like_count < 1 or like_count > 100:
                return jsonify({
                    "error": "like_count must be between 1 and 100 for God's Plan",
                    "credits": {
                        "Developer": "👑 God",
                        "Instagram": "📱 _echo.del.alma_"
                    }
                }), 400
        except ValueError:
            return jsonify({
                "error": "like_count must be a valid number for God's Plan",
                "credits": {
                    "Developer": "👑 God",
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 400

        # Process the request - God's Plan in action yoo yoo!
        data = load_tokens(server_name)
        if not data:
            return jsonify({
                "error": "No tokens available for this server in God's Plan",
                "credits": {
                    "Developer": "👑 God",
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 500
            
        token = data[0]['token']
        encrypted_uid = enc(uid)
        
        if not encrypted_uid:
            return jsonify({
                "error": "Encryption failed in God's Plan",
                "credits": {
                    "Developer": "👑 God",
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 500

        # Get initial like count
        print("📊 God is counting...")
        before = make_request(encrypted_uid, server_name, token)
        if before is None:
            return jsonify({
                "error": "Failed to see the profile information by GOD",
                "credits": {
                    "Developer": "👑 God",
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 500
            
        before_json = json.loads(MessageToJson(before))
        before_like = before_json.get('AccountInfo', {}).get('Likes', 0)
        before_like = int(before_like) if before_like else 0
        
        # Get initial profile info
        initial_name = before_json.get('AccountInfo', {}).get('PlayerNickname', 'Unknown')
        
        print(f"📊 God's Plan - Initial likes: {before_like}, Player: {initial_name}")
        
        # Send likes - Executing God's Plan!
        print(f"🚀 God is Sending {like_count} likes...")
        results = asyncio.run(send_multiple_requests(uid, server_name, like_count))
        print(f"✅ God's Plan - Likes sent: {results}")
        
        # Get updated like count
        print("📊 God's Plan - Getting updated like count...")
        after = make_request(encrypted_uid, server_name, token)
        if after is None:
            return jsonify({
                "error": "Failed to get updated profile information in God's Plan",
                "credits": {
                    "Developer": "👑 God",
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 500
            
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
            "LikesGivenByAPI": like_given,
            "LikesafterCommand": after_like,
            "LikesbeforeCommand": before_like,
            "PlayerNickname": name,
            "UID": player_id,
            "Level": level,
            "Experience": exp,
            "Avatar": avatar,
            "RequestedLikes": like_count,
            "status": status,
            "message": "God's Plan Executed Successfully! 🙏",
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_",
                "project": "God is very cruel"
            }
        }
        
        print("🎉 God's Plan - Request completed successfully!")
        print("🌟 God's Plan has been executed perfectly!")
        print("📱 Instagram: _echo.del.alma_")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"💥 Error in God's Plan: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "God's Plan encountered an internal error",
            "message": str(e),
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_",
                "message": "Even God's Plan has challenges sometimes 🙏"
            }
        }), 500

# ==================== GOD'S PLAN - DEBUG ROUTES ====================

@app.route('/debug-tokens/<server_name>')
def debug_tokens(server_name):
    """God's Plan - Token Debug Route 🙏"""
    try:
        print(f"🔍 God's Plan - Debug tokens for server: {server_name}")
        
        data = load_tokens(server_name.upper())
        if not data:
            return jsonify({
                "error": "No tokens found in God's Plan",
                "credits": {
                    "Developer": "👑 God", 
                    "Instagram": "📱 _echo.del.alma_"
                }
            }), 500
            
        token_info = {
            "total_tokens": len(data),
            "server": server_name,
            "tokens_preview": [{"token": token_data["token"][:20] + "..."} for token_data in data],
            "message": "God's Plan Token Debug"
        }
        
        return jsonify({
            "debug_info": token_info,
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_",
                "project": "God's Plan - Token Debug"
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Token debug failed: {str(e)}",
            "credits": {
                "Developer": "👑 God",
                "Instagram": "📱 _echo.del.alma_"
            }
        }), 500

# ==================== GOD'S PLAN - VERCEL HANDLER ====================
app = app

if __name__ == '__main__':
    print("🌟 Starting God's Plan API Server...")
    print("🙏 Developed by  God | Instagram: _echo.del.alma_")
    print("🚀 God's Plan is now running!")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
