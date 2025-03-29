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

# Index Management
def create_indexes():
    """Create required database indexes"""
    try:
        # Handle existing index
        existing_indexes = requests_collection.index_information()
        if 'user_id_1_channel_id_1' in existing_indexes:
            requests_collection.drop_index('user_id_1_channel_id_1')
        
        requests_collection.create_index(
            [("user_id", 1), ("channel_id", 1)], 
            unique=True,
            name="user_channel_idx"
        )
        channels_collection.create_index("_id", unique=True)
        logger.info("✅ Database indexes created")
    except pymongo.errors.OperationFailure as e:
        if "IndexOptionsConflict" in str(e):
            logger.warning("⚠️ Index already exists, skipping creation")
        else:
            logger.error(f"❌ Index creation failed: {e}")
    except Exception as e:
        logger.error(f"❌ Index setup error: {e}")

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

# Ban Management
def add_ban(user_id):
    """Add user to ban list"""
    try:
        banned_users_collection.update_one(
            {"_id": user_id},
            {"$setOnInsert": {
                "banned_at": datetime.now()
            }},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to ban user: {e}")
        return False

def remove_ban(user_id):
    """Remove user from ban list"""
    try:
        result = banned_users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to unban user: {e}")
        return False

# Admin Management
async def get_admins():
    """Get admin list"""
    try:
        doc = settings_collection.find_one({"_id": 1})
        return doc.get("admins", []) if doc else []
    except Exception as e:
        logger.error(f"❌ Failed to get admins: {e}")
        return []

async def get_admin_ids():
    """Get admin IDs as integers"""
    try:
        admins = await get_admins()
        return [int(admin_id) for admin_id in admins]
    except Exception as e:
        logger.error(f"❌ Failed to get admin IDs: {e}")
        return []

# Spoiler Management
def edit_spoiler(value):
    """Update spoiler setting"""
    try:
        settings_collection.update_one(
            {"_id": 1},
            {"$set": {"SPOILER": value}}
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update spoiler: {e}")
        return False

def get_spoiler():
    """Get current spoiler setting"""
    try:
        doc = settings_collection.find_one({"_id": 1})
        return doc.get("SPOILER", False) if doc else False
    except Exception as e:
        logger.error(f"❌ Failed to get spoiler: {e}")
        return False

# Initialize database
initialize_defaults()
create_indexes()
