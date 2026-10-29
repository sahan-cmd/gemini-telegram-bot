import os
import json
from http.server import BaseHTTPRequestHandler
import telebot
from google import genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update_dict = json.loads(post_data.decode('utf-8'))

            update = telebot.types.Update.de_json(update_dict)

            if update.message and update.message.text:
                chat_id = update.message.chat.id
                user_text = update.message.text

                if user_text == "/start":
                    bot.send_message(chat_id, "මම ඔබේ Gemini AI සහයකයා! මගෙන් ඕනෑම දෙයක් අහන්න. 😊")
                else:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=user_text
                    )
                    bot.send_message(chat_id, response.text)
        except Exception as e:
            pass

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is alive!')
                
