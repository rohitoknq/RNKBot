from pyrogram import filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import (
    get_channel_settings,
    log_join_request,
    has_approved_request,
    add_bot_admin,
    remove_bot_admin
)
from bot import Bot
import logging
from config import ADMINS

logger = logging.getLogger(__name__)

async def is_admin(user_id: int):
    return user_id in ADMINS or user_id in await get_admin_ids()

@Bot.on_chat_join_request(filters.channel)
async def handle_join_request(client: Bot, join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    channel_settings = get_channel_settings(channel_id)
    
    if not channel_settings:
        return
    
    try:
        # Auto-approve handling
        if channel_settings.get('auto_accept'):
            await client.approve_chat_join_request(channel_id, user_id)
            log_join_request(user_id, channel_id, approved=True)
            await client.send_message(
                user_id,
                f"✅ **Auto-approved!**\nYou can now access {join_request.chat.title}!"
            )
        else:
            # Log pending request
            log_join_request(user_id, channel_id, approved=False)
            
            # Send request to admin channel
            if channel_settings.get('request_channel'):
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Approve", 
                            callback_data=f"approve_{user_id}_{channel_id}"),
                        InlineKeyboardButton("❌ Deny", 
                            callback_data=f"deny_{user_id}_{channel_id}")
                    ]
                ])
                
                await client.send_message(
                    channel_settings['request_channel'],
                    f"📥 New join request from [{user_id}](tg://user?id={user_id})\n"
                    f"Channel: {join_request.chat.title}\n"
                    f"User: {join_request.from_user.mention}",
                    reply_markup=keyboard
                )
                
            # Notify user
            await client.send_message(
                user_id,
                "⌛ **Request Received!**\n"
                "You can use the bot while we review your request!"
            )
            
    except Exception as e:
        logger.error(f"Join request error: {e}")
        await client.send_message(
            user_id,
            "⚠️ An error occurred processing your request. Please try again later."
        )

@Bot.on_callback_query(filters.regex(r"^approve_|^deny_"))
async def handle_approval(client: Bot, query: CallbackQuery):
    if not await is_admin(query.from_user.id):
        await query.answer("You're not authorized!", show_alert=True)
        return
        
    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])
    channel_id = int(data[2])
    
    try:
        if action == "approve":
            # Approve request
            await client.approve_chat_join_request(channel_id, user_id)
            log_join_request(user_id, channel_id, approved=True)
            
            # Update user
            await client.send_message(
                user_id,
                f"🎉 **Request Approved!**\n"
                f"You now have access to all features!"
            )
            
            # Update admin message
            await query.message.edit_text(
                f"✅ Approved by {query.from_user.mention}",
                reply_markup=None
            )
            
        else:
            # Deny request
            await client.decline_chat_join_request(channel_id, user_id)
            log_join_request(user_id, channel_id, approved=False)
            
            # Update admin message
            await query.message.edit_text(
                f"❌ Denied by {query.from_user.mention}",
                reply_markup=None
            )
            
            # Notify user
            await client.send_message(
                user_id,
                "⚠️ **Request Denied**\n"
                "Contact admins for more information."
            )
            
    except Exception as e:
        logger.error(f"Approval error: {e}")
        await query.answer("Failed to process request!", show_alert=True)

# Add this in database.py
"""
async def get_admin_ids():
    return [int(admin_id) for admin_id in (await get_admins())]
"""
