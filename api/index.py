import os
import json
from http.server import BaseHTTPRequestHandler
import telebot
from groq import Groq

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update_dict = json.loads(post_data.decode('utf-8'))
            update = telebot.types.Update.de_json(update_dict)

            if update and update.message and update.message.text:
                chat_id = update.message.chat.id
                user_text = update.message.text

                if user_text.strip() == "/start":
                    bot.send_message(chat_id, "මම ඔබේ AI සහයකයා! මගෙන් ඕනෑම දෙයක් අහන්න. 😊")
                else:
                    bot.send_chat_action(chat_id, 'typing')

                    try:
                        # Groq මගින් ඉතා වේගවත්ව පිළිතුරු සැපයීම (Llama 3.3 70B)
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful and friendly AI assistant. Always respond fluently in Sinhala if the user speaks Sinhala."
                                },
                                {
                                    "role": "user",
                                    "content": user_text
                                }
                            ]
                        )
                        reply_text = completion.choices[0].message.content
                        bot.send_message(chat_id, reply_text)

                    except Exception as ai_err:
                        bot.send_message(chat_id, f"⚠️ Error: {str(ai_err)[:300]}")

        except Exception as main_err:
            print(f"Server Error: {main_err}")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running with Groq!')
