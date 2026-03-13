from flask import Flask, request
import telebot
from googletrans import Translator
import os

TOKEN = '8706205011:AAE6Jd3slh3dFRRS3rcwsalpBB28EebBB50'
bot = telebot.TeleBot(TOKEN, threaded=False)
translator = Translator()
app = Flask(__name__)

# Функция для обработки сообщений (та же логика)
def handle_message_text(text):
    detected = translator.detect(text)
    if detected.lang == 'ru':
        result = translator.translate(text, dest='en')
        return f"🌍 **Перевод (английский):**\n\n{result.text}"
    else:
        result = translator.translate(text, dest='ru')
        return f"🌍 **Перевод (русский):**\n\n{result.text}"

# Обработчик вебхуков
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

# Простой эндпоинт для проверки работы
@app.route('/')
def index():
    return 'Бот работает!'

# Эндпоинт для пингера (чтобы бот не засыпал)
@app.route('/health')
def health():
    return 'OK', 200

# Обработчик сообщений (такой же, как в предыдущей версии)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Привет! Я бот-переводчик. Просто отправь мне текст.")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    try:
        response = handle_message_text(message.text)
        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка перевода")

if __name__ == '__main__':
    # Для локального тестирования
    bot.remove_webhook()
    bot.set_webhook(url=f'https://ВАШ_ПРОЕКТ.onrender.com/{TOKEN}')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))