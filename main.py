# (c) @AbirHasan2005
# Edit By @pikyus1 SendiAp

import random
import aiohttp
import asyncio
from configs import Config
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from helpers.markup_maker import MakeCaptchaMarkup
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, ChatPermissions

CaptchaBot = Client(
    session_name=Config.SESSION_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)
CaptchaDB = {}


@CaptchaBot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    await message.reply(
        text=f"**Haii!!{message.chat.first_name}!**\n\n😍 **Saya Adalah Bot Captcha Emoji Yang Canggih**.\n\n**Saya akan meminta Anggota Grup baru untuk memverifikasi mereka dengan memecahkan captcha emoji.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ➕', url='https://t.me/CaptchaEmojiBot?startgroup=true')
                ],
                [
                    InlineKeyboardButton('🌹 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🌹', url='https://t.me/fckyoupeople1')
                ]
            ]
        )
    )

@CaptchaBot.on_chat_member_updated()
async def welcome_handler(bot: Client, event: Message):
    if (event.chat.id != Config.GROUP_CHAT_ID) or (event.from_user.is_bot is True):
        return
    try:
        user_ = await bot.get_chat_member(event.chat.id, event.from_user.id)
        if (user_.is_member is False) and (CaptchaDB.get(event.from_user.id, None) is not None):
            try:
                await bot.delete_messages(
                    chat_id=event.chat.id,
                    message_ids=CaptchaDB[event.from_user.id]["message_id"]
                )
            except:
                pass
            return
        elif (user_.is_member is False) and (CaptchaDB.get(event.from_user.id, None) is None):
            return
    except UserNotParticipant:
        return
    try:
        if CaptchaDB.get(event.from_user.id, None) is not None:
            try:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text=f"{event.from_user.mention} lagi bergabung dengan grup tanpa memverifikasi!\n\n"
                         f"Dia bisa mencoba lagi setelah 10 Menit.",
                    disable_web_page_preview=True
                )
                await bot.restrict_chat_member(
                    chat_id=event.chat.id,
                    user_id=event.from_user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                await bot.delete_messages(chat_id=event.chat.id,
                                          message_ids=CaptchaDB[event.from_user.id]["message_id"])
            except:
                pass
            await asyncio.sleep(600)
            del CaptchaDB[event.from_user.id]
        else:
            await bot.restrict_chat_member(
                chat_id=event.chat.id,
                user_id=event.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await bot.send_message(
                chat_id=event.chat.id,
                text=f"{event.from_user.mention}, untuk mengobrol di sini, harap verifikasi bahwa Anda bukan robot",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ᴋʟɪᴋ ᴅɪꜱɪɴɪ", callback_data=f"startVerify_{str(event.from_user.id)}")]
                ])
            )
    except:
        pass


