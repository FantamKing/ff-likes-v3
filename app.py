# Credit:- "insta :-_echo.del.alma_"
# Developed by God

from pymongo import MongoClient
import os
import sys
import traceback
import time
import hashlib
import hmac
import base64
from urllib.parse import urlparse

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

# ==================== MONGODB TOKEN MANAGER ====================

class MongoDBTokenManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            connection_string = os.environ.get('MONGODB_URI')
            if not connection_string:
                print("❌ MONGODB_URI not found in environment variables")
                return False
            
            print(f"🔗 Connecting to MongoDB...")
            
            # Add timeout and better error handling
            self.client = MongoClient(
                connection_string, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test the connection with a simple command
            self.client.admin.command('ping')
            
            # Use the default database from connection string
            self.db = self.client.get_database()
            print(f"✅ Connected to MongoDB Atlas - Database: {self.db.name}")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            return False
    
    def store_tokens(self, server_name, tokens):
        """Store tokens for a server"""
        try:
            # Ensure we have a valid connection
            if not self.db:
                print("🔄 No active MongoDB connection, reconnecting...")
                if not self.connect():
                    print("❌ Reconnection failed")
                    return False
            
            result = self.db.tokens.update_one(
                {"server": server_name},
                {
                    "$set": {
                        "tokens": tokens,
                        "last_updated": time.time(),
                        "expires_at": time.time() + (4 * 3600)
                    }
                },
                upsert=True
            )
            
            if result.acknowledged:
                print(f"✅ Successfully stored {len(tokens)} tokens for {server_name}")
                return True
            else:
                print(f"❌ Token storage failed for {server_name}")
                return False
                
        except Exception as e:
            print(f"💥 Token storage error: {e}")
            return False
    
    def get_tokens(self, server_name):
        """Get tokens for a server"""
        try:
            data = self.db.tokens.find_one({"server": server_name})
            if data and data.get('tokens'):
                # Check if tokens are expired
                if time.time() > data.get('expires_at', 0):
                    print(f"🔄 Tokens for {server_name} expired, need refresh")
                    return None
                return data['tokens']
            return None
        except Exception as e:
            print(f"Token retrieval error: {e}")
            return None
    
    def should_refresh_tokens(self, server_name):
        """Check if tokens need refresh"""
        try:
            data = self.db.tokens.find_one({"server": server_name})
            if not data:
                return True
            return time.time() > data.get('expires_at', 0)
        except Exception as e:
            print(f"Token check error: {e}")
            return True
    
    def generate_jwt_token(self, uid, password, account_id, name, region):
        """Generate JWT token (same as before)"""
        try:
            header = {
                "alg": "HS256",
                "typ": "JWT"
            }
            
            current_time = int(time.time())
            payload = {
                "uid": int(uid),
                "account_id": int(account_id),
                "name": name,
                "region": region,
                "iat": current_time,
                "exp": current_time + (24 * 60 * 60),
                "iss": "freefire",
                "aud": "freefire-client"
            }
            
            header_encoded = base64.urlsafe_b64encode(
                json.dumps(header).encode()
            ).decode().rstrip('=')
            
            payload_encoded = base64.urlsafe_b64encode(
                json.dumps(payload).encode()
            ).decode().rstrip('=')
            
            message = f"{header_encoded}.{payload_encoded}"
            signature = hmac.new(
                password.encode() if isinstance(password, str) else password,
                message.encode(),
                hashlib.sha256
            ).digest()
            
            signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
            
            jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
            return jwt_token
            
        except Exception as e:
            print(f"JWT generation error: {e}")
            return None
    
    def refresh_tokens(self, server_name):
        """Refresh tokens for a server"""
        try:
            # Load accounts from environment variable or file
            accounts_json = os.environ.get('ACCOUNTS_JSON')
            if accounts_json:
                accounts = json.loads(accounts_json)
            else:
                with open("accounts.json", "r") as f:
                    accounts = json.load(f)
            
            tokens = []
            
            for account in accounts:
                uid = account.get("uid")
                password = account.get("password")
                account_id = account.get("account_id", 1)
                name = account.get("name", "Guest")
                region = account.get("region", "IND").upper()
                
                if region != server_name:
                    continue
                
                if not uid or not password:
                    continue
                
                token = self.generate_jwt_token(uid, password, account_id, name, region)
                if token:
                    tokens.append({"token": token})
                    print(f"✅ Generated token for {name}")
            
            if tokens:
                self.store_tokens(server_name, tokens)
                print(f"🔄 Stored {len(tokens)} tokens for {server_name} in MongoDB")
                return tokens
            else:
                print(f"❌ No tokens generated for {server_name}")
                return None
                
        except Exception as e:
            print(f"Token refresh error: {e}")
            return None

# Initialize MongoDB manager
mongo_manager = MongoDBTokenManager()

# ==================== MAIN FUNCTIONALITY ====================

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
    """Load tokens from MongoDB with auto-refresh"""
    try:
        # Check if tokens need refresh
        if mongo_manager.should_refresh_tokens(server_name):
            print(f"🔄 Refreshing tokens for {server_name}...")
            tokens = mongo_manager.refresh_tokens(server_name)
            if tokens:
                return tokens
            else:
                print(f"⚠️ Token refresh failed for {server_name}")
        
        # Get tokens from MongoDB
        tokens = mongo_manager.get_tokens(server_name)
        if tokens:
            return tokens
        else:
            print(f"❌ No tokens found for {server_name} in MongoDB")
            return [{"token": "default_token"}]
            
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

@app.route('/test-connection')
def test_connection():
    """Test MongoDB connection with detailed info"""
    try:
        # Reconnect if needed
        if not mongo_manager.client:
            mongo_manager.connect()
        
        if mongo_manager.client and mongo_manager.db:
            # Test with a simple command
            mongo_manager.client.admin.command('ping')
            
            # Try to list collections to verify database access
            collections = mongo_manager.db.list_collection_names()
            
            return jsonify({
                "status": "connected",
                "database": mongo_manager.db.name,
                "collections": collections,
                "collections_count": len(collections),
                "message": "MongoDB connection successful"
            })
        else:
            return jsonify({
                "status": "failed",
                "error": "MongoDB client or database not initialized",
                "check": "Check MongoDB connection in MongoDBTokenManager"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "MongoDB connection failed"
        })
        

@app.route('/view-mongodb-tokens')
def view_mongodb_tokens():
    """View actual tokens stored in MongoDB"""
    try:
        tokens_data = mongo_manager.db.tokens.find_one({"server": "IND"})
        
        if tokens_data:
            tokens = tokens_data.get('tokens', [])
            return jsonify({
                "tokens_in_mongodb": tokens,
                "total_tokens": len(tokens),
                "last_updated": time.ctime(tokens_data.get('last_updated', 0)),
                "expires_at": time.ctime(tokens_data.get('expires_at', 0))
            })
        else:
            return jsonify({"error": "No tokens found in MongoDB for IND server"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/test-mongodb')
def test_mongodb():
    """Test MongoDB connection with error details"""
    try:
        # Test connection
        mongo_manager.db.command('ping')
        return jsonify({"status": "connected", "message": "MongoDB authentication successful"})
    except Exception as e:
        return jsonify({
            "error": "MongoDB connection failed",
            "details": str(e),
            "check": "Verify MONGODB_URI environment variable has correct username/password"
        })

@app.route('/debug-token-storage')
def debug_token_storage():
    """Debug why tokens aren't being stored"""
    try:
        # Test token generation
        tokens = mongo_manager.refresh_tokens("IND")
        
        if tokens:
            # Test storage
            storage_success = mongo_manager.store_tokens("IND", tokens)
            
            # Verify storage
            stored_tokens = mongo_manager.get_tokens("IND")
            
            return jsonify({
                "tokens_generated": len(tokens),
                "storage_success": storage_success,
                "tokens_after_storage": len(stored_tokens) if stored_tokens else 0,
                "stored_tokens_preview": stored_tokens[:2] if stored_tokens else "None"
            })
        else:
            return jsonify({"error": "No tokens generated"})
            
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()})

@app.route('/debug-mongodb-write')
def debug_mongodb_write():
    """Debug MongoDB write operations"""
    try:
        # Test basic connection
        mongo_manager.db.command('ping')
        
        # Test collection access
        collection = mongo_manager.db.tokens
        
        # Test insert
        test_data = {
            "server": "TEST",
            "tokens": [{"token": "test_token"}],
            "last_updated": time.time(),
            "expires_at": time.time() + 3600
        }
        
        insert_result = collection.insert_one(test_data)
        insert_success = insert_result.acknowledged
        
        # Test find
        found_data = collection.find_one({"server": "TEST"})
        find_success = bool(found_data)
        
        # Test update
        update_result = collection.update_one(
            {"server": "TEST"}, 
            {"$set": {"tokens": [{"token": "updated_token"}]}}
        )
        update_success = update_result.acknowledged
        
        # Cleanup
        delete_result = collection.delete_one({"server": "TEST"})
        
        return jsonify({
            "ping_success": True,
            "insert_success": insert_success,
            "find_success": find_success,
            "update_success": update_success,
            "inserted_id": str(insert_result.inserted_id) if insert_success else "None",
            "found_data": str(found_data) if found_data else "None",
            "database": mongo_manager.db.name,
            "collection": "tokens"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        })

@app.route('/mongodb-status')
def mongodb_status():
    """Check MongoDB connection and token status"""
    status = {}
    
    for server in ["IND", "BR", "BD"]:
        tokens = mongo_manager.get_tokens(server)
        needs_refresh = mongo_manager.should_refresh_tokens(server)
        
        status[server] = {
            "connected": mongo_manager.client is not None,
            "tokens_available": len(tokens) if tokens else 0,
            "needs_refresh": needs_refresh,
            "has_tokens": bool(tokens)
        }
    
    return jsonify({
        "mongodb_status": status,
        "connection": "active" if mongo_manager.client else "failed"
    })

@app.route('/refresh-mongodb-tokens/<server_name>')
def refresh_mongodb_tokens(server_name):
    """Manually refresh tokens in MongoDB"""
    server_name = server_name.upper()
    tokens = mongo_manager.refresh_tokens(server_name)
    
    return jsonify({
        "server": server_name,
        "status": "success" if tokens else "failed",
        "tokens_generated": len(tokens) if tokens else 0,
        "message": f"Tokens refreshed in MongoDB for {server_name}" if tokens else f"Failed to refresh tokens for {server_name}"
    })

# ======================================================================================================================================================================================



@app.route('/test-manager')
def test_manager():
    """Test if MongoDBTokenManager is working"""
    try:
        # Test if manager connected
        if mongo_manager.client:
            mongo_manager.client.admin.command('ping')
            return jsonify({
                "manager_status": "connected",
                "database": mongo_manager.db.name if mongo_manager.db else "None",
                "client_initialized": mongo_manager.client is not None,
                "db_initialized": mongo_manager.db is not None
            })
        else:
            # Try to reconnect
            connected = mongo_manager.connect()
            return jsonify({
                "manager_status": "reconnected" if connected else "failed",
                "reconnect_success": connected,
                "client_initialized": mongo_manager.client is not None,
                "db_initialized": mongo_manager.db is not None
            })
    except Exception as e:
        return jsonify({
            "manager_status": "error",
            "error": str(e)
        })







@app.route('/debug-env')
def debug_env():
    """Check if environment variables are loaded"""
    mongodb_uri = os.environ.get('MONGODB_URI')
    
    return jsonify({
        "MONGODB_URI_exists": bool(mongodb_uri),
        "MONGODB_URI_preview": mongodb_uri[:20] + "..." if mongodb_uri else "Not found",
        "all_env_vars": list(os.environ.keys())
    })



@app.route('/debug-mongodb-error')
def debug_mongodb_error():
    """Get detailed MongoDB connection error"""
    try:
        connection_string = os.environ.get('MONGODB_URI')
        
        # Test connection with detailed error
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        return jsonify({"status": "connected", "message": "MongoDB working!"})
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "connection_string_preview": connection_string[:50] + "..." if connection_string else "None"
        })


