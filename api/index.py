import os
import json
from http.server import BaseHTTPRequestHandler
import telebot
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_gemini_reply(prompt_text):
    # 1. ඔබගේ API Key එකට සහය දක්වන models list එක ලබා ගැනීම
    available_models = []
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            available_models.append(m.name)

    if not available_models:
        return "⚠️ කිසිදු Generation Model එකක් ඔබගේ API Key එකට හමු නොවීය."

    # 2. වඩාත් සුදුසු model එක තෝරා ගැනීම (පළමු ප්‍රමුඛතාවය flash/pro වෙත)
    chosen_model = None
    for name in available_models:
        if "flash" in name.lower() or "pro" in name.lower():
            chosen_model = name
            break
            
    if not chosen_model:
        chosen_model = available_models[0]

    # 3. පිළිතුර ලබා ගැනීම
    model = genai.GenerativeModel(chosen_model)
    response = model.generate_content(prompt_text)
    return response.text

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
                        reply = get_gemini_reply(user_text)
                        bot.send_message(chat_id, reply)
                    except Exception as gemini_err:
                        bot.send_message(chat_id, f"⚠️ Error: {str(gemini_err)}")

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
