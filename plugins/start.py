import os, asyncio, humanize, logging
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired
from bot import Bot
from config import *
from database.database import *
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from helper_func import encode, decode, get_messages
from pyrogram.enums import ChatMemberStatus

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = Client("fsubbot", api_id=APP_ID, api_hash=API_HASH, bot_token=TG_BOT_TOKEN)


# Function to handle file deletion
async def delete_files(messages, client, k, enter):
    auto_del = get_auto_del()
    del_timer = get_file_del_timer()
    if auto_del == True:
        await asyncio.sleep(del_timer)  # Wait for the specified duration in config.py

        for msg in messages:
            if msg and msg.chat:  # Ensure msg and chat are not None
                try:
                    await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
                except Exception as e:
                    print(f"The attempt to delete the media {getattr(msg, 'id', 'Unknown')} was unsuccessful: {e}")
            else:
                print("Encountered an empty or deleted message.")

        # Safeguard against k.command being None or having insufficient parts
        
        command = enter.split(" ")
        command_part = command[1] if len(command) > 1 else None
        
        
        if command_part:
            button_url = f"https://t.me/{client.username}?start={command_part}"
            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Gᴇᴛ Yᴏᴜʀ Fɪʟᴇ Aɢᴀɪɴ!", url=button_url)]
                ]
            )
        else:
            keyboard = None

    # Edit message with the button
    await k.edit_text(
        "<blockquote><b>Yᴏᴜʀ Vɪᴅᴇᴏ / Fɪʟᴇ Is Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</b></blockquote>",
        reply_markup=keyboard
    )


async def get_invite_link(channel_id):
    """Generate an invite link for the channel."""
    if not app.is_connected:
        await app.start()  # Ensures client is started if it isn't

    try:
        # Attempt to create a new invite link
        invite_link_obj = await app.create_chat_invite_link(chat_id=channel_id, creates_join_request=True)
        if invite_link_obj and invite_link_obj.invite_link:
            return invite_link_obj.invite_link
        logger.error(f"No invite link created for channel {channel_id}.")
        return None
    except Exception as e:
        logger.error(f"Could not create invite link for channel {channel_id}: {e}")
        return None


async def check_subscription(client, user_id):
    """Check if user is subscribed or has pending request"""
    fsubs = load_fsubs()
    statuses = {}
    
    for channel in fsubs:
        channel_id = channel['_id']
        settings = get_channel_settings(channel_id)
        
        try:
            if settings.get('is_private'):
                if settings.get('auto_accept'):
                    # Auto-approved channel
                    statuses[channel_id] = ChatMemberStatus.MEMBER
                else:
                    # Allow access if ANY request exists (approved or pending)
                    request_exists = join_requests.find_one({
                        'user_id': user_id,
                        'channel_id': channel_id,
                        'approved': {'$ne': False}  # True or not set
                    })
                    statuses[channel_id] = ChatMemberStatus.MEMBER if request_exists else ChatMemberStatus.BANNED
            else:
                # Public channel check
                member = await client.get_chat_member(channel_id, user_id)
                statuses[channel_id] = member.status
                
        except UserNotParticipant:
            statuses[channel_id] = ChatMemberStatus.BANNED
        except Exception as e:
            logger.error(f"Subscription check error: {e}")
            statuses[channel_id] = ChatMemberStatus.BANNED  # Fail-safe

    return statuses

def is_user_subscribed(statuses):
    """Determine if the user is subscribed based on their statuses."""
    return all(
        status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER} 
        for status in statuses.values() if status is not None
    ) and len(statuses) > 0  # Ensure at least one channel was checked

