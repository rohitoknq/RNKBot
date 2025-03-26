from bot import Bot
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import SUDO
from database.database import add_ban, remove_ban, get_banned, get_banned_ids, get_admin_ids


@Bot.on_message(filters.command("ban") & filters.private)
async def add_ban_user(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        ad_ban = message.text.split(" ")[1:]
        ad_ban = [int(ban_id) for ban_id in ad_ban]
        
        added_ids = []
        for ban_id in ad_ban:
            if add_ban(ban_id):  # Add to the database
                added_ids.append(ban_id)
                await client.send_message(chat_id=ban_id, text="Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.")

    
        if added_ids:
            OUT = f"Aᴅᴅᴇᴅ {added_ids} ᴛᴏ ᴛʜᴇ ʙᴀɴ ʟɪsᴛ."
        else:
            OUT = "Nᴏ ɴᴇᴡ ʙᴀɴs ᴡᴇʀᴇ ᴀᴅᴅᴇᴅ; ᴛʜᴇʏ ᴍᴀʏ ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛ ɪɴ ᴛʜᴇ ʟɪsᴛ."
        
        await message.reply_text(OUT, quote=True)

@Bot.on_message(filters.command("unban") & filters.private)
async def remove_ban_users(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        rm_ban = message.text.split(" ")[1:]
        rm_ban = [int(ban_id) for ban_id in rm_ban]
        
        removed_ids = []
        not_found_ids = []
        for ban_id in rm_ban:
            if remove_ban(ban_id):  # Remove from the database
                removed_ids.append(ban_id)
                await client.send_message(chat_id=ban_id, text="Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.")

            else:
                not_found_ids.append(ban_id)
        
        OUT = f"Rᴇᴍᴏᴠᴇᴅ {removed_ids} ғʀᴏᴍ ᴛʜᴇ ʙᴀɴ ʟɪsᴛ."
        if not_found_ids:
            OUT += f" Tʜᴇsᴇ IDs ᴡᴇʀᴇ ɴᴏᴛ ɪɴ ᴛʜᴇ ʙᴀɴ ʟɪsᴛ: {not_found_ids}."
        
        await message.reply_text(OUT, quote=True)

@Bot.on_message(filters.command("banlist") & filters.private)
async def show_ban_users(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        
        banned_list = await get_banned()  # Retrieve from the database
        await message.reply_text(f"**Cᴜʀʀᴇɴᴛ ʙᴀɴ ᴍᴇᴍʙᴇʀs: {banned_list}**", quote=True)

