from flask import Flask, request
import telebot
from deep_translator import GoogleTranslator
import os
import time
from langdetect import detect  # добавим определение языка

TOKEN = '8706205011:AAE6Jd3slh3dFRRS3rcwsalpBB28EebBB50'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Инициализация переводчиков
translator_ru_en = GoogleTranslator(source='ru', target='en')
translator_en_ru = GoogleTranslator(source='en', target='ru')

def handle_message_text(text):
    # Определяем язык с помощью langdetect
    try:
        lang = detect(text)
    except:
        lang = 'en'  # если не удалось определить, считаем английским
    
    if lang == 'ru':
        translated = translator_ru_en.translate(text)
        return f"🌍 **Перевод (английский):**\n\n{translated}"
    else:
        translated = translator_en_ru.translate(text)
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
    bot.reply_to(message, 
        "👋 Привет! Я бот-переводчик.\n"
        "Просто отправь мне текст, и я переведу его с русского на английский или наоборот."
    )

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    try:
        response = handle_message_text(message.text)
        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка перевода: {e}")

# *** ВАЖНО: устанавливаем вебхук при старте (вне if __name__) ***
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")

if __name__ == '__main__':
    # Запуск Flask-приложения (gunicorn не заходит сюда)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
