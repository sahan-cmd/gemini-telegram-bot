import os
import json
import logging
from http.server import BaseHTTPRequestHandler
import telebot
from google import genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

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
                        response = client.interactions.create(
                            model=GEMINI_MODEL,
                            input=user_text,
                            system_instruction=(
                                "You are a helpful and friendly AI assistant. "
                                "Always respond fluently in Sinhala if the user speaks Sinhala."
                            ),
                            store=False,
                        )
                        reply_text = response.output_text or "Gemini වෙතින් පිළිතුරක් ලැබුණේ නැහැ."
                        bot.send_message(chat_id, reply_text)

                    except Exception:
                        logging.exception("Gemini request failed")
                        bot.send_message(
                            chat_id,
                            "⚠️ Gemini වෙත සම්බන්ධ වීමේ ගැටලුවක් ඇති වුණා. ටිකකින් නැවත උත්සාහ කරන්න.",
                        )

        except Exception as main_err:
            logging.exception("Webhook request failed: %s", main_err)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running with Gemini!')
