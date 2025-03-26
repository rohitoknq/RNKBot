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
    channel_link = await get_invite_link(channel_id)
    channel_name = escape(join_request.chat.title)

    logger.info(f"Jᴏɪɴ ʀᴇǫᴜᴇsᴛ ғʀᴏᴍ ᴜsᴇʀ {user_id} ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_name} (ID: {channel_id})")

    fsubs = load_fsubs()
    fsubs_channel_ids = {channel["_id"] for channel in fsubs}

    try:
        await client.approve_chat_join_request(chat_id=channel_id, user_id=user_id)
        join_message = (
            f"<b>Yᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ <i><a href='{channel_link}'>{channel_name}</a></i> ʜᴀs ʙᴇᴇɴ ᴀᴄᴄᴇᴘᴛᴇᴅ.</b>"
        )
        await client.send_photo(
            photo='plugins/image/start.jpg',
            has_spoiler=True,
            chat_id=user_id,
            caption=join_message,
        )
        logger.info(f"Approved join request for user {user_id} in channel {channel_name}.")

        # Check if user is present in the database, and add if not
        if not present_user(user_id):
            try:
                await add_user(user_id)
            except Exception as e:
                logger.error(f"Error adding user: {e}")

    except Exception as e:
        logger.error(f"Error approving join request for user {user_id} in channel {channel_id}: {e}")
