from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b><blockquote>○ ᴏᴡɴᴇʀ : <a href='tg://user?id={OWNER_ID}'>DARKXSIDE78</a>\n○ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ : <a href='https://t.me/GenAnimeOfc'>Gᴇɴ Aɴɪᴍᴇ</a>\n○ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ : <a href='https://t.me/Genanimeofcchat'>Gᴇɴ Cʜᴀᴛ</a>\n○ Oɴɢᴏɪɴɢ : <a href='https://t.me/GenAnimeOngoing'>Gᴇɴ Aɴɪᴍᴇ Oɴɢᴏɪɴɢ</a>\n○ ʜɪɴᴅɪ ᴀɴɪᴍᴇ : <a href='https://t.me/Crunchyroll_Anime_India'>Cʀᴜɴᴄʜʏʀᴏʟʟ Aɴɪᴍᴇ Iɴᴅɪᴀ</a></blockquote></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton('🍁 ʙᴀᴄᴋ', callback_data = "back"),
                    InlineKeyboardButton("⚡️ ᴄʟᴏsᴇ", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "back":
        await query.message.edit_reply_markup(
            text = f"<blockquote>ʙᴀᴋᴋᴀᴀᴀ!!! {mention}\n\nɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</blockquote>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⚡️ ᴍᴀɪɴ ʜᴜʙ", url= "https://t.me/genanimeofc"),
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
