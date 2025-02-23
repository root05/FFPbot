import telebot
from telebot import types
from flask import Flask, request
import os

# Получаем значения из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN или CHANNEL_ID не установлены в переменных окружения")

# Инициализация бота и Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Функция проверки подписки
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# Создание клавиатуры с кнопками
def get_subscription_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    subscribe_button = types.InlineKeyboardButton("Подписаться", url=f"https://t.me/{CHANNEL_ID[1:]}")
    check_button = types.InlineKeyboardButton("Уже подписан", callback_data="check_subscription")
    keyboard.add(subscribe_button, check_button)
    return keyboard

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    image_url = "https://sun9-28.userapi.com/s/v1/ig2/uPvIzj3U5U2z-7jS8SwawDLX1hkvF7SgzN3VcMy-0_TvQnvUYoywgVRWk1rCgNTGGTxXNxMIDxFXGVGkb14CgxgJ.jpg?quality=95&as=32x32,48x48,72x72,108x108,160x160,240x240,360x360,480x480,540x540,640x640,720x720,1080x1080,1280x1280,1301x1301&from=bu&u=eG0S4Pm-U5esBh_oRE8MwlhlXhV2kDKgO9a8FWI_xqU&cs=1301x1301"
    caption = "Привет! Это Friendly Fire Promo! Подпишись на наш канал, чтобы быть в курсе новых вечеринок и получить свою скидку."
    try:
        bot.send_photo(user_id, image_url, caption=caption, reply_markup=get_subscription_keyboard())
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")

# Обработка нажатия кнопки "Уже подписан"
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def handle_check_subscription(call):
    user_id = call.from_user.id
    try:
        if check_subscription(user_id):
            keyboard = types.InlineKeyboardMarkup()
            ticket_button = types.InlineKeyboardButton("Купить билет", url="https://hardline-dnb.ru/")
            keyboard.add(ticket_button)
            bot.edit_message_caption(
                chat_id=user_id,
                message_id=call.message.message_id,
                caption="Поздравляем! Вы подписаны на наши обновления, мы хотим отблагодарить вас промокодом на наши мероприятия! Промокод: JUNGLEISMASSIVE действует только при покупке билетов онлайн.",
                reply_markup=keyboard
            )
        else:
            bot.edit_message_caption(
                chat_id=user_id,
                message_id=call.message.message_id,
                caption="К сожалению, вы всё ещё не подписаны на наш канал.",
                reply_markup=get_subscription_keyboard()
            )
    except Exception as e:
        bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте позже.")
        print(f"Ошибка: {e}")

# Маршрут для корневого URL
@app.route('/', methods=['GET'])
def home():
    return "Friendly Fire Promo Bot is running!", 200

# Маршрут для вебхука
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'OK', 200
    except Exception as e:
        print(f"Ошибка в вебхуке: {e}")
        return 'Error', 500

# Запуск приложения
if __name__ == "__main__":
    bot.remove_webhook()
    render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_hostname:
        try:
            bot.set_webhook(url=f"https://{render_hostname}/webhook")
            print(f"Вебхук установлен: https://{render_hostname}/webhook")
        except Exception as e:
            print(f"Ошибка установки вебхука: {e}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
