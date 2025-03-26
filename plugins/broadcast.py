from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS, SUDO, settings
from database.database import *
from pyrogram.raw.types import MessageActionPinMessage
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired
import asyncio

@Bot.on_message(filters.command('users') & filters.private)
async def get_users(client: Bot, message: Message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        msg = await client.send_message(chat_id=message.chat.id, text=f"Pʀᴏᴄᴇssɪɴɢ...")
        users = full_userbase()
        await msg.edit(f"**{len(users)} Usᴇʀs Aʀᴇ Usɪɴɢ Tʜɪs Bᴏᴛ.**")

@Bot.on_message(filters.private & filters.command('broadcast'))
async def send_text(client: Bot, message: Message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        
        if message.reply_to_message:
            query = full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
            
            pls_wait = await message.reply("<blockquote>Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ Mᴇssᴀɢᴇ... Tʜɪs ᴡɪʟʟ Tᴀᴋᴇ Sᴏᴍᴇ Tɪᴍᴇ</blockquote>")
            for chat_id in query:
                try:
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except UserIsBlocked:
                    await del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    print(f"Fᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ {chat_id}: {e}")
                    unsuccessful += 1
                    pass
                total += 1
            
            status = f"""<blockquote><b><u>Bʀᴏᴀᴅᴄᴀsᴛ ʜᴀs ʙᴇᴇɴ Cᴏᴍᴘʟᴇᴛᴇᴅ!!!</u></b></blockquote>
    <blockquote expandable><b>Tᴏᴛᴀʟ Usᴇʀs :</b> <code>{total}</code>
    <b>Sᴜᴄᴄᴇssғᴜʟ :</b> <code>{successful}</code>
    <b>Bʟᴏᴄᴋᴇᴅ :</b> <code>{blocked}</code>
    <b>Dᴇʟᴇᴛᴇᴅ :</b> <code>{deleted}</code>
    <b>Uɴsᴜᴄᴄᴇssғᴜʟ :</b> <code>{unsuccessful}</code><blockquote>"""
            
            return await pls_wait.edit_message_text(status)
    
        else:
            msg = await message.reply(f"**Usᴇ Tʜɪs Cᴏᴍᴍᴀɴᴅ As A Rᴇᴘʟʏ Tᴏ Aɴʏ Tᴇʟᴇɢʀᴀᴍ Mᴇssᴀɢᴇ Wɪᴛʜᴏᴜᴛ Aɴʏ Sᴘᴀᴄᴇs.**")
            await asyncio.sleep(4)
            await msg.delete()



@Bot.on_message(filters.private & filters.command('pbroadcast'))
async def pin_bdcst_text(client: Bot, message: Message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id in admin_ids:
        if message.reply_to_message:
            query = full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
    
            pls_wait = await message.reply("<blockquote>Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ Mᴇssᴀɢᴇ... Tʜɪs ᴡɪʟʟ Tᴀᴋᴇ Sᴏᴍᴇ Tɪᴍᴇ</blockquote>")
            
            for chat_id in query:
                try:
                    sent_msg = await broadcast_msg.copy(chat_id)
                    successful += 1
    
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    sent_msg = await broadcast_msg.copy(chat_id)
                    successful += 1
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id)
                except UserIsBlocked:
                    await del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")
                    unsuccessful += 1
                total += 1
    
            status = f"""<blockquote><b><u>Bʀᴏᴀᴅᴄᴀsᴛ ʜᴀs ʙᴇᴇɴ Cᴏᴍᴘʟᴇᴛᴇᴅ!!!</u></b></blockquote>
    <blockquote expandable><b>Tᴏᴛᴀʟ Usᴇʀs :</b> <code>{total}</code>
    <b>Sᴜᴄᴄᴇssғᴜʟ :</b> <code>{successful}</code>
    <b>Bʟᴏᴄᴋᴇᴅ :</b> <code>{blocked}</code>
    <b>Dᴇʟᴇᴛᴇᴅ :</b> <code>{deleted}</code>
    <b>Uɴsᴜᴄᴄᴇssғᴜʟ :</b> <code>{unsuccessful}</code><blockquote>"""
    
            return await pls_wait.edit(status)
    
        else:
            msg = await message.reply(f"**Usᴇ Tʜɪs Cᴏᴍᴍᴀɴᴅ As A Rᴇᴘʟʏ Tᴏ Aɴʏ Tᴇʟᴇɢʀᴀᴍ Mᴇssᴀɢᴇ Wɪᴛʜᴏᴜᴛ Aɴʏ Sᴘᴀᴄᴇs.**")
            await asyncio.sleep(4)
            await msg.delete()
    
