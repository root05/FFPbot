import os
import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Объявляем константы в начале кода
PROMO_CODE = "JUNGLEISMASSIVE"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

# Проверка и установка порта
port_value = os.getenv("PORT")
if port_value == "os.getenv(\"PORT\")" or not port_value:
    PORT = 8080
else:
    PORT = int(port_value)

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
def send_photo(chat_id, photo_url, caption, reply_markup=None, parse_mode=None):
    url = f"{TELEGRAM_API_URL}sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Фото отправлено пользователю {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки фото: {e}")

# Функция для редактирования сообщения в Telegram
def edit_message_caption(chat_id, message_id, caption, reply_markup=None, parse_mode=None):
    url = f"{TELEGRAM_API_URL}editMessageCaption"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if parse_mode:
        payload["parse_mode"] = parse_mode
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

# Клавиатура для подписки
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

# Клавиатура только с покупкой билета
def get_ticket_keyboard():
    keyboard = {
        "inline_keyboard": [
            [{"text": "Купить билет", "url": "https://hardline-dnb.ru"}]
        ]
    }
    return keyboard

# Обработка вебхука
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(f"Получен GET-запрос к /webhook от {request.remote_addr}")
        return "Webhook is active and ready. Status: OK", 200, {'Content-Type': 'text/plain'}

    try:
        update = request.get_json()
        print(f"Получен вебхук: {json.dumps(update, indent=2)}")

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']

            if 'text' in message and message['text'] == '/start':
                image_url = "https://sun9-28.userapi.com/s/v1/ig2/uPvIzj3U5U2z-7jS8SwawDLX1hkvF7SgzN3VcMy-0_TvQnvUYoywgVRWk1rCgNTGGTxXNxMIDxFXGVGkb14CgxgJ.jpg?quality=95&as=32x32,48x48,72x72,108x108,160x160,240x240,360x360,480x480,540x540,640x640,720x720,1080x1080,1280x1280,1301x1301&from=bu&u=eG0S4Pm-U5esBh_oRE8MwlhlXhV2kDKgO9a8FWI_xqU&cs=1301x1301"
                caption = "Привет! \nЭто Friendly Fire Promo!\nПодпишись на наш канал, чтобы получить свою скидку и быть в курсе новых вечеринок."
                send_photo(chat_id, image_url, caption, reply_markup=get_subscription_keyboard())

        elif 'callback_query' in update:
            callback_query = update['callback_query']
            user_id = callback_query['from']['id']
            message_id = callback_query['message']['message_id']
            chat_id = callback_query['message']['chat']['id']
            callback_data = callback_query['data']

            if callback_data == "check_subscription":
                if check_subscription(user_id):
                    # Используем Markdown для выделения промокода
                    caption = f"Поздравляем! \nТы подписан на наши обновления и мы хотим отблагодарить тебя промокодом на наши мероприятия: `{PROMO_CODE}`\nДействует только при покупке билетов онлайн."
                    edit_message_caption(chat_id, message_id, caption, reply_markup=get_ticket_keyboard(), parse_mode="Markdown")
                else:
                    edit_message_caption(chat_id, message_id, 
                        "К сожалению, ты всё ещё не подписан на наш канал.", 
                        reply_markup=get_subscription_keyboard())

        return jsonify({"status": "OK"}), 200
    except Exception as e:
        print(f"Ошибка в вебхуке: {str(e)}")
        return jsonify({"status": "Error", "message": str(e)}), 500

# Корневой маршрут для UptimeRobot
@app.route('/', methods=['GET'])
def home():
    print(f"Получен GET-запрос к / от {request.remote_addr}")
    return "Friendly Fire Promo Bot is running!", 200, {'Content-Type': 'text/plain'}

# Установка вебхука
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
