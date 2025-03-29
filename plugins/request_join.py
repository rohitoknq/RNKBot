from pyrogram import filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import (
    get_channel_settings,
    log_join_request,
    has_approved_request,
    update_join_request,
    get_admin_ids
)
from bot import Bot
import logging
from config import ADMINS

logger = logging.getLogger(__name__)

async def is_admin(user_id: int):
    """Check if user is admin"""
    return user_id in ADMINS or user_id in await get_admin_ids()

@Bot.on_chat_join_request(filters.channel)
async def handle_join_request(client: Bot, join_request: ChatJoinRequest):
    """Handle new join requests and grant temporary access"""
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    channel_settings = get_channel_settings(channel_id)
    
    if not channel_settings:
        return
    
    try:
        # Always log the request first
        log_join_request(user_id, channel_id, approved=False)
        
        if channel_settings.get('auto_accept'):
            # Auto-approve if enabled
            await client.approve_chat_join_request(channel_id, user_id)
            update_join_request(user_id, channel_id, approved=True)
            await client.send_message(
                user_id,
                f"✅ **Instant Access Granted!**\n"
                f"You've been automatically approved for {join_request.chat.title}!"
            )
        else:
            # Notify request channel if exists
            request_channel = channel_settings.get('request_channel')
            if request_channel:
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Approve", 
                            callback_data=f"approve_{user_id}_{channel_id}"),
                        InlineKeyboardButton("❌ Deny", 
                            callback_data=f"deny_{user_id}_{channel_id}")
                    ]
                ])
                
                await client.send_message(
                    request_channel,
                    f"📥 New join request from [{user_id}](tg://user?id={user_id})\n"
                    f"**Channel:** {join_request.chat.title}\n"
                    f"**User:** {join_request.from_user.mention}",
                    reply_markup=keyboard
                )
            
            # Notify user about temporary access
            await client.send_message(
                user_id,
                "⏳ **Request Received!**\n"
                "You can use the bot while we review your request!\n\n"
                "Status: __Pending Review__",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Check Status", 
                        callback_data=f"status_{channel_id}")]
                ])
            )

    except Exception as e:
        logger.error(f"Join request error: {e}")
        await client.send_message(
            user_id,
            "⚠️ An error occurred processing your request. Please try again later."
        )

@Bot.on_callback_query(filters.regex(r"^approve_|^deny_|^status_"))
async def handle_join_callbacks(client: Bot, query: CallbackQuery):
    """Handle all join request related callbacks"""
    user_id = query.from_user.id
    data = query.data.split("_")
    
    if data[0] in ("approve", "deny") and not await is_admin(user_id):
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
        
    if data[0] == "status":
        # User checking request status
        channel_id = int(data[1])
        status = "Approved" if has_approved_request(query.from_user.id, channel_id) else "Pending"
        
        await query.answer(
            f"Current Status: {status}",
            show_alert=True
        )
        return
    
    # Handle approval/denial
    action = data[0]
    target_user = int(data[1])
    channel_id = int(data[2])
    
    try:
        if action == "approve":
            await client.approve_chat_join_request(channel_id, target_user)
            update_join_request(target_user, channel_id, approved=True)
            
            await client.send_message(
                target_user,
                f"🎉 **Request Approved!**\n"
                f"You now have full access to {query.message.chat.title}!"
            )
            
            await query.message.edit_text(
                f"✅ Approved by {query.from_user.mention}",
                reply_markup=None
            )
            
        elif action == "deny":
            await client.decline_chat_join_request(channel_id, target_user)
            update_join_request(target_user, channel_id, approved=False)
            
            await client.send_message(
                target_user,
                f"⚠️ **Request Denied**\n"
                f"Access to {query.message.chat.title} was not approved."
            )
            
            await query.message.edit_text(
                f"❌ Denied by {query.from_user.mention}",
                reply_markup=None
            )
            
        await query.answer("Action processed!")
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await query.answer("Failed to process request!", show_alert=True)
