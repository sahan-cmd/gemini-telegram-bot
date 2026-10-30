import os
import json
from http.server import BaseHTTPRequestHandler
import telebot
from google import genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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
                    bot.send_message(chat_id, "මම ඔබේ Gemini AI සහයකයා! මගෙන් ඕනෑම දෙයක් අහන්න. 😊")
                else:
                    bot.send_chat_action(chat_id, 'typing')

                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=user_text
                        )
                        bot.send_message(chat_id, response.text)
                    except Exception as err:
                        bot.send_message(chat_id, f"⚠️ Error: {str(err)}")

        except Exception as e:
            pass

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
