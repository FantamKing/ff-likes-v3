import json
import time
from datetime import datetime, timedelta
import os

class DailyLikeTracker:
    def __init__(self, filename="daily_likes.json"):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_data(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    def get_reset_time(self):
        """Get next reset time (4:00 AM IST)"""
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # UTC to IST
        today_4am = now.replace(hour=4, minute=0, second=0, microsecond=0)
        
        if now >= today_4am:
            next_reset = today_4am + timedelta(days=1)
        else:
            next_reset = today_4am
        
        return next_reset.strftime("%H:%M %p IST"), next_reset
    
    def can_send_likes(self, uid, requested_likes):
        """Check if we can send requested likes to this UID today"""
        uid = str(uid)
        current_time = time.time()
        reset_time_str, next_reset = self.get_reset_time()
        
        # Clean old data (older than 24 hours)
        self.clean_old_data()
        
        if uid not in self.data:
            self.data[uid] = {"likes_sent": 0, "last_updated": current_time}
            self.save_data()
        
        used_today = self.data[uid]["likes_sent"]
        remaining = max(0, 100 - used_today)
        
        can_send = min(requested_likes, remaining)
        return can_send, used_today, remaining, reset_time_str
    
    def update_likes_sent(self, uid, likes_sent):
        """Update the like count for a UID"""
        uid = str(uid)
        if uid in self.data:
            self.data[uid]["likes_sent"] += likes_sent
            self.data[uid]["last_updated"] = time.time()
            self.save_data()
    
    def clean_old_data(self):
        """Remove data older than 24 hours"""
        current_time = time.time()
        uids_to_remove = []
        
        for uid, info in self.data.items():
            if current_time - info["last_updated"] > 24 * 3600:  # 24 hours
                uids_to_remove.append(uid)
        
        for uid in uids_to_remove:
            del self.data[uid]
        
        if uids_to_remove:
            self.save_data()

# Global tracker instance
tracker = DailyLikeTracker()
