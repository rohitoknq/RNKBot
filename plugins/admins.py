from bot import Bot
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import SUDO
from database.database import get_admins, add_bot_admin, remove_bot_admin, get_admin_ids

@Bot.on_message(filters.command("add_admin") & filters.private & filters.user(SUDO))
async def add_new_admins(client, message):
    ad_adm = message.text.split(" ")[1:]
    ad_adm = [int(admin_id) for admin_id in ad_adm]
    
    added_ids = []
    for admin_id in ad_adm:
        if add_bot_admin(admin_id):  # Add to the database
            added_ids.append(admin_id)
            await client.send_message(chat_id=admin_id, text="ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴘʀᴏᴍᴏᴛᴇᴅ ᴛᴏ ᴀᴅᴍɪɴ.")

    if added_ids:
        OUT = f"Aᴅᴅᴇᴅ {added_ids} ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴ ʟɪsᴛ."
    else:
        OUT = "Nᴏ ɴᴇᴡ ᴀᴅᴍɪɴs ᴡᴇʀᴇ ᴀᴅᴅᴇᴅ; ᴛʜᴇʏ ᴍᴀʏ ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛ ɪɴ ᴛʜᴇ ʟɪsᴛ."
    
    await client.reply_text(OUT, quote=True)

@Bot.on_message(filters.command("rm_admin") & filters.private & filters.user(SUDO))
async def remove_old_admins(client, message):
    rm_adm = message.text.split(" ")[1:]
    rm_adm = [int(admin_id) for admin_id in rm_adm]
    
    removed_ids = []
    not_found_ids = []
    for admin_id in rm_adm:
        if remove_bot_admin(admin_id):  # Remove from the database
            removed_ids.append(admin_id)
            await client.send_message(chat_id=admin_id, text="Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇᴍᴏᴛᴇᴅ ғʀᴏᴍ ᴀᴅᴍɪɴ.")
 
        else:
            not_found_ids.append(admin_id)
    
    OUT = f"Rᴇᴍᴏᴠᴇᴅ {removed_ids} ғʀᴏᴍ ᴛʜᴇ ᴀᴅᴍɪɴ ʟɪsᴛ."
    if not_found_ids:
        OUT += f" Tʜᴇsᴇ IDs ᴡᴇʀᴇ ɴᴏᴛ ɪɴ ᴛʜᴇ ᴀᴅᴍɪɴ ʟɪsᴛ: {not_found_ids}"
    
    await client.reply_text(OUT, quote=True)

@Bot.on_message(filters.command("sudo") & filters.private)
async def sudousers(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        
        admin_list = await get_admins()  # Retrieve from the database
        await message.reply_text(f"**Cᴜʀʀᴇɴᴛ ᴀᴅᴍɪɴs: {admin_list}**", quote=True)
