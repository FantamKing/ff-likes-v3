# Credit:- "insta :-echo.del.alma"

from flask import Flask, request, jsonify
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import aiohttp
import requests
import json
import os

app = Flask(_name_)

# Try to import protobuf files with error handling
try:
    import like_pb2
    import like_count_pb2
    import uid_generator_pb2
except ImportError as e:
    print(f"Protobuf import error: {e}")
    # Create dummy classes to prevent crashes
    class DummyProto:
        def _init_(self): pass
        def ParseFromString(self, x): pass
    like_pb2 = type('like_pb2', (), {'like': DummyProto})
    like_count_pb2 = type('like_count_pb2', (), {'Info': DummyProto})
    uid_generator_pb2 = type('uid_generator_pb2', (), {'uid_generator': DummyProto})

def get_headers(token):
    return {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; SM-G991B Build/TP1A.220624.014)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2022.3.21f1",
        'X-GA': "v2 1",
        'ReleaseVersion': "OB50"
    }

def load_tokens(server_name):
    try:
        # For Vercel, files should be in the same directory
        token_files = {
            "IND": "token_ind.json",
            "BR": "token_br.json", 
            "US": "token_br.json",
            "SAC": "token_br.json",
            "NA": "token_br.json"
        }
        
        filename = token_files.get(server_name, "token_bd.json")
        
        # Check if file exists
        if not os.path.exists(filename):
            return [{"token": "default_token"}]
            
        with open(filename, "r") as f:
            tokens = json.load(f)
        
        if not tokens:
            return [{"token": "default_token"}]
        return tokens
        
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
    
    if endpoint_type == "like":
        return base_url + "LikeProfile"
    else:
        return base_url + "GetPlayerPersonalShow"

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
        
        if not encrypted_uid:
            return []
            
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
        response.raise_for_status()
        
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

@app.route('/')
def home():
    return jsonify({
        "message": "Free Fire Likes API is running",
        "usage": "/like?uid=USER_ID&server_name=SERVER&like_count=COUNT",
        "servers": ["IND", "BR", "US", "SAC", "NA", "BD"],
        "credits": {
            "Developer": "God",
            "Instagram": "echo.del.alma"
        }
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    try:
        # Support both 'uid' and 'user_id' parameters
        uid = request.args.get("uid") or request.args.get("user_id")
        server_name = request.args.get("server_name", "").upper()
        like_count = request.args.get("like_count", "100")
        
        # Input validation
        if not uid or not server_name:
            return jsonify({
                "error": "UID and server_name are required",
                "example": "/like?uid=123456&server_name=IND&like_count=50"
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
        data = load_tokens(server_name)
        if not data:
            return jsonify({"error": "No tokens available for this server"}), 500
            
        token = data[0]['token']
        encrypted_uid = enc(uid)
        
        if not encrypted_uid:
            return jsonify({"error": "Encryption failed"}), 500

        # Get initial like count
        before = make_request(encrypted_uid, server_name, token)
        if before is None:
            return jsonify({"error": "Failed to get initial profile information"}), 500
            
        before_json = json.loads(MessageToJson(before))
        before_like = before_json.get('AccountInfo', {}).get('Likes', 0)
        before_like = int(before_like) if before_like else 0
        
        # Send likes
        results = asyncio.run(send_multiple_requests(uid, server_name, like_count))
        
        # Get updated like count
        after = make_request(encrypted_uid, server_name, token)
        if after is None:
            return jsonify({"error": "Failed to get updated profile information"}), 500
            
        after_json = json.loads(MessageToJson(after))
        after_like = int(after_json['AccountInfo']['Likes'])
        player_id = int(after_json['AccountInfo']['UID'])
        name = str(after_json['AccountInfo']['PlayerNickname'])
        
        like_given = after_like - before_like
        status = 1 if like_given > 0 else 2
        
        result = {
            "LikesGivenByAPI": like_given,
            "LikesafterCommand": after_like,
            "LikesbeforeCommand": before_like,
            "PlayerNickname": name,
            "UID": player_id,
            "RequestedLikes": like_count,
            "status": status,
            "credits": {
                "Developer": "God",
                "Instagram": "echo.del.alma"
            }
        }
        return jsonify(result)
        
    except Exception as e:
        print(f"Main handler error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if _name_ == '_main_':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
