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
    logger.info("Database connection established")
except Exception as e:
    logger.critical(f"Database connection failed: {e}")
    raise

# Collections
user_data = database['users']
banuser_data = database['bannedusers']
settings_collection = database['settings']
fsubs_collection = database['forcesubs']
join_requests = database['join_requests']

# Create indexes
try:
    join_requests.create_index([("user_id", 1), ("channel_id", 1)], unique=True)
    fsubs_collection.create_index("_id", unique=True)
    logger.info("Database indexes created")
except Exception as e:
    logger.error(f"Index creation failed: {e}")

# Initialize default data
def initialize_defaults():
    """Load default configurations"""
    try:
        # Settings
        if not settings_collection.find_one({"_id": 1}):
            settings_collection.insert_one(settings)
            logger.info("Default settings loaded")
        
        # Force subs
        if fsubs_collection.count_documents({}) == 0 and FSUBS:
            fsubs_collection.insert_many(FSUBS)
            logger.info("Default force subs loaded")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")

# Force Subscription Functions
def add_fsub(channel_id, channel_name, is_private=False, auto_accept=False, request_channel=None):
    """Add/update force subscription channel"""
    try:
        result = fsubs_collection.update_one(
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
        logger.info(f"Updated fsub: {channel_name} (ID: {channel_id})")
        return result.acknowledged
    except Exception as e:
        logger.error(f"Error adding fsub: {e}")
        return False

def del_fsub(channel_id):
    """Remove force subscription channel"""
    try:
        result = fsubs_collection.delete_one({'_id': channel_id})
        logger.info(f"Deleted fsub: {channel_id}")
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting fsub: {e}")
        return False

def load_fsubs():
    """Load all force subs"""
    try:
        return list(fsubs_collection.find())
    except Exception as e:
        logger.error(f"Error loading fsubs: {e}")
        return []

def get_channel_settings(channel_id):
    """Get channel configuration"""
    try:
        return fsubs_collection.find_one({'_id': channel_id})
    except Exception as e:
        logger.error(f"Error getting channel: {e}")
        return None

# Join Request Management
def log_join_request(user_id, channel_id, approved=False):
    """Log a new join request"""
    try:
        result = join_requests.update_one(
            {'user_id': user_id, 'channel_id': channel_id},
            {'$set': {
                'approved': approved,
                'timestamp': datetime.now()
            }},
            upsert=True
        )
        return result.acknowledged
    except Exception as e:
        logger.error(f"Error logging request: {e}")
        return False

def update_join_request(user_id, channel_id, approved):
    """Update request status"""
    try:
        result = join_requests.update_one(
            {'user_id': user_id, 'channel_id': channel_id},
            {'$set': {
                'approved': approved,
                'processed_at': datetime.now()
            }}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating request: {e}")
        return False

def has_approved_request(user_id, channel_id):
    """Check if request was approved"""
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
def present_user(user_id):
    """Check if user exists"""
    try:
        return bool(user_data.find_one({'_id': user_id}))
    except Exception as e:
        logger.error(f"Error checking user: {e}")
        return False

def add_user(user_id):
    """Add new user"""
    try:
        user_data.insert_one({
            '_id': user_id,
            'joined_at': datetime.now(),
            'last_active': datetime.now()
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        return True  # Already exists
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False

def full_userbase():
    """Get all user IDs"""
    try:
        return [doc['_id'] for doc in user_data.find({}, {'_id': 1})]
    except Exception as e:
        logger.error(f"Error getting userbase: {e}")
        return []

# Admin Management
async def get_admins():
    """Get admin list"""
    try:
        doc = settings_collection.find_one({"_id": 1})
        return doc.get("bot_admin", []) if doc else []
    except Exception as e:
        logger.error(f"Error getting admins: {e}")
        return []

async def get_admin_ids():
    """Get admin IDs as integers"""
    try:
        return [int(admin_id) for admin_id in (await get_admins())]
    except Exception as e:
        logger.error(f"Error getting admin IDs: {e}")
        return []

# Initialize on import
initialize_defaults()