def force_sub(func):
    """Implement Force Subs using @force_sub before any command function."""
    async def wrapper(client, message):
        SPOILER = get_spoiler()
        msg = await message.reply_photo(caption="<code>Cᴏɴɴᴇᴄᴛɪɴɢ!</code>", photo="plugins/image/fsub.jpg", has_spoiler=SPOILER)
        user_id = message.from_user.id
        
        try:
            fsubs = load_fsubs()  # Load channels from database
            logger.debug(f"Loaded fsubs: {fsubs}")
            await msg.edit_text("<code>Cᴏɴɴᴇᴄᴛɪɴɢ!!</code>")
            await msg.edit_text("<code>Cᴏɴɴᴇᴄᴛɪɴɢ!!!</code>")
            logger.debug(f"Loaded spoiler: {SPOILER}")
            await msg.edit_text("<code>Cᴏɴɴᴇᴄᴛɪɴɢ!!!!</code>")
            logger.info(f"User {user_id} invoked {message.command[0]} command")
            await msg.edit_text("<code>Lᴏᴀᴅɪɴɢ!</code>")
            statuses = await check_subscription(client, user_id)
            logger.debug(f"Subscription statuses for user {user_id}: {statuses}")

            if is_user_subscribed(statuses):
                logger.debug(f"User {user_id} passed the subscription check.")
                await msg.edit_text("<code>Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Sᴛᴀᴛᴜs: Pᴀssᴇᴅ</code>")
                await msg.delete()
                await func(client, message)  # Added await
            else:
                logger.debug(f"User {user_id} failed the subscription check.")
                channels_list = []
                buttons = []
                await msg.edit_text("<code>Lᴏᴀᴅɪɴɢ!!!</code>")
                # Collect channels user is not subscribed to and prepare buttons
                for channel in fsubs:
                    channel_id = channel['_id']
                    channel_name = channel['CHANNEL_NAME']

                    if statuses.get(channel_id) in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                        t = (str(channel_name), "Jᴏɪɴᴇᴅ")
                        channels_list.append(t)
                    else:
                        t = (str(channel_name), "Nᴏᴛ Jᴏɪɴᴇᴅ")
                        channels_list.append(t)
                        link = await get_invite_link(channel_id)  # Attempt to get the invite link
                        if link:
                            buttons.append(InlineKeyboardButton(channel_name, url=link))
                        else:
                            buttons.append(InlineKeyboardButton("Eʀʀᴏʀ ᴄʀᴇᴀᴛɪɴɢ ɪɴᴠɪᴛᴇ ʟɪɴᴋ", url="https://t.me/GenAnimeOfc"))
                    
                from_link = message.text.split(" ")
                if len(from_link) > 1:
                    try_again_link = f"https://t.me/{client.username}/?start={from_link[1]}"
                    buttons.append(InlineKeyboardButton("Tʀʏ Aɢᴀɪɴ!", url=try_again_link))
                await msg.edit_text("<code>Lᴏᴀᴅɪɴɢ!!!!</code>")
                channels_message = (
                    "<blockquote><b>Cʜᴀɴɴᴇʟs Sᴛᴀᴛᴜs:</b></blockquote>\n" +
                    "\n".join(f"<b>{i+1}. {name}</b>\n<b>Sᴛᴀᴛᴜs:</b> <code>{userstatus}</code>\n" for i, (name, userstatus) in enumerate(channels_list))
                )
                logger.debug(f"Channels message: {channels_message}")

                n = 2  # Adjust number of buttons per row
                buttons = [buttons[i:i + n] for i in range(0, len(buttons), n)]
                await msg.edit_text("<code>Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Sᴛᴀᴛᴜs: Fᴀɪʟᴇᴅ</code>")
                if buttons:
                    try:
                        await msg.edit_text(
                            text=channels_message,
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                    except Exception as e:
                        logger.error(f"Error editing message with buttons: {e}")
                else:
                    logger.error("No buttons to send. Check the button generation.")
        
        except Exception as e:
            logger.error(f"Error in force_sub decorator: {e}")

    return wrapper


#Commands
@Bot.on_message(filters.command("fsubs") & filters.private)
async def fsublist(client, message):
    user_id = message.from_user.id
    admin_ids = await get_admin_ids()
    
    if user_id in admin_ids:
        fsubs = load_fsubs()
        channel_ids = [fsub['_id'] if isinstance(fsub, dict) else fsub for fsub in fsubs]
        fsublist = str(channel_ids)
        await message.reply(fsublist)

# Variable to keep track of the current operation
current_operation = {}

@Bot.on_message(filters.command("add_fsub") & filters.private)
async def start_add_fsub(client, message):
    user_id = message.from_user.id
    admin_ids = await get_admin_ids()
    
    if user_id in admin_ids:    
        # Start the process by asking for the channel ID
        await message.reply("Wʜᴀᴛ ɪs ᴛʜᴇ ID ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ?")
        
        # Set the current operation for adding a channel
        current_operation[user_id] = {"action": "add_fsub", "step": "awaiting_channel_id"}

@Bot.on_message(filters.command("rm_fsub") & filters.private)
async def start_rm_fsub(client, message):
    user_id = message.from_user.id
    admin_ids = await get_admin_ids()
    
    if user_id in admin_ids:
    
        # Start the process by asking for the channel ID to remove
        await message.reply("Wʜᴀᴛ ɪs ᴛʜᴇ ID ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ʀᴇᴍᴏᴠᴇ?")
        
        # Set the current operation for removing a channel
        current_operation[user_id] = {"action": "rm_fsub", "step": "awaiting_channel_id"}

@Bot.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    
    user_id = message.from_user.id
    admin_ids = await get_admin_ids()
    
    if user_id in admin_ids:
    
    # Check if the user is in an active operation
        if user_id in current_operation:
            # Remove the user's operation and send a cancellation message
            del current_operation[user_id]
            await message.reply("Tʜᴇ ᴏᴘᴇʀᴀᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟᴇᴅ.")
        else:
            await message.reply("Nᴏ ᴏᴘᴇʀᴀᴛɪᴏɴ ɪs ɪɴ ᴘʀᴏɢʀᴇss ᴛᴏ ᴄᴀɴᴄᴇʟ.")


@Bot.on_message(filters.private & ~filters.command(['start','users','broadcast','b_link','g_link','ping','my_id','add_sticker','spoiler','add_fsub','rm_fsub','cancel','ban','unban','banlist','s_img','del_timer','f_img','add_admin','rm_admin','auto_del','pbroadcast','sudo','fsubs']))
async def channel_post(client: Client, message: Message):
    user_id = message.from_user.id
    fsubs = load_fsubs()
    channel_ids = [fsub['_id'] for fsub in fsubs]
    admin_ids = await get_admin_ids()
    ban_ids = await get_banned_ids()
    
    if user_id in ban_ids:
        await client.send_message(chat_id=user_id, text="Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.")
    elif user_id in admin_ids:
        if user_id in current_operation:
            action = current_operation[user_id]["action"]
            step = current_operation[user_id]["step"]
            
            if action == "add_fsub":
                if step == "awaiting_channel_id":
                    try:
                        channel_id = int(message.text)
                        bot_user = await client.get_me()
                        bot_status = await client.get_chat_member(channel_id, bot_user.id)
                        
                        if bot_status.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                            current_operation[user_id].update({
                                "channel_id": channel_id,
                                "step": "awaiting_channel_name"
                            })
                            await message.reply("Nᴀᴍᴇ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ?")
                        else:
                            await message.reply("Tʜᴇ ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴅᴅ ɪᴛ ᴛᴏ ᴛʜᴇ ғsᴜʙ ʟɪsᴛ.")
                            del current_operation[user_id]
                    except ValueError:
                        await message.reply("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ ғᴏʀ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ID.")
                
                elif step == "awaiting_channel_name":
                    channel_id = current_operation[user_id]["channel_id"]
                    channel_name = message.text
                    
                    try:
                        chat = await client.get_chat(channel_id)
                        is_private = chat.has_protected_content
                    except:
                        is_private = False

                    if is_private:
                        current_operation[user_id].update({
                            "step": "set_auto_approve",
                            "channel_name": channel_name,
                            "is_private": True
                        })
                        await message.reply(
                            "Eɴᴀʙʟᴇ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ ғᴏʀ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs?",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🤖 Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ", callback_data="auto_yes"),
                                 InlineKeyboardButton("📝 Mᴀɴᴜᴀʟ Rᴇǫᴜᴇsᴛ", callback_data="auto_no")]
                            ])
                        )
                    else:
                        add_fsub(channel_id, channel_name)
                        await message.reply(f"Aᴅᴅᴇᴅ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ: {channel_name}")
                        del current_operation[user_id]

            elif action == "rm_fsub" and step == "awaiting_channel_id":
                try:
                    channel_id = int(message.text)
                    if channel_id in channel_ids:
                        del_fsub(channel_id)
                        await message.reply(f"Cʜᴀɴɴᴇʟ (ID: {channel_id}) ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ғsᴜʙ ʟɪsᴛ.")
                    else:
                        await message.reply("Tʜɪs ᴄʜᴀɴɴᴇʟ ɪs ɴᴏᴛ ɪɴ ғsᴜʙ ʟɪsᴛ.")
                    del current_operation[user_id]
                except ValueError:
                    await message.reply("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ ғᴏʀ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ID.")
        
        elif user_id in waiting_for_image:
            try:
                img_type = waiting_for_image[user_id]
                image_path = "plugins/image/start.jpg" if img_type == "start" else "plugins/image/fsub.jpg"
                
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                file_path = await client.download_media(message.photo, file_name="temp_image.jpg")
                
                if file_path:
                    os.rename(file_path, image_path)
                    await message.reply("Iᴍᴀɢᴇ sᴀᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!", quote=True)
                else:
                    await message.reply("Fᴀɪʟᴇᴅ ᴛᴏ sᴀᴠᴇ ɪᴍᴀɢᴇ. Tʀʏ ᴀɢᴀɪɴ.", quote=True)
                
                del waiting_for_image[user_id]
            except:
                await message.reply("Pʟᴇᴀsᴇ ᴜsᴇ /s_img ᴏʀ /f_img ᴄᴏᴍᴍᴀɴᴅ ғɪʀsᴛ!")
        
        else:
            reply_text = await message.reply_text("Pʟᴇᴀsᴇ Wᴀɪᴛ...!", quote=True)
            try:
                post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
                converted_id = post_message.id
                base64_string = await encode(str(converted_id))
                link = f"https://t.me/{client.username}?start=filez{base64_string}"
                
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Sʜᴀʀᴇ URL", url=f'https://telegram.me/share/url?url={link}')]])
                await reply_text.edit(f"<b>Hᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview=True)
                
                if not DISABLE_CHANNEL_BUTTON:
                    await post_message.edit_reply_markup(reply_markup)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
            except Exception as e:
                await reply_text.edit_text(f"Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ Wʀᴏɴɢ: {e}")


@Bot.on_callback_query(filters.regex(r"^auto_(yes|no)$"))
async def handle_auto_approve_choice(client, query):
    user_id = query.from_user.id
    action = query.data.split("_")[1]
    
    if user_id not in current_operation:
        await query.answer("Operation expired!")
        return
    
    data = current_operation[user_id]
    channel_id = data["channel_id"]
    channel_name = data["channel_name"]
    
    if action == "yes":
        add_fsub(
            channel_id=channel_id,
            channel_name=channel_name,
            is_private=True,
            auto_accept=True
        )
        msg = "🤖 Auto-approve enabled! Users will be approved instantly."
    else:
        add_fsub(
            channel_id=channel_id,
            channel_name=channel_name,
            is_private=True,
            auto_accept=False
        )
        msg = "📝 Manual approval enabled! Users can use bot while requests are pending."
    
    await query.edit_message_text(f"✅ {channel_name} settings saved!\n{msg}")
    del current_operation[user_id]

@Bot.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    load_settings()
    SPOILER = get_spoiler()
    auto_del = get_auto_del()
    del_timer = get_file_del_timer()
    id = message.from_user.id
    ban_ids = await get_banned_ids()
    user_id = message.from_user.id
    
    if not present_user(id):
        try:
            await add_user(id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass
    
    text = message.text
    if user_id in ban_ids:
        await client.send_message(chat_id=user_id, text="Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.")

    elif len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return
        base64_string = base64_string[5:]
        string = await decode(base64_string)
        
        argument = string.split("-")
        
        ids = []
        if len(argument) == 2:
            try:
                start = int(argument[0])
                end = int(argument[1])
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 1:
            try:
                ids = [int(argument[0])]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        temp_msg = await message.reply("<blockquote><b>Wᴀɪᴛ A Sᴇᴄ...</b></blockquote>")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ...!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        yugen_msgs = []  # List to keep track of sent messages

        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption=msg.caption.html if msg.caption else msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))


            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                yugen_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                yugen_msgs.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass
        
        
        if auto_del == True:
            enter = text
            k = await client.send_message(chat_id=message.from_user.id, 
                                      text=f'<blockquote><b><i>Tʜɪs Fɪʟᴇ ɪs ᴅᴇʟᴇᴛɪɴɢ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ɪɴ {humanize.naturaldelta(del_timer)}. Fᴏʀᴡᴀʀᴅ ɪɴ ʏᴏᴜʀ Sᴀᴠᴇᴅ Mᴇssᴀɢᴇs...!</i></b></blockquote>')

        # Schedule the file deletion
            asyncio.create_task(delete_files(yugen_msgs, client, k, enter))
            return

        
    elif id in await get_admins():
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("「Mᴀɪɴ Hᴜʙ」", url="t.me/genanimeofc"),
                ],
                [
                    InlineKeyboardButton("「Hɪɴᴅɪ Aɴɪᴍᴇ」", url="t.me/Crunchyroll_Anime_India"),
                    InlineKeyboardButton("「Mᴀɴɢᴀ」", url="t.me/Crunchyroll_Anime_India")
                ],
                [
                    InlineKeyboardButton("🛈 ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close")
                ]
            ]
        )
        
        await client.send_photo(
            chat_id=message.chat.id,
            photo="plugins/image/start.jpg",
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
                    
            ),
            has_spoiler=SPOILER,
            reply_markup=reply_markup
        )
        await asyncio.sleep(settings["stk_del_timer"])
        
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("「ᴍᴀɪɴ ʜᴜʙ」", url="t.me/genanimeofc"),
                ],
                [
                    InlineKeyboardButton("「Hɪɴᴅɪ Aɴɪᴍᴇ」", url="t.me/Crunchyroll_Anime_India"),
                    InlineKeyboardButton("「Mᴀɴɢᴀ」", url="t.me/Crunchyroll_Anime_India")
                ],
                [
                    InlineKeyboardButton("🛈 ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close")
                ]
            ]
        )
        await asyncio.sleep(settings["stk_del_timer"])
        
        
        await client.send_photo(
            chat_id=message.chat.id,
            photo="plugins/image/start.jpg",
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
                    
            ),
            has_spoiler=SPOILER,
            reply_markup=reply_markup
        )
        
        return
        
    

# Assuming ADMINS and SUDO are defined elsewhere
# Dictionary to keep track of users waiting for image input
waiting_for_image = {}

@Bot.on_message(filters.command("s_img") & filters.private)
async def change_start_img(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    
    if user_id in admin_ids:
        # Prompt the user to send a photo
        await message.reply("Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ sᴇᴛ ᴀs ᴛʜᴇ sᴛᴀʀᴛ ɪᴍᴀɢᴇ.")
        waiting_for_image[message.from_user.id] = "start"  # Mark user as waiting for start image

@Bot.on_message(filters.command("f_img") & filters.private)
async def change_force_img(client, message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    
    if user_id in admin_ids:
        # Prompt the user to send a photo
        await message.reply("Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ sᴇᴛ ᴀs ᴛʜᴇ ғᴏʀᴄᴇ ɪᴍᴀɢᴇ.")
        waiting_for_image[message.from_user.id] = "fsub"  # Mark user as waiting for force image
        
        
if __name__=='__main__':
    asyncio.run(main())
