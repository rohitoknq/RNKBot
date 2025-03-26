from bot import Bot
import os
from database.database import edit_spoiler, get_admins, get_admin_ids
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS, SUDO, settings

@Bot.on_message(filters.command("spoiler") & filters.private)
async def image_spoiler(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        spl = await client.ask(
            message.chat.id, 
            text="**Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sʜᴏᴡ sᴘᴏɪʟᴇʀ ɪɴ ɪᴍᴀɢᴇs? Tʏᴘᴇ Yᴇs/Oɴ/Tʀᴜᴇ ᴛᴏ ᴄᴏɴғɪʀᴍ, ᴏʀ Nᴏ/Oғғ/Fᴀʟsᴇ ᴛᴏ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ɴᴏ ᴄʜᴀɴɢᴇs ᴀᴘᴘʟɪᴇᴅ.**"
        )
        spl_l = spl.text.lower()
        
        if spl_l in ('on', 'true', 'yes'):
            edit_spoiler(True)
            OUT = "Sᴘᴏɪʟᴇʀ ʜᴀs ʙᴇᴇɴ sᴇᴛ."
        elif spl_l in ('off', 'no', 'false'):
            edit_spoiler(False)
            OUT = "Sᴘᴏɪʟᴇʀ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ."
        else:
            current_spoiler = get_spoiler()
            OUT = f"Sᴘᴏɪʟᴇʀ ᴠᴀʟᴜᴇ ʀᴇᴍᴀɪɴs ᴀs ʙᴇғᴏʀᴇ, ɪ.ᴇ., {current_spoiler}."
        
        await message.reply_text(OUT, quote=True)

    
