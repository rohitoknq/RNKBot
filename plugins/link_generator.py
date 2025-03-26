from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from database.database import get_admins, get_admin_ids
from config import ADMINS, SUDO
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.command('b_link'))
async def batch(client: Client, message: Message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        while True:
            try:
                first_message = await client.ask(text = "Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Fɪʀsᴛ Mᴇssᴀɢᴇ ғʀᴏᴍ DB Cʜᴀɴɴᴇʟ (ᴡɪᴛʜ Qᴜᴏᴛᴇs) ᴏʀ Sᴇɴᴅ ᴛʜᴇ DB Cʜᴀɴɴᴇʟ Pᴏsᴛ Lɪɴᴋ...", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=1600)
            except:
                return
            f_msg_id = await get_message_id(client, first_message)
            if f_msg_id:
                break
            else:
                await first_message.reply("Eʀʀᴏʀ: Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ Pᴏsᴛ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ DB Cʜᴀɴɴᴇʟ ᴏʀ ᴛʜɪs Lɪɴᴋ ɪs ᴛᴀᴋᴇɴ ғʀᴏᴍ DB Cʜᴀɴɴᴇʟ...", quote = True)
                continue
    
        while True:
            try:
                second_message = await client.ask(text = "Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Lᴀsᴛ Mᴇssᴀɢᴇ ғʀᴏᴍ DB Cʜᴀɴɴᴇʟ (ᴡɪᴛʜ Qᴜᴏᴛᴇs) ᴏʀ Sᴇɴᴅ ᴛʜᴇ DB Cʜᴀɴɴᴇʟ Pᴏsᴛ ʟɪɴᴋ...", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=1600)
            except:
                return
            s_msg_id = await get_message_id(client, second_message)
            if s_msg_id:
                break
            else:
                await second_message.reply("Eʀʀᴏʀ: Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ Pᴏsᴛ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ DB Cʜᴀɴɴᴇʟ ᴏʀ ᴛʜɪs Lɪɴᴋ ɪs ᴛᴀᴋᴇɴ ғʀᴏᴍ DB Cʜᴀɴɴᴇʟ...", quote = True)
                continue
    
    
        string = f"{f_msg_id}-{s_msg_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start=filez{base64_string}"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Sʜᴀʀᴇ URL", url=f'https://telegram.me/share/url?url={link}')]])
        await second_message.reply_text(f"<b>Lɪɴᴋ - </b>{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.command('g_link'))
async def link_generator(client: Client, message: Message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        while True:
            try:
                channel_message = await client.ask(text = "Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Lᴀsᴛ Mᴇssᴀɢᴇ ғʀᴏᴍ DB Cʜᴀɴɴᴇʟ (ᴡɪᴛʜ Qᴜᴏᴛᴇs) ᴏʀ Sᴇɴᴅ ᴛʜᴇ DB Cʜᴀɴɴᴇʟ Pᴏsᴛ ʟɪɴᴋ...", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
            except:
                return
            msg_id = await get_message_id(client, channel_message)
            if msg_id:
                break
            else:
                await channel_message.reply("Eʀʀᴏʀ: Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ Pᴏsᴛ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ DB Cʜᴀɴɴᴇʟ ᴏʀ ᴛʜɪs Lɪɴᴋ ɪs ᴛᴀᴋᴇɴ ғʀᴏᴍ DB Cʜᴀɴɴᴇʟ...", quote = True)
                continue
    
        base64_string = await encode(f"{msg_id}")
        link = f"https://t.me/{client.username}?start=filez{base64_string}"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Sʜᴀʀᴇ URL", url=f'https://telegram.me/share/url?url={link}')]])
        await channel_message.reply_text(f"<b>Lɪɴᴋ - </b>{link}", quote=True, reply_markup=reply_markup)
    
