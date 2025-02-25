import requests
import json
import time

# Жёстко задаём константы внутри кода
BOT_TOKEN = ""
CHANNEL_ID = ""  
PROMO_CODE = ""

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
        response = requests.post(url, json=payload, timeout=60)  # Увеличенный таймаут
        response.raise_for_status()
        print(f"Сообщение отправлено пользователю {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки сообщения: {e}")
        return False
    return True

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
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(f"Фото отправлено пользователю {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки фото: {e}")
        return False
    return True

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
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(f"Сообщение обновлено для пользователя {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка редактирования сообщения: {e}")
        return False
    return True

# Функция проверки подписки
def check_subscription(user_id):
    url = f"{TELEGRAM_API_URL}getChatMember"
    payload = {
        "chat_id": CHANNEL_ID,
        "user_id": user_id
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
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
    max_retries = 5  # Максимальное количество повторных попыток
    retry_delay = 10  # Задержка между повторными попытками (секунд)

    while True:
        retries = 0
        while retries < max_retries:
            try:
                # Получаем обновления через long polling
                url = f"{TELEGRAM_API_URL}getUpdates?offset={offset}&timeout=60"  # Увеличенный таймаут
                response = requests.get(url, timeout=60)
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
                            if send_photo(chat_id, image_url, caption, reply_markup=get_subscription_keyboard()):
                                print(f"Отправлено начальное сообщение пользователю {chat_id}")
                            else:
                                print(f"Не удалось отправить начальное сообщение пользователю {chat_id}")

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
                                if edit_message_caption(chat_id, message_id, caption):
                                    promo_text = f"<b><code>{PROMO_CODE}</code></b>"
                                    if send_message(chat_id, promo_text, reply_markup=get_ticket_keyboard(), parse_mode="HTML"):
                                        print(f"Отправлен промокод пользователю {chat_id}")
                                    else:
                                        print(f"Не удалось отправить промокод пользователю {chat_id}")
                            else:
                                if edit_message_caption(chat_id, message_id, 
                                    "К сожалению, ты всё ещё не подписан на наш канал.", 
                                    reply_markup=get_subscription_keyboard()):
                                    print(f"Обновлено сообщение для пользователя {chat_id} о необходимости подписки")
                                else:
                                    print(f"Не удалось обновить сообщение для пользователя {chat_id}")

                break  # Если запрос успешен, выходим из цикла повторных попыток

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении обновлений (попытка {retries + 1}/{max_retries}): {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(retry_delay)
                else:
                    print("Превышено максимальное количество повторных попыток. Перезапуск через 60 секунд...")
                    time.sleep(60)

        # Дополнительная задержка для предотвращения перегрузки API
        time.sleep(2)  # Увеличенная задержка между циклами

if __name__ == "__main__":
    main()