# ========================================================================================================================================================================================

@app.route('/debug-databases')
def debug_databases():
    """See what databases are available"""
    try:
        if mongo_manager.client:
            databases = mongo_manager.client.list_database_names()
            return jsonify({
                "available_databases": databases,
                "current_database": mongo_manager.db.name if mongo_manager.db else "None"
            })
        else:
            return jsonify({"error": "No MongoDB connection"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def home():
    return jsonify({
        "message": "God is Opening his gate!",
        "status": "opening...",
        "Yoo! just add & edit this after the page's url": "/like?uid=UID&server_name=SERVER&like_count=how much like want",
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
                return jsonify({"error": "Hey greedy...!   like_count must be between 1 and 100"}), 400
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
        print("📊 Getting initial like count...")
        before = make_request(encrypted_uid, server_name, token)
        if before is None:
            return jsonify({"error": "God is not in a mood right now, gate is closing...."}), 500
            
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
            "Likes before Wish": before_like,
            "God give you ": like_given,
            "Likes after Wish": after_like,
            "PlayerNickname": name,
            "UID": player_id,
            "Level": level,
            "Experience": exp,
            "Avatar": avatar,
            "RequestedLikes": like_count,
            "status": status,
            "credits": {
                "Developer": "God",
                "Instagram": "_echo.del.alma_"
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
                "Developer": "God",
                "Instagram": "_echo.del.alma_"
            }
        }), 500

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
        
        print(f"🔍 DEBUG: Sending request to {url}")
        print(f"🔍 DEBUG: Headers: {headers}")
        print(f"🔍 DEBUG: Encrypted UID length: {len(encrypted_uid)}")
        
        response = requests.post(url, data=edata, headers=headers, verify=True, timeout=30)
        
        debug_info = {
            "url": url,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body_preview": response.text[:500] if response.text else "Empty response",
            "response_hex": response.content.hex()[:100] + "..." if response.content else "No content"
        }
        
        print(f"🔍 DEBUG: Response Status: {response.status_code}")
        print(f"🔍 DEBUG: Response Headers: {dict(response.headers)}")
        print(f"🔍 DEBUG: Response Body Preview: {response.text[:200]}")
        
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
