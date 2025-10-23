# Credit:- "insta :-echo.del.alma"

from flask import Flask, request, jsonify
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import aiohttp
from google.protobuf.json_format import MessageToDict
import requests
import json
import like_pb2
import like_count_pb2
import uid_generator_pb2

app = Flask(_name_)

def load_tokens(server_name):
    try:
        if server_name == "IND":
            with open("token_ind.json", "r") as f:
                tokens = json.load(f)
        elif server_name in {"BR", "US", "SAC", "NA"}:
            with open("token_br.json", "r") as f:
                tokens = json.load(f)
        else:
            with open("token_bd.json", "r") as f:
                tokens = json.load(f)
        
        if not tokens:
            raise ValueError(f"No tokens found for server: {server_name}")
        return tokens
    except FileNotFoundError:
        raise FileNotFoundError(f"Token file not found for server: {server_name}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in token file for server: {server_name}")

def encrypt_message(plaintext):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%' 
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return binascii.hexlify(encrypted_message).decode('utf-8')
    
def create_protobuf_message(user_id, region):
    message = like_pb2.like()
    message.uid = int(user_id)
    message.region = region
    return message.SerializeToString()

def get_server_url(server_name, endpoint_type="like"):
    """Centralized function to get server URLs"""
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
    else:  # info endpoint
        return base_url + "GetPlayerPersonalShow"

async def send_request(encrypted_uid, token, url):
    edata = bytes.fromhex(encrypted_uid)
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB49"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"Request failed with status code: {response.status}")
                return response.status
    except asyncio.TimeoutError:
        print("Request timeout")
        return 408
    except Exception as e:
        print(f"Request error: {e}")
        return 500

async def send_multiple_requests(uid, server_name, like_count):
    region = server_name
    protobuf_message = create_protobuf_message(uid, region)
    encrypted_uid = encrypt_message(protobuf_message)
    
    url = get_server_url(server_name, "like")
    tokens = load_tokens(server_name)
    
    # Validate like_count range
    like_count = max(1, min(100, like_count))
    
    tasks = []
    for i in range(like_count):
        token = tokens[i % len(tokens)]["token"]
        tasks.append(send_request(encrypted_uid, token, url))
    
    results = await asyncio.gather(*tasks)
    return results

def create_protobuf(uid):
    message = uid_generator_pb2.uid_generator()
    message.krishna_ = int(uid)
    message.teamXdarks = 1
    return message.SerializeToString()

def enc(uid):
    protobuf_data = create_protobuf(uid)
    encrypted_uid = encrypt_message(protobuf_data)
    return encrypted_uid

def make_request(encrypt, server_name, token):
    url = get_server_url(server_name, "info")

    edata = bytes.fromhex(encrypt)

    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB49"
    }

    try:
        response = requests.post(url, data=edata, headers=headers, verify=True, timeout=30)
        response.raise_for_status()
        
        hex_data = response.content.hex()
        binary = bytes.fromhex(hex_data)
        decode = decode_protobuf(binary)
        return decode
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except Exception as e:
        print(f"Error decoding Protobuf data: {e}")
        return None

@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    like_count = request.args.get("like_count", "100")
    
    # Input validation
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400
    
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

    def process_request():
        try:
            data = load_tokens(server_name)
            if not data:
                return {"error": "No tokens available for this server"}
                
            token = data[0]['token']
            encrypt = enc(uid)
            
            # Get initial like count
            before = make_request(encrypt, server_name, token)
            if before is None:
                return {"error": "Failed to get initial profile information"}
                
            jsone = MessageToJson(before)
            data_json = json.loads(jsone)
            before_like = data_json['AccountInfo'].get('Likes', 0)
            if before_like is None:
                before_like = 0
            else:
                before_like = int(before_like)
            
            print(f"Initial likes: {before_like}")
            
            # Send the specified number of likes
            asyncio.run(send_multiple_requests(uid, server_name, like_count))
            
            # Get updated like count
            after = make_request(encrypt, server_name, token)
            if after is None:
                return {"error": "Failed to get updated profile information"}
                
            jsone = MessageToJson(after)
            data_json = json.loads(jsone)
            after_like = int(data_json['AccountInfo']['Likes'])
            player_id = int(data_json['AccountInfo']['UID'])
            name = str(data_json['AccountInfo']['PlayerNickname'])
            
            like_given = after_like - before_like
            
            if like_given > 0:
                status = 1  # Success
            else:
                status = 2  # No likes added
                
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
            return result
            
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}

    result = process_request()
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)

if _name_ == '_main_':
    app.run(debug=True, use_reloader=False)
# Credit:- "insta :-echo.del.alma"
