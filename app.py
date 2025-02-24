import requests
import json
import time

# Жёстко задаём константы внутри кода
BOT_TOKEN = "7874282672:AAHomA_qWkMnY5VJAZAEwlkVM0uIvVDb8jM"
CHANNEL_ID = "-1001823318732"  # Числовой ID канала
PROMO_CODE = "JUNGLEISMASSIVE"

# Базовый URL Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Функция для отправки сообщений в Telegram
def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if parse_mode:
        payload["parse_mode"] = parse_mode
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
                {"text": "Подписаться", "url": f"https://t.me/{CHANNEL_ID[4:]}"},  # Убираем "-100" для URL
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

# Основной цикл long polling
def main():
    offset = 0
    while True:
        try:
            # Получаем обновления через long polling
            url = f"{TELEGRAM_API_URL}getUpdates?offset={offset}&timeout=30"
            response = requests.get(url)
            response.raise_for_status()
            updates = response.json()['result']

            for update in updates:
                offset = update['update_id'] + 1  # Увеличиваем offset для следующего запроса

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
                            # Редактируем подпись первого сообщения
                            caption = (
                                "Поздравляем! \n"
                                "Ты подписан на наши обновления и мы хотим отблагодарить тебя промокодом на наши мероприятия:"
                            )
                            edit_message_caption(chat_id, message_id, caption)
                            # Отправляем второе сообщение с промокодом (жирный и моноширинный) и кнопкой
                            promo_text = f"<b><code>{PROMO_CODE}</code></b>"
                            send_message(chat_id, promo_text, reply_markup=get_ticket_keyboard(), parse_mode="HTML")
                        else:
                            edit_message_caption(chat_id, message_id, 
                                "К сожалению, ты всё ещё не подписан на наш канал.", 
                                reply_markup=get_subscription_keyboard())

            time.sleep(1)  # Задержка, чтобы не перегружать API

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении обновлений: {e}")
            time.sleep(5)  # Задержка перед повторной попыткой

if __name__ == "__main__":
    main()
