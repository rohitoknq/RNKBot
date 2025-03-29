from pyrogram.enums import ChatMemberStatus
from bot import Bot
import logging
from plugins.start import get_invite_link
from database.database import *
from pyrogram import filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from html import escape

logger = logging.getLogger(__name__)

@Bot.on_chat_join_request(filters.channel)
async def handle_join_request(client, join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    channel_settings = get_channel_settings(channel_id)
    
    if not channel_settings:
        return
    
    # Auto-approve if enabled
    if channel_settings.get('auto_accept'):
        try:
            await client.approve_chat_join_request(channel_id, user_id)
            await client.send_message(
                user_id,
                f"✅ Automatically approved for {join_request.chat.title}!"
            )
        except Exception as e:
            logger.error(f"Auto-approve failed: {e}")
    
    # No auto-approve: Just let the request stay pending
    else:
        try:
            await client.send_message(
                user_id,
                f"📥 Your request to join {join_request.chat.title} has been received. "
                "You can now use the bot while we review your request!"
            )
        except Exception as e:
            logger.error(f"Request confirmation failed: {e}")
