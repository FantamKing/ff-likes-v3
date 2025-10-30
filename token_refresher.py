# token_refresher.py
import os
import json
import asyncio
import hashlib
import time
import hmac
import base64
from datetime import datetime
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeFireTokenRefresher:
    def __init__(self):
        self.mongodb_uri = os.environ.get("MONGODB_URI")
        self.client = None
        self.db = None
        if self.mongodb_uri:
            self._connect_db()
    
    def _connect_db(self):
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client.ff_tokens
            logger.info("✅ MongoDB connected for token refresh")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
    
    def load_accounts(self):
        """Load all accounts from accounts.json"""
        try:
            with open('accounts.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading accounts.json: {e}")
            return {}
    
    def generate_jwt_token(self, account, server):
        """
        Generate JWT token for Free Fire account
        """
        try:
            # JWT Header
            header = {
                "alg": "HS256",
                "typ": "JWT",
                "region": server.upper()
            }
            
            # JWT Payload
            current_time = int(time.time())
            payload = {
                "uid": int(account['uid']),
                "account_id": account.get('account_id', 1),
                "name": account.get('name', 'Guest'),
                "region": server.upper(),
                "iat": current_time,
                "exp": current_time + (23 * 60 * 60),  # 23 hours expiry
                "iss": "freefire",
                "device_id": self._generate_device_id()
            }
            
            # Encode header and payload
            header_encoded = base64.urlsafe_b64encode(
                json.dumps(header).encode()
            ).decode().rstrip('=')
            
            payload_encoded = base64.urlsafe_b64encode(
                json.dumps(payload).encode()
            ).decode().rstrip('=')
            
            # Create signature using password as secret
            message = f"{header_encoded}.{payload_encoded}"
            signature = hmac.new(
                account['password'].encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
            
            # Combine to create JWT
            jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
            
            logger.info(f"✅ Generated JWT token for {account.get('name')}")
            
            return {
                'token': jwt_token,
                'uid': account['uid'],
                'name': account.get('name', 'Unknown'),
                'server': server.upper(),
                'generated_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"❌ JWT generation failed for {account.get('name')}: {e}")
            return None
    
    def _generate_device_id(self):
        """Generate unique device ID"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:16].upper()
    
    async def convert_accounts_to_tokens(self):
        """
        Main function: Convert all accounts to JWT tokens and update token files
        """
        try:
            accounts_data = self.load_accounts()
            if not accounts_data:
                logger.error("❌ No accounts found in accounts.json")
                return False
            
            logger.info("🔄 Starting automatic token conversion...")
            
            total_tokens_generated = 0
            
            # Process each server
            for server, accounts in accounts_data.items():
                if not accounts:
                    logger.warning(f"⚠️ No accounts found for {server}")
                    continue
                
                logger.info(f"🔄 Processing {len(accounts)} accounts for {server.upper()}")
                
                # Generate tokens for all accounts in this server
                tokens = []
                for account in accounts:
                    token_data = self.generate_jwt_token(account, server)
                    if token_data:
                        tokens.append(token_data)
                        logger.info(f"✅ Generated token for {account.get('name')} ({server.upper()})")
                        total_tokens_generated += 1
                    else:
                        logger.error(f"❌ Failed to generate token for {account.get('name')}")
                
                # Update token file for this server
                if tokens:
                    success = self._update_token_file(server, tokens)
                    if success:
                        self._store_in_mongodb(server, tokens)
                        logger.info(f"🎯 Updated token_{server}.json with {len(tokens)} tokens")
                    else:
                        logger.error(f"❌ Failed to update token file for {server}")
                else:
                    logger.error(f"❌ No tokens generated for {server.upper()}")
            
            logger.info(f"✅ All accounts converted! Total tokens: {total_tokens_generated}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error in convert_accounts_to_tokens: {e}")
            return False
    
    def _update_token_file(self, server, tokens):
        """Overwrite token file for specific server"""
        try:
            filename = f"token_{server.lower()}.json"
            
            # Keep only token field for compatibility with your main app
            simplified_tokens = [{'token': token_data['token']} for token_data in tokens]
            
            with open(filename, 'w') as f:
                json.dump(simplified_tokens, f, indent=2)
            
            logger.info(f"📁 Overwritten {filename} with {len(tokens)} tokens")
            return True
        except Exception as e:
            logger.error(f"❌ Error updating {filename}: {e}")
            return False
    
    def _store_in_mongodb(self, server, tokens):
        """Store tokens in MongoDB for backup"""
        if not self.db:
            logger.info("ℹ️ MongoDB not available, skipping backup")
            return
        
        try:
            collection = self.db.tokens
            document = {
                "server_name": server.upper(),
                "tokens": tokens,
                "last_updated": datetime.utcnow(),
                "total_accounts": len(tokens)
            }
            
            collection.update_one(
                {"server_name": server.upper()},
                {"$set": document},
                upsert=True
            )
            logger.info(f"💾 Backed up {len(tokens)} tokens to MongoDB for {server.upper()}")
        except Exception as e:
            logger.error(f"❌ MongoDB storage error: {e}")
    
    def get_token_stats(self):
        """Get statistics about current tokens"""
        stats = {}
        servers = ['ind', 'br', 'bd']
        
        for server in servers:
            filename = f"token_{server}.json"
            try:
                with open(filename, 'r') as f:
                    tokens = json.load(f)
                    stats[server] = {
                        'token_count': len(tokens),
                        'file_exists': True,
                        'sample_token': tokens[0]['token'][:50] + '...' if tokens else 'No tokens'
                    }
            except FileNotFoundError:
                stats[server] = {
                    'token_count': 0,
                    'file_exists': False
                }
            except Exception as e:
                stats[server] = {
                    'token_count': 0,
                    'file_exists': False,
                    'error': str(e)
                }
        
        return stats
