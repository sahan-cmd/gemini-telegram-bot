import os
import threading
from flask import Flask
import telebot
from google import genai

# Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Render එක Free run වෙන්න අවශ්‍ය Dummy Web Server එක
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Telegram Message Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "මම ඔබේ Gemini AI සහයකයා! මගෙන් ඕනෑම දෙයක් අහන්න. 😊")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "කණගාටුයි, පිළිතුර ලබාගැනීමේදී දෝෂයක් සිදු වුණා.")

# Thread එකක් මගින් Web Server එක සහ Bot දෙකම එකවර Run කිරීම
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