@CaptchaBot.on_callback_query()
async def buttons_handlers(bot: Client, cb: CallbackQuery):
    if cb.data.startswith("startVerify_"):
        __user = cb.data.split("_", 1)[-1]
        if cb.from_user.id != int(__user):
            await cb.answer("Pesan Ini Bukan Untuk Anda!", show_alert=True)
            return
        await cb.message.edit("Menghasilkan Captcha...")
        print("Mengambil Data JSON Captcha ...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.abirhasan.wtf/captcha?token={Config.CAPTCHA_API_TOKEN}") as res:
                if res.status != 200:
                    try:
                        UserOnChat = await bot.get_chat_member(user_id=cb.from_user.id, chat_id=cb.message.chat.id)
                        if UserOnChat.restricted_by.id == (await bot.get_me()).id:
                            await bot.unban_chat_member(chat_id=cb.message.chat.id, user_id=cb.from_user.id)
                    except:
                        pass
                    await cb.message.edit("Tidak bisa mendapatkan Captcha!")
                    return
                data = await res.json()
                print("Done!")
                markup = [[], [], []]
                __emojis = data["CaptchaAnswer"].split(": ", 1)[-1].split()
                print(__emojis)
                _emojis = ['🐻', '🐔', '☁️', '🔮', '🌀', '🌚', '💎', '🐶', '🍩', '🌏', '🐸', '🌕', '🍏', '🐵', '🌙',
                           '🐧', '🍎', '😀', '🐍', '❄️', '🐚', '🐢', '🌝', '🍺', '🍔', '🍒', '🍫', '🍡', '🌑', '🍟',
                           '☕️', '🍑', '🍷', '🍧', '🍕', '🍵', '🐋', '🐱', '💄', '👠', '💰', '💸', '🎹', '📦', '📍',
                           '🐊', '🦕', '🐬', '💋', '🦎', '🦈', '🦷', '🦖', '🐠', '🐟']
                print("Cleaning Answer Emojis from Emojis List ...")
                for a in range(len(__emojis)):
                    if __emojis[a] in _emojis:
                        _emojis.remove(__emojis[a])
                show = __emojis
                print("Menambahkan Daftar Emoji Baru ...")
                for b in range(9):
                    show.append(_emojis[b])
                print("Randomizing ...")
                random.shuffle(show)
                count = 0
                print("Appending to ROW - 1")
                for _ in range(5):
                    markup[0].append(InlineKeyboardButton(f"{show[count]}",
                                                          callback_data=f"verify_{str(cb.from_user.id)}_{show[count]}"))
                    count += 1
                print("Appending to ROW - 2")
                for _ in range(5):
                    markup[1].append(InlineKeyboardButton(f"{show[count]}",
                                                          callback_data=f"verify_{str(cb.from_user.id)}_{show[count]}"))
                    count += 1
                print("Appending to ROW - 3")
                for _ in range(5):
                    markup[2].append(InlineKeyboardButton(f"{show[count]}",
                                                          callback_data=f"verify_{str(cb.from_user.id)}_{show[count]}"))
                    count += 1
                print("Setting Up in Database ...")
                CaptchaDB[cb.from_user.id] = {
                    "emojis": data["CaptchaAnswer"].split(": ", 1)[-1].split(),
                    "mistakes": 0,
                    "group_id": cb.message.chat.id,
                    "message_id": None
                }
                print("Sending Captcha ...")
                __message = await bot.send_photo(
                    chat_id=cb.message.chat.id,
                    photo=data["DownloadURL"],
                    caption=f"{cb.from_user.mention}, pilih semua emoji yang dapat Anda lihat di gambar."
                            f"Anda hanya diperbolehkan (3) kesalahan.",
                    reply_markup=InlineKeyboardMarkup(markup)
                )
                CaptchaDB[cb.from_user.id]["message_id"] = __message.message_id
                await cb.message.delete(revoke=True)

    elif cb.data.startswith("verify_"):
        __emoji = cb.data.rsplit("_", 1)[-1]
        __user = cb.data.split("_")[1]
        if cb.from_user.id != int(__user):
            await cb.answer("Pesan Ini Bukan Untuk Anda!", show_alert=True)
            return
        if cb.from_user.id not in CaptchaDB:
            await cb.answer("Coba Lagi Setelah Bergabung Kembali!", show_alert=True)
        if __emoji not in CaptchaDB.get(cb.from_user.id).get("emojis"):
            CaptchaDB[cb.from_user.id]["mistakes"] += 1
            await cb.answer("Anda salah menekan emoji!", show_alert=True)
            n = 3 - CaptchaDB[cb.from_user.id]['mistakes']
            if n == 0:
                await cb.message.edit_caption(f"{cb.from_user.mention}, you failed to solve the captcha!\n\n"
                                              f"You can try again after 10 minutes.",
                                              reply_markup=None)
                await asyncio.sleep(600)
                del CaptchaDB[cb.from_user.id]
                return
            markup = await MakeCaptchaMarkup(cb.message["reply_markup"]["inline_keyboard"], __emoji, "❌")
            await cb.message.edit_caption(
                caption=f"{cb.from_user.mention}, pilih semua emoji yang dapat Anda lihat di gambar."
                        f"Anda hanya diperbolehkan ({n}) mistakes.",
                reply_markup=InlineKeyboardMarkup(markup)
            )
            return
        else:
            CaptchaDB.get(cb.from_user.id).get("emojis").remove(__emoji)
            markup = await MakeCaptchaMarkup(cb.message["reply_markup"]["inline_keyboard"], __emoji, "✅")
            await cb.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(markup))
            if not CaptchaDB.get(cb.from_user.id).get("emojis"):
                await cb.answer("Anda Melewati Captcha!", show_alert=True)
                del CaptchaDB[cb.from_user.id]
                try:
                    UserOnChat = await bot.get_chat_member(user_id=cb.from_user.id, chat_id=cb.message.chat.id)
                    if UserOnChat.restricted_by.id == (await bot.get_me()).id:
                        await bot.unban_chat_member(chat_id=cb.message.chat.id, user_id=cb.from_user.id)
                except:
                    pass
                await cb.message.delete(True)
            await cb.answer()


CaptchaBot.run()
