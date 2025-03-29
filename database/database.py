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
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

# Collections
user_data = database['users']
banuser_data = database['bannedusers']
settings_collection = database['settings']
fsubs_collection = database['forcesubs']
join_requests = database['join_requests']
request_channels = database['request_channels']

# Default configurations
default_settings = settings
default_fsubs = FSUBS

def load_fsubs():
    """Load force subscription channels from database"""
    try:
        fsubs = list(fsubs_collection.find())
        if not fsubs:
            fsubs_collection.insert_many(default_fsubs)
            return default_fsubs
        return fsubs
    except Exception as e:
        logger.error(f"Error loading fsubs: {e}")
        return []

def load_settings():
    """Initialize settings if not exists"""
    try:
        if not settings_collection.find_one({"_id": 1}):
            settings_collection.insert_one(default_settings)
            logger.info("Default settings initialized")
        return True
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return False

# Force Subscription Functions
def add_fsub(channel_id, channel_name, is_private=False, auto_accept=False, request_channel=None):
    """Add/update force subscription channel"""
    try:
        fsubs_collection.update_one(
            {'_id': channel_id},
            {'$set': {
                'CHANNEL_NAME': channel_name,
                'is_private': is_private,
                'auto_accept': auto_accept,
                'request_channel': request_channel,
                'updated_at': datetime.now()
            }},
            upsert=True
        )
        logger.info(f"Updated fsub: {channel_name} ({channel_id})")
        return True
    except Exception as e:
        logger.error(f"Error adding fsub: {e}")
        return False

def del_fsub(channel_id):
    """Remove force subscription channel"""
    try:
        fsubs_collection.delete_one({'_id': channel_id})
        logger.info(f"Deleted fsub: {channel_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting fsub: {e}")
        return False

def get_channel_settings(channel_id):
    """Get full channel configuration"""
    return fsubs_collection.find_one({'_id': channel_id})

# Join Request Handling
def log_join_request(user_id, channel_id, approved=False):
    """Log join request status"""
    try:
        join_requests.update_one(
            {'user_id': user_id, 'channel_id': channel_id},
            {'$set': {
                'approved': approved,
                'timestamp': datetime.now()
            }},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error logging request: {e}")

def has_approved_request(user_id, channel_id):
    """Check if request exists and is approved"""
    try:
        return bool(join_requests.find_one({
            'user_id': user_id,
            'channel_id': channel_id,
            'approved': True
        }))
    except Exception as e:
        logger.error(f"Error checking request: {e}")
        return False

# User Management
def present_user(user_id: int):
    return bool(user_data.find_one({'_id': user_id}))

def add_user(user_id: int):
    user_data.insert_one({'_id': user_id, 'joined_at': datetime.now()})

def full_userbase():
    return [doc['_id'] for doc in user_data.find()]

def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})

# Banned Users
def present_ban_user(user_id: int):
    return bool(banuser_data.find_one({'_id': user_id}))

def add_ban_user(user_id: int):
    banuser_data.insert_one({'_id': user_id, 'banned_at': datetime.now()})

def full_banuserbase():
    return [doc['_id'] for doc in banuser_data.find()]

def del_ban_user(user_id: int):
    banuser_data.delete_one({'_id': user_id})

# Settings Management
def edit_spoiler(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"SPOILER": value}})

def get_spoiler():
    return settings_collection.find_one({'_id': 1}).get("SPOILER", False)

def edit_auto_del(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"AUTO_DEL": value}})

def get_auto_del():
    return settings_collection.find_one({'_id': 1}).get("AUTO_DEL", False)

def edit_file_auto_del(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"FILE_AUTO_DELETE": value}})

def get_file_del_timer():
    return settings_collection.find_one({'_id': 1}).get("FILE_AUTO_DELETE", 0)

def edit_sticker_id(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"STICKER_ID": value}})

def get_sticker_id():
    return settings_collection.find_one({'_id': 1}).get("STICKER_ID", None)

# Admin Management
async def get_admins():
    settings_doc = settings_collection.find_one({"_id": 1})
    return settings_doc.get("bot_admin", []) if settings_doc else []

async def get_admin_ids():
    return [int(admin_id) for admin_id in (await get_admins())]

def add_bot_admin(user_id):
    settings_collection.update_one(
        {"_id": 1},
        {"$addToSet": {"bot_admin": str(user_id)}}
    )

def remove_bot_admin(user_id):
    settings_collection.update_one(
        {"_id": 1},
        {"$pull": {"bot_admin": str(user_id)}}
    )

# Ban Management
async def get_banned():
    settings_doc = settings_collection.find_one({"_id": 1})
    return settings_doc.get("banned_ids", []) if settings_doc else []

async def get_banned_ids():
    return [int(banned_id) for banned_id in (await get_banned())]

def add_ban(user_id):
    settings_collection.update_one(
        {"_id": 1},
        {"$addToSet": {"banned_ids": str(user_id)}}
    )

def remove_ban(user_id):
    settings_collection.update_one(
        {"_id": 1},
        {"$pull": {"banned_ids": str(user_id)}}
    )
