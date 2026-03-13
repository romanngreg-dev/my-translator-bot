from flask import Flask, request
import telebot
from deep_translator import GoogleTranslator
import os

TOKEN = '8706205011:AAE6Jd3slh3dFRRS3rcwsalpBB28EebBB50'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Инициализация переводчика
translator = GoogleTranslator()

def handle_message_text(text):
    # Определяем язык исходного текста
    detected_lang = GoogleTranslator().detect(text)
    if detected_lang == 'ru':
        # Русский -> Английский
        translated = GoogleTranslator(source='ru', target='en').translate(text)
        return f"🌍 **Перевод (английский):**\n\n{translated}"
    else:
        # Иначе -> Русский (если английский или другой)
        translated = GoogleTranslator(source='auto', target='ru').translate(text)
        return f"🌍 **Перевод (русский):**\n\n{translated}"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/health')
def health():
    return 'OK', 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Привет! Я бот-переводчик. Просто отправь мне текст.")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    try:
        response = handle_message_text(message.text)
        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка перевода: {str(e)}")

if __name__ == '__main__':
    import time
    # Удаляем старый вебхук и устанавливаем новый
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f'https://{os.environ.get("RENDER_EXTERNAL_HOSTNAME")}/{TOKEN}')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
