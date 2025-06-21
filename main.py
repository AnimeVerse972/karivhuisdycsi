from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os
import logging
import json
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keep_alive import keep_alive

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # Obuna uchun kanal

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

keep_alive()

# ✅ Adminlar
ADMINS = [6486825926, 7575041003]

# 📁 Kodlar bilan ishlash
def load_codes():
    with open("anime_posts.json", "r") as f:
        return json.load(f)

def save_codes(codes):
    with open("anime_posts.json", "w") as f:
        json.dump(codes, f, indent=2)

# 📁 Foydalanuvchilar bilan ishlash
def save_user(user_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w") as f:
            json.dump(users, f)

# 🔄 Kodlar ro'yxatini yuklash
anime_posts = load_codes()

# ✅ Obuna tekshirish funksiyasi
async def is_user_subscribed(user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    save_user(message.from_user.id)

    if await is_user_subscribed(message.from_user.id):
        buttons = [[KeyboardButton(text="📢 Reklama"), KeyboardButton(text="💼 Homiylik")]]
        if message.from_user.id in ADMINS:
            buttons.append([KeyboardButton(text="🛠 Admin panel")])

        markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("✅ Obuna bor. Kodni yuboring:", reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Kanal", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"),
            InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
        )
        await message.answer("❗ Iltimos, kanalga obuna bo‘ling:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: CallbackQuery):
    if await is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.edit_text("✅ Obuna tekshirildi. Kod yuboring.")
    else:
        await callback_query.answer("❗ Hali ham obuna emassiz!", show_alert=True)

# 📢 Reklama
@dp.message_handler(lambda m: m.text == "📢 Reklama")
async def reklama_handler(message: types.Message):
    await message.answer("Reklama uchun: @DiyorbekPTMA")

# 💼 Homiylik
@dp.message_handler(lambda m: m.text == "💼 Homiylik")
async def homiy_handler(message: types.Message):
    await message.answer("Homiylik uchun karta: `8800904257677885`")

# 🛠 Admin panel
@dp.message_handler(lambda m: m.text == "🛠 Admin panel")
async def admin_handler(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("👮‍♂️ Admin paneliga xush kelibsiz!")
    else:
        await message.answer("⛔ Siz admin emassiz!")

# 🔐 Kod qo‘shish (admin uchun)
@dp.message_handler(lambda msg: msg.text.startswith("add "))
async def add_code(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")

    try:
        _, code, msg_id = message.text.split()
        anime_posts = load_codes()
        anime_posts[code] = {"channel": CHANNEL_USERNAME, "message_id": int(msg_id)}
        save_codes(anime_posts)
        await message.answer(f"✅ Kod {code} qo‘shildi. ID: {msg_id}")
    except:
        await message.answer("❗ Xatolik! Format: `add 47 123`")

# 👥 Foydalanuvchilar sonini ko‘rsatish (admin uchun)
@dp.message_handler(commands=["users"])
async def user_count(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")

    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        await message.answer(f"👥 Foydalanuvchilar soni: {len(users)} ta")
    except:
        await message.answer("❗ Ma'lumotlar mavjud emas.")

# 🔢 Kod orqali post chiqarish
@dp.message_handler(lambda msg: msg.text.strip().isdigit())
async def handle_code(message: types.Message):
    code = message.text.strip()

    if not await is_user_subscribed(message.from_user.id):
        await message.answer("❗ Koddan foydalanish uchun avval kanalga obuna bo‘ling.")
        return

    anime_posts = load_codes()
    if code in anime_posts:
        info = anime_posts[code]
        channel = info["channel"]
        msg_id = info["message_id"]

        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=channel,
            message_id=msg_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="📥 Yuklab olish", url=f"https://t.me/{channel.strip('@')}/{msg_id}")
            )
        )
    else:
        await message.answer("❌ Bunday kod topilmadi. Iltimos, to‘g‘ri kod yuboring.")

# 🟢 Ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
