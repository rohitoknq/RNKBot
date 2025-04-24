from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b><blockquote>○ ᴏᴡɴᴇʀ : <a href='tg://user?id={OWNER_ID}'>𝘈𝘯𝘪𝘮𝘦</a>\n○ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ : <a href='https://t.me/RNK_Anime'>𝘙𝘕𝘒 𝘈𝘕𝘐𝘔𝘌</a>\n○ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ : <a href='https://t.me/RNK_Chat'>𝘙𝘕𝘒 𝘈𝘕𝘐𝘔𝘌</a>\n○ Dᴇᴠ : <a href='https://t.me/FraxxShadow'>FʀᴀxxSʜᴀᴅᴏᴡ</a></blockquote></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton('◄ ʙᴀᴄᴋ', callback_data = "back"),
                    InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "back":
        await query.message.edit_text((
            text = f"<blockquote><b>ʙᴀᴋᴀ!!! </b><b>{mention}</b>\n<b>ɪ ᴀᴍ <a href='https://t.me/TheNamiRobot'>ɴᴀᴍɪ</a>, ᴀ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ ᴄʀᴇᴀᴛᴇᴅ ʙʏ </b><b><a href='https://t.me/AnimeMonth'>𝘈𝘯𝘪𝘮𝘦𝘔𝘰𝘯𝘵𝘩</a> ᴛᴏ ꜱʜᴀʀᴇ ᴀɴɪᴍᴇ ᴛᴏ ᴀ ʟᴀʀɢᴇ ɴᴜᴍʙᴇʀ </b><b>ᴏꜰ ꜰᴀɴꜱ ᴠɪᴀ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋꜱ...</blockquote>\n</b><blockquote><b>🇵​🇴​🇼​🇪​🇷​🇪​🇩​ 🇧​🇾​ <a href='https://t.me/RNK_Anime'>RNK Anime</a></b></blockquote>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝘙𝘕𝘒 𝘈𝘕𝘐𝘔𝘌", url= "https://t.me/RNK_ANIME"),
                    ],
                    [
                        InlineKeyboardButton("🛈 ᴀʙᴏᴜᴛ", callback_data = "about"),
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
