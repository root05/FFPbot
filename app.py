import os
import requests
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# Получаем и проверяем значения из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
# Исправляем определение PORT, добавляя проверку на некорректные данные
PORT = int(os.getenv("PORT", "8080"))  # По умолчанию 8080, если PORT не задан или некорректен

print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"CHANNEL_ID: {CHANNEL_ID}")
print(f"RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME}")
print(f"PORT: {PORT}")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN или CHANNEL_ID не установлены в переменных окружения")

# Базовый URL Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Функция для отправки сообщений в Telegram
def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Сообщение отправлено пользователю {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки сообщения: {e}")

# Функция для отправки фото в Telegram
def send_photo(chat_id, photo_url, caption, reply_markup=None):
    url = f"{TELEGRAM_API_URL}sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Фото отправлено пользователю {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки фото: {e}")

# Функция для редактирования сообщения в Telegram
def edit_message_caption(chat_id, message_id, caption, reply_markup=None):
    url = f"{TELEGRAM_API_URL}editMessageCaption"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Сообщение обновлено для пользователя {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка редактирования сообщения: {e}")

# Функция проверки подписки
def check_subscription(user_id):
    url = f"{TELEGRAM_API_URL}getChatMember"
    payload = {
        "chat_id": CHANNEL_ID,
        "user_id": user_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        member_status = response.json()['result']['status']
        print(f"Проверка подписки для user_id {user_id}: {member_status}")
        return member_status in ["member", "administrator", "creator"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# Создание клавиатуры с кнопками
def get_subscription_keyboard():
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Подписаться", "url": f"https://t.me/{CHANNEL_ID[1:]}"},
                {"text": "Уже подписан", "callback_data": "check_subscription"}
            ]
        ]
    }
    return keyboard

# Создание клавиатуры с кнопкой "Купить билет"
def get_ticket_keyboard():
    keyboard = {
        "inline_keyboard": [
            [{"text": "Купить билет", "url": "https://hardline-dnb.ru/"}]
        ]
    }
    return keyboard

# Обработка вебхука (GET для UptimeRobot и проверки, POST для Telegram)
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Простая HTML-страница для UptimeRobot и проверки
        html = """
        <html>
            <head><title>Friendly Fire Promo Bot</title></head>
            <body>
                <h1>Friendly Fire Promo Bot is running!</h1>
                <p>Webhook is active and ready to receive updates from Telegram.</p>
                <p>Status: OK</p>
            </body>
        </html>
        """
        return html, 200

    try:
        update = request.get_json()
        print(f"Получен вебхук: {json.dumps(update, indent=2)}")

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']

            if 'text' in message and message['text'] == '/start':
                image_url = "https://sun9-28.userapi.com/s/v1/ig2/uPvIzj3U5U2z-7jS8SwawDLX1hkvF7SgzN3VcMy-0_TvQnvUYoywgVRWk1rCgNTGGTxXNxMIDxFXGVGkb14CgxgJ.jpg?quality=95&as=32x32,48x48,72x72,108x108,160x160,240x240,360x360,480x480,540x540,640x640,720x720,1080x1080,1280x1280,1301x1301&from=bu&u=eG0S4Pm-U5esBh_oRE8MwlhlXhV2kDKgO9a8FWI_xqU&cs=1301x1301"
                caption = "Привет! Это Friendly Fire Promo!\nПодпишись на наш канал, чтобы быть в курсе новых вечеринок и получить свою скидку."
                send_photo(chat_id, image_url, caption, reply_markup=get_subscription_keyboard())

        elif 'callback_query' in update:
            callback_query = update['callback_query']
            user_id = callback_query['from']['id']
            message_id = callback_query['message']['message_id']
            chat_id = callback_query['message']['chat']['id']

            if callback_query['data'] == "check_subscription":
                if check_subscription(user_id):
                    edit_message_caption(chat_id, message_id, "Поздравляем! Вы подписаны на наши обновления,\nмы хотим отблагодарить вас промокодом на наши мероприятия!\nПромокод: JUNGLEISMASSIVE действует только при покупке билетов онлайн.", reply_markup=get_ticket_keyboard())
                else:
                    edit_message_caption(chat_id, message_id, "К сожалению, вы всё ещё не подписаны на наш канал.", reply_markup=get_subscription_keyboard())

        return jsonify({"status": "OK"}), 200
    except Exception as e:
        print(f"Ошибка в вебхуке: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500

# Маршрут для корневого URL
@app.route('/', methods=['GET'])
def home():
    print("Получен GET-запрос к /")
    return "Friendly Fire Promo Bot is running!", 200

# Установка вебхука перед запуском (для Render)
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname:
    try:
        webhook_url = f"https://{render_hostname}/webhook"
        response = requests.post(f"{TELEGRAM_API_URL}setWebhook", json={"url": webhook_url})
        response.raise_for_status()
        print(f"Вебхук установлен: {webhook_url}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка установки вебхука: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
