# Credit:- "insta :-_echo.del.alma_"
# Token Generator for Free Fire Likes API

import json
import time
import hashlib
import hmac
import base64
import os
from flask import Flask, jsonify

# Create separate Flask app for token generator
token_app = Flask(__name__)

def generate_jwt_token(uid, password, account_id, name, region):
    """Generate JWT token for Free Fire authentication"""
    try:
        # JWT Header
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        # JWT Payload
        current_time = int(time.time())
        payload = {
            "uid": int(uid),
            "account_id": int(account_id),
            "name": name,
            "region": region,
            "iat": current_time,
            "exp": current_time + (24 * 60 * 60),  # 24 hours expiry
            "iss": "freefire",
            "aud": "freefire-client"
        }
        
        # Encode header and payload
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            password.encode() if isinstance(password, str) else password,
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine to create JWT
        jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
        return jwt_token
        
    except Exception as e:
        print(f"JWT generation error: {e}")
        return None

def load_accounts_from_file(filename="accounts.json"):
    """Load account details from accounts.json file"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading accounts: {e}")
        return []

def generate_tokens_for_all_accounts():
    """Generate fresh tokens for all accounts and update token files"""
    try:
        accounts = load_accounts_from_file()
        if not accounts:
            return {"error": "No accounts found in accounts.json"}
        
        tokens_by_region = {
            "IND": [],
            "BR": [],
            "BD": []
        }
        
        successful_tokens = 0
        
        for account in accounts:
            uid = account.get("uid")
            password = account.get("password")
            account_id = account.get("account_id", 1)
            name = account.get("name", "Guest")
            region = account.get("region", "IND").upper()
            
            if not uid or not password:
                print(f"⚠️ Skipping account - missing UID or password: {account}")
                continue
            
            # Generate JWT token
            token = generate_jwt_token(uid, password, account_id, name, region)
            
            if token:
                token_data = {
                    "token": token,
                    "uid": uid,
                    "name": name,
                    "generated_at": time.time(),
                    "region": region
                }
                
                # Add to appropriate region
                if region in tokens_by_region:
                    tokens_by_region[region].append(token_data)
                else:
                    tokens_by_region["IND"].append(token_data)  # Default to IND
                
                successful_tokens += 1
                print(f"✅ Generated token for {name} ({region})")
            else:
                print(f"❌ Failed to generate token for {name}")
        
        # Update token files
        for region, tokens in tokens_by_region.items():
            if tokens:
                filename = f"token_{region.lower()}.json"
                with open(filename, "w") as f:
                    # Save only token strings for main API
                    token_strings = [{"token": token_data["token"]} for token_data in tokens]
                    json.dump(token_strings, f, indent=2)
                print(f"📁 Updated {filename} with {len(tokens)} tokens")
        
        return {
            "status": "success",
            "message": f"Generated {successful_tokens} tokens successfully",
            "tokens_generated": successful_tokens,
            "details": {region: len(tokens) for region, tokens in tokens_by_region.items()}
        }
        
    except Exception as e:
        print(f"Token generation error: {e}")
        return {"error": str(e)}

def are_tokens_expired():
    """Check if tokens need refresh (older than 12 hours)"""
    try:
        for region in ["IND", "BR", "BD"]:
            filename = f"token_{region.lower()}.json"
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    tokens = json.load(f)
                    if tokens and len(tokens) > 0:
                        # Check if file was modified more than 12 hours ago
                        file_mtime = os.path.getmtime(filename)
                        if time.time() - file_mtime > (12 * 60 * 60):  # 12 hours
                            return True
        return False
    except:
        return True

# ==================== TOKEN GENERATOR ROUTES ====================

@token_app.route('/')
def token_generator_home():
    return jsonify({
        "message": "Free Fire Token Generator",
        "status": "active",
        "endpoints": {
            "refresh_tokens": "/refresh-tokens",
            "check_tokens": "/check-tokens",
            "auto_refresh": "/auto-refresh"
        },
        "credits": {
            "Developer": "👑 God",
            "Instagram": "📱 _echo.del.alma_"
        }
    })

@token_app.route('/refresh-tokens', methods=['GET'])
def refresh_tokens():
    """Manually refresh all tokens"""
    result = generate_tokens_for_all_accounts()
    return jsonify({
        "token_refresh": result,
        "credits": {
            "Developer": "👑 God", 
            "Instagram": "📱 _echo.del.alma_"
        }
    })

@token_app.route('/check-tokens', methods=['GET'])
def check_tokens():
    """Check token status and expiry"""
    token_status = {}
    
    for region in ["IND", "BR", "BD"]:
        filename = f"token_{region.lower()}.json"
        if os.path.exists(filename):
            file_mtime = os.path.getmtime(filename)
            age_hours = (time.time() - file_mtime) / 3600
            
            with open(filename, "r") as f:
                tokens = json.load(f)
            
            token_status[region] = {
                "token_count": len(tokens),
                "last_updated": time.ctime(file_mtime),
                "age_hours": round(age_hours, 2),
                "expired": age_hours > 12
            }
        else:
            token_status[region] = {
                "token_count": 0,
                "status": "file_not_found"
            }
    
    return jsonify({
        "token_status": token_status,
        "credits": {
            "Developer": "👑 God",
            "Instagram": "📱 _echo.del.alma_"
        }
    })

@token_app.route('/auto-refresh', methods=['GET'])
def auto_refresh():
    """Auto-refresh tokens if expired"""
    if are_tokens_expired():
        print("🔄 Tokens expired, auto-refreshing...")
        result = generate_tokens_for_all_accounts()
        return jsonify({
            "auto_refresh": "tokens_refreshed",
            "details": result
        })
    else:
        return jsonify({
            "auto_refresh": "tokens_fresh",
            "message": "Tokens are still valid (less than 12 hours old)"
        })

# For Vercel
def handler(request, context):
    return token_app(request, context)

if __name__ == '__main__':
    token_app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
