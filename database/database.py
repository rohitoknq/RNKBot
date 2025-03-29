import pymongo
import logging
from bot import Bot
from config import DB_URI, DB_NAME, settings, FSUBS

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the MongoDB client
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

# Define MongoDB collections
user_data = database['users']
banuser_data = database['bannedusers']
settings_collection = database['settings']
fsubs_collection = database['forcesubs']

# Default values for settings and force subscriptions
default_settings = settings
default_fsubs = FSUBS


# -----Force-Subs-DB----- #
def load_fsubs():
    fsubs = list(fsubs_collection.find())
    if not fsubs:
        fsubs_collection.insert_many(default_fsubs)
        fsubs = default_fsubs
    return fsubs  # Return the full document instead of just the IDs
    
# Function to get the current list of bot admins from the database
async def get_admins():
    settings_doc = settings_collection.find_one({"_id": 1})
    if settings_doc and "bot_admin" in settings_doc:
        return settings_doc["bot_admin"]
    return []

async def get_admin_ids():
    admin_ids = await get_admins()
    return [int(admin_id) for admin_id in admin_ids]


def add_bot_admin(user_id):
    settings_doc = settings_collection.find_one({"_id": 1})
    if settings_doc:
        bot_admin_list = settings_doc.get("bot_admin", [])
        if user_id not in bot_admin_list:
            bot_admin_list.append(user_id)
            settings_collection.update_one({"_id": 1}, {"$set": {"bot_admin": bot_admin_list}})
            return True
    return False

def remove_bot_admin(user_id):
    settings_doc = settings_collection.find_one({"_id": 1})
    if settings_doc:
        bot_admin_list = settings_doc.get("bot_admin", [])
        if user_id in bot_admin_list:
            bot_admin_list.remove(user_id)
            settings_collection.update_one({"_id": 1}, {"$set": {"bot_admin": bot_admin_list}})
            return True
    return False
    
def del_fsub(channel_id):
    try:
        fsubs_collection.delete_one({'_id': channel_id})
        logger.info(f"Force subscription with ID {channel_id} deleted.")
    except Exception as e:
        logger.error(f"Error deleting force subscription {channel_id}: {e}")

def add_fsub(channel_id, channel_name, is_private=False, auto_accept=False):
    """Adds a channel to the fsubs collection with additional parameters"""
    try:
        if not fsubs_collection.find_one({'_id': channel_id}):
            fsubs_collection.insert_one({
                '_id': channel_id,
                'CHANNEL_NAME': channel_name,
                'is_private': is_private,
                'auto_accept': auto_accept,
                'request_channel': None  # To store request channel ID if needed
            })
            logger.info(f"Added force subscription for channel {channel_name} (ID: {channel_id}).")
        else:
            logger.info(f"Channel {channel_name} (ID: {channel_id}) is already in the fsubs list.")
    except Exception as e:
        logger.error(f"Error adding force subscription for channel {channel_id}: {e}")

# -----Settings-DB----- # 
def load_settings():
    settings_data = settings_collection.find_one({'_id': 1})
    if settings_data:
        return True
    else:
        settings_collection.insert_one(default_settings)
        logger.info("Default settings inserted.")
        return False

def edit_spoiler(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"SPOILER": value}})

def get_spoiler():
    spoiler_data = settings_collection.find_one({'_id': 1})
    return spoiler_data.get("SPOILER", False) if spoiler_data else False

def edit_auto_del(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"AUTO_DEL": value}})

def get_auto_del():
    auto_del_data = settings_collection.find_one({'_id': 1})
    return auto_del_data.get("AUTO_DEL", False) if auto_del_data else False

def edit_file_auto_del(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"FILE_AUTO_DELETE": value}})

def get_file_del_timer():
    file_del_timer = settings_collection.find_one({'_id': 1})
    return file_del_timer["FILE_AUTO_DELETE"]

def edit_sticker_id(value):
    settings_collection.update_one({'_id': 1}, {'$set': {"STICKER_ID": value}})

def get_sticker_id():
    sticker_id = settings_collection.find_one({'_id': 1})
    return sticker_id["STICKER_ID"]

# -----Users-DB----- #
def present_user(user_id: int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})

def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] for doc in user_docs]
    return user_ids

def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
        
# -----Banned-Users-DB----- #
def present_ban_user(user_id: int):
    found = banuser_data.find_one({'_id': user_id})
    return bool(found)

def add_ban_user(user_id: int):
    banuser_data.insert_one({'_id': user_id})

def full_banuserbase():
    user_docs = banuser_data.find()
    user_ids = [doc['_id'] for doc in user_docs]
    return user_ids

def del_ban_user(user_id: int):
    banuser_data.delete_one({'_id': user_id})
        
        
async def get_banned():
    banned_doc = settings_collection.find_one({"_id": 1})
    if banned_doc and "banned_ids" in banned_doc:
        return banned_doc["banned_ids"]
    return []

async def get_banned_ids():
    banned_ids = await get_banned()
    return [int(banned_id) for banned_id in banned_ids]

def add_ban(user_id):
    banned_doc = settings_collection.find_one({"_id": 1})
    if banned_doc:
        banned_list = banned_doc.get("banned_ids", [])
        if user_id not in banned_list:
            banned_list.append(user_id)
            settings_collection.update_one({"_id": 1}, {"$set": {"banned_ids": banned_list}})
            return True
    return False

def remove_ban(user_id):
    banned_doc = settings_collection.find_one({"_id": 1})
    if banned_doc:
        banned_list = banned_doc.get("banned_ids", [])
        if user_id in banned_list:
            banned_list.remove(user_id)
            settings_collection.update_one({"_id": 1}, {"$set": {"banned_ids": banned_list}})
            return True
    return False
    
