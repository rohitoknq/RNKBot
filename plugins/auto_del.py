from bot import Bot
from database.database import edit_auto_del, edit_file_auto_del, get_admins, get_admin_ids
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import settings, SUDO, ADMINS


@Bot.on_message(filters.command("auto_del") & filters.private)
async def auto_del_option(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        
        ad = await client.ask(message.chat.id, text="Sᴇɴᴅ Mᴇssᴀɢᴇ Yᴇs/Tʀᴜᴇ/Oɴ ᴛᴏ ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀɴᴅ sᴇɴᴅ Nᴏ/Fᴀʟsᴇ/Oғғ ᴛᴏ ᴅɪsᴀʙʟᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ.")
        ad_l = ad.text.lower()
        if ad_l in ("on", "yes", "true"):
            edit_auto_del(True)
            OUT = f"Aᴜᴛᴏ Dᴇʟᴇᴛᴇ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ."
        elif ad_l in ("no", "false", "off"):
            edit_auto_del(False)
            OUT = f"Aᴜᴛᴏ Dᴇʟᴇᴛᴇ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ."
        else:
            OUT = f"Aᴜᴛᴏ Dᴇʟᴇᴛᴇ Vᴀʟᴜᴇ ʜᴀs ɴᴏᴛ ᴄʜᴀɴɢᴇᴅ."
        await message.reply_text(OUT, quote=True)
    
@Bot.on_message(filters.command("del_timer") & filters.private)
async def auto_del_timer(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        adt = await client.ask(message.chat.id, text="Sᴇɴᴅ Iɴᴛᴇɢᴇʀ Vᴀʟᴜᴇ ғᴏʀ Aᴜᴛᴏ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ, sʜᴏᴜʟᴅ ʙᴇ ɢʀᴇᴀᴛᴏʀ ᴛʜᴀɴ 0, ᴠᴀʟᴜᴇ ᴡɪʟʟ ʙᴇ ᴛᴀᴋᴇɴ ɪɴ sᴇᴄᴏɴᴅs.")
        adt_i = int(adt.text)
        if adt_i > 0:
            edit_file_auto_del(adt_i)
            OUT = f"Aᴜᴛᴏ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ {adt_i} sᴇᴄᴏɴᴅs."
        else:
            OUT = f"Aᴜᴛᴏ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ sʜᴏᴜʟᴅ ʙᴇ ɢʀᴇᴀᴛᴏʀ ᴛʜᴀɴ 0."
        await message.reply_text(OUT, quote=True)

