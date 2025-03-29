import pymongo
import logging
from datetime import datetime
from config import DB_URI, DB_NAME, settings, FSUBS

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize MongoDB connection
try:
    dbclient = pymongo.MongoClient(DB_URI)
    database = dbclient[DB_NAME]
    logger.info("✅ Database connection established")
except Exception as e:
    logger.critical(f"❌ Database connection failed: {e}")
    raise SystemExit

# Collections
users_collection = database['users']
banned_users_collection = database['banned_users']
settings_collection = database['settings']
channels_collection = database['channels']
requests_collection = database['join_requests']

# Create indexes
try:
    requests_collection.create_index(
        [("user_id", 1), ("channel_id", 1)], 
        unique=True,
        name="user_channel_idx"
    )
    channels_collection.create_index("_id", unique=True)
    logger.info("✅ Database indexes created")
except Exception as e:
    logger.error(f"❌ Index creation failed: {e}")

def initialize_defaults():
    """Initialize default configurations"""
    try:
        # Settings
        if not settings_collection.find_one({"_id": 1}):
            settings_collection.insert_one({
                "_id": 1,
                **settings,
                "created_at": datetime.now()
            })
            logger.info("✅ Default settings initialized")
        
        # Force subscriptions
        if channels_collection.count_documents({}) == 0 and FSUBS:
            channels_collection.insert_many([{
                **channel,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            } for channel in FSUBS])
            logger.info("✅ Default channels loaded")
            
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")

# Channel Management
def add_channel(channel_id, name, is_private=False, auto_approve=False, request_channel=None):
    """Add/update a force subscription channel"""
    try:
        result = channels_collection.update_one(
            {"_id": channel_id},
            {"$set": {
                "name": name,
                "is_private": is_private,
                "auto_approve": auto_approve,
                "request_channel": request_channel,
                "updated_at": datetime.now()
            }},
            upsert=True
        )
        logger.info(f"📥 Channel {name} ({channel_id}) updated")
        return result.acknowledged
    except Exception as e:
        logger.error(f"❌ Failed to update channel: {e}")
        return False

def remove_channel(channel_id):
    """Remove a force subscription channel"""
    try:
        result = channels_collection.delete_one({"_id": channel_id})
        if result.deleted_count > 0:
            logger.info(f"🗑️ Channel {channel_id} removed")
            return True
        logger.warning(f"⚠️ Channel {channel_id} not found")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to remove channel: {e}")
        return False

def get_channel(channel_id):
    """Get channel configuration"""
    try:
        return channels_collection.find_one({"_id": channel_id})
    except Exception as e:
        logger.error(f"❌ Failed to get channel: {e}")
        return None

def get_all_channels():
    """Get all force subscription channels"""
    try:
        return list(channels_collection.find())
    except Exception as e:
        logger.error(f"❌ Failed to get channels: {e}")
        return []

# Join Request Management
def create_request(user_id, channel_id):
    """Create new join request"""
    try:
        result = requests_collection.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$setOnInsert": {
                "status": "pending",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }},
            upsert=True
        )
        return result.upserted_id is not None
    except Exception as e:
        logger.error(f"❌ Failed to create request: {e}")
        return False

def update_request(user_id, channel_id, status):
    """Update request status"""
    valid_statuses = ["approved", "rejected", "pending"]
    if status not in valid_statuses:
        logger.error(f"❌ Invalid status: {status}")
        return False
        
    try:
        result = requests_collection.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {
                "status": status,
                "updated_at": datetime.now()
            }}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to update request: {e}")
        return False

def get_request_status(user_id, channel_id):
    """Get current request status"""
    try:
        doc = requests_collection.find_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"status": 1}
        )
        return doc.get("status", "none") if doc else "none"
    except Exception as e:
        logger.error(f"❌ Failed to get request status: {e}")
        return "error"

# User Management
def add_user(user_id):
    """Add new user to database"""
    try:
        users_collection.update_one(
            {"_id": user_id},
            {"$setOnInsert": {
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to add user: {e}")
        return False

def get_user(user_id):
    """Get user document"""
    try:
        return users_collection.find_one({"_id": user_id})
    except Exception as e:
        logger.error(f"❌ Failed to get user: {e}")
        return None

def update_user_activity(user_id):
    """Update user's last active time"""
    try:
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {"last_active": datetime.now()}}
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update user activity: {e}")
        return False

# Ban Management
def ban_user(user_id):
    """Add user to ban list"""
    try:
        banned_users_collection.insert_one({
            "_id": user_id,
            "banned_at": datetime.now()
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        return True  # Already banned
    except Exception as e:
        logger.error(f"❌ Failed to ban user: {e}")
        return False

def unban_user(user_id):
    """Remove user from ban list"""
    try:
        result = banned_users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to unban user: {e}")
        return False

def is_banned(user_id):
    """Check if user is banned"""
    try:
        return bool(banned_users_collection.find_one({"_id": user_id}))
    except Exception as e:
        logger.error(f"❌ Failed to check ban status: {e}")
        return False

# Admin Management
def add_admin(user_id):
    """Add new admin"""
    try:
        settings_collection.update_one(
            {"_id": 1},
            {"$addToSet": {"admins": user_id}}
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to add admin: {e}")
        return False

def remove_admin(user_id):
    """Remove admin"""
    try:
        settings_collection.update_one(
            {"_id": 1},
            {"$pull": {"admins": user_id}}
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to remove admin: {e}")
        return False

def get_admins():
    """Get list of admins"""
    try:
        doc = settings_collection.find_one({"_id": 1})
        return doc.get("admins", []) if doc else []
    except Exception as e:
        logger.error(f"❌ Failed to get admins: {e}")
        return []

# Initialize database on import
initialize_defaults()
