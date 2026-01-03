import telebot
import requests
import uuid
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# --- CONFIGURATION (In 7 Lines Ko Edit Karein) ---
API_TOKEN = '8543013467:AAGcpyMVcTgKCg5eKn5gBX2u4I8qZHiWdhU'      # BotFather wala token
GPLINKS_API = ' eb68eb5b11a608931184c9ed2ac1d22b2bbdf3a3'  # GPLinks Dashboard se
OMDB_API_KEY = '60c05c55'    # OMDb se mili 8-digit key
MONGO_URL = ' mongodb+srv://manmitkumar20095_db_user:Manmit1234@cluster0.nbklxej.mongodb.net/?appName=Cluster0' # Password ke sath wala link
BOT_USERNAME = 'mkgivelink_bot'              # Bot ka username (bina @ ke)
CHANNEL_ID = '@Latest movies'           # Channel ka username (@ ke sath)
ADMIN_ID =   7352169748                   # Aapki Numeric ID (@userinfobot se lein)

bot = telebot.TeleBot(API_TOKEN)
db = MongoClient(MONGO_URL)['movie_db']['links']
user_temp_data = {}

# 1. START HANDLER: User ads ke baad yahan aayega
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) > 1:
        movie_id = args[1]
        data = db.find_one({"movie_id": movie_id})
        if data:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎬 Watch/Download Now", url=data['original_link']))
            bot.send_message(chat_id, "✅ **Link Unlocked!**\n\nMovie dekhne ke liye niche click karein:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "❌ Link expire ho chuka hai.")
    else:
        bot.send_message(chat_id, "Welcome! /post se movie post banayein.")

# 2. POST CREATION: Admin flow
@bot.message_handler(commands=['post'], func=lambda m: m.from_user.id == ADMIN_ID)
def start_post(message):
    msg = bot.reply_to(message, "🎬 **Movie ka naam** likhiye:")
    bot.register_next_step_handler(msg, get_movie_details)

def get_movie_details(message):
    name = message.text
    data = requests.get(f"http://www.omdbapi.com/?t={name}&apikey={OMDB_API_KEY}").json()
    if data.get('Response') == 'False':
        bot.send_message(message.chat.id, "❌ Movie nahi mili! Phir se /post karein.")
        return

    user_temp_data[message.chat.id] = {
        'title': data.get('Title'), 'rating': data.get('imdbRating'),
        'poster': data.get('Poster'), 'genre': data.get('Genre'), 'year': data.get('Year')
    }
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Yes ✅", callback_data="cens_Yes"), 
               InlineKeyboardButton("No ❌", callback_data="cens_No"))
    bot.send_message(message.chat.id, "🔞 Kya movie **Censored** hai?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cens_'))
def handle_censored(call):
    censored_status = call.data.split('_')[1]
    user_temp_data[call.message.chat.id]['censored'] = censored_status
    bot.edit_message_text("🔗 Ab movie ka **TeraBox Link** bhejiye:", call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, finalize_post)

def finalize_post(message):
    chat_id = message.chat.id
    original_link = message.text
    details = user_temp_data[chat_id]
    
    markup = InlineKeyboardMarkup(row_width=2)
    qualities = ["480p", "720p", "1080p"]
    
    for q in qualities:
        m_id = str(uuid.uuid4())[:8]
        db.insert_one({"movie_id": m_id, "original_link": original_link})
        
        bot_url = f"https://t.me/{BOT_USERNAME}?start={m_id}"
        res = requests.get(f"https://gplinks.in/api?api={GPLINKS_API}&url={bot_url}").json()
        short_url = res.get('shortenedUrl', bot_url)
        markup.add(InlineKeyboardButton(f"📥 Download {q}", url=short_url))

    caption = (
        f"🎬 **Movie:** {details['title']} ({details['year']})\n"
        f"⭐ **IMDb:** {details['rating']}/10\n"
        f"🎭 **Genre:** {details['genre']}\n"
        f"🔞 **Censored:** {details['censored']}\n"
        f"💿 **Qualities:** 480p, 720p, 1080p\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 *Join {CHANNEL_ID} for more!*"
    )

    if details['poster'] != "N/A":
        bot.send_photo(CHANNEL_ID, details['poster'], caption=caption, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(CHANNEL_ID, caption, reply_markup=markup, parse_mode="Markdown")

    bot.send_message(chat_id, "✅ **Post Successfully uploaded to Channel!**")
    del user_temp_data[chat_id]

import os; from threading import Thread; from flask import Flask; app = Flask(''); @app.route('/')\ndef home(): return "I am alive";\ndef run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)));\nThread(target=run).start()
bot.infinity_polling()
