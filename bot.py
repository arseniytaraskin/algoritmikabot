from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Установите токен вашего бота
TOKEN = '7306744515:AAFX6M9WE0GfPf-kfG4Q9qjQMdT1mJIbPiU'

# ID вашей таблицы
SHEET_ID = '1DXp2zvhf8JEGSBf3HrnP-RFwiHvKuUh4FsFtWh3MLNY'

# Установите путь к вашему JSON файлу с учетными данными
CREDENTIALS_FILE = 'algoritmika-429013-6b635be7ceac.json'

# Настройка подключения к Google Таблицам
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Приветственное сообщение с встроенной клавиатурой
WELCOME_MESSAGE = (
    "Вас приветствует международная школа программирования и математики Алгоритмика для детей 6-14 лет в Екатеринбурге и Свердловской области 🧑‍💻\n\n"
    "Учитесь в школе международного уровня и создайте успешное будущее своему ребёнку вместе с IT-навыками от Алгоритмики 🚀\n\n"
    "Выберите действие:"
)

LOCATIONS = [
    "ул. Уральская, 59",
    "ул. Совхозная, 2",
    "ул. Кировградская, 11",
    "ул. Сони Морозовой, 190",
    "ул. Сыромолотова, 14",
    "г. Верхняя Пышма, ул. Уральских Рабочих, 45а"
]

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Записаться на бесплатное пробное занятие", callback_data='signup')],
        [InlineKeyboardButton("Локации Алгоритмики", callback_data='locations')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user = update.message.from_user
    username = user.username if user.username else 'Не указан'

    if text == 'Записаться на бесплатное пробное занятие':
        update.message.reply_text(
            'Бесплатное пробное занятие — это возможность познакомиться с нашими услугами.\n\n'
            'Пожалуйста, укажите Ваше ФИО и номер телефона в формате: ФИО, Номер телефона'
        )
    else:
        user_input = text.split(', ')
        if len(user_input) == 2:
            name, phone = user_input
            sheet.append_row([name, phone, username])
            update.message.reply_text('Спасибо за заявку! Мы свяжемся с вами.')
        else:
            update.message.reply_text('Пожалуйста, укажите ФИО и номер телефона в формате: ФИО, Номер телефона')

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'signup':
        # Отправляем изображение
        query.message.reply_photo(photo=open('images/trial_lesson.png', 'rb'))

        # Отправляем сообщение с просьбой указать ФИО и номер телефона
        query.message.reply_text(
            'Бесплатное пробное занятие — это возможность познакомиться с нашими услугами.\n\n'
            'Пожалуйста, укажите Ваше ФИО и номер телефона в формате: ФИО, Номер телефона'
        )
    elif query.data == 'locations':
        # Отправляем изображение
        query.message.reply_photo(photo=open('images/locations.jpg', 'rb'))

        # Создаем кнопки с адресами
        keyboard = [[InlineKeyboardButton(location, callback_data=f'location_{i}')] for i, location in enumerate(LOCATIONS)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Выберите локацию:', reply_markup=reply_markup)
    elif query.data.startswith('location_'):
        # Получаем индекс выбранной локации
        index = int(query.data.split('_')[1])
        location = LOCATIONS[index]

        # Предлагаем записаться на пробное занятие
        query.message.reply_text(
            f'Вы выбрали локацию: {location}\n\n'
            'Бесплатное пробное занятие — это возможность познакомиться с нашими услугами.\n\n'
            'Пожалуйста, укажите Ваше ФИО и номер телефона в формате: ФИО, Номер телефона'
        )
    else:
        query.message.reply_text('Неизвестное действие.')

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
