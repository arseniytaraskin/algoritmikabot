from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import texts
from datetime import datetime

TOKEN = '7306744515:AAFX6M9WE0GfPf-kfG4Q9qjQMdT1mJIbPiU'
SHEET_ID = '1DXp2zvhf8JEGSBf3HrnP-RFwiHvKuUh4FsFtWh3MLNY'
CREDENTIALS_FILE = 'algoritmika-429013-6b635be7ceac.json'

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

LOCATIONS = [
    "ул. Уральская, 59",
    "ул. Совхозная, 2",
    "ул. Кировградская, 11",
    "ул. Сони Морозовой, 190",
    "ул. Сыромолотова, 14",
    "г. Верхняя Пышма, ул. Уральских Рабочих, 45а"
]

COURSES = [
    ("Scratch - визуальный язык программирования.", "presentation/presentation_scratch.pdf"),
    ("Python Start - 1 год.", "presentation/presentation_scratch.pdf"),
    ("Roblox - геймдизайн.", "presentation/presentation_scratch.pdf"),
    ("Unity - создание 3D игр.", "presentation/presentation_scratch.pdf")
]

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Записаться на бесплатное пробное занятие", callback_data='signup')],
        [InlineKeyboardButton("Локации Алгоритмики", callback_data='locations')],
        [InlineKeyboardButton("Наши курсы", callback_data='courses')],
        [InlineKeyboardButton("Нейросмена 2.0", callback_data='neurosmena')],
        [InlineKeyboardButton("Связь с менеджером", callback_data='contact_manager')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(texts.WELCOME_MESSAGE, reply_markup=reply_markup)

def show_main_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Записаться на бесплатное пробное занятие", callback_data='signup')],
        [InlineKeyboardButton("Локации Алгоритмики", callback_data='locations')],
        [InlineKeyboardButton("Наши курсы", callback_data='courses')],
        [InlineKeyboardButton("Нейросмена 2.0", callback_data='neurosmena')],
        [InlineKeyboardButton("Связь с менеджером", callback_data='contact_manager')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Что бы вы хотели сделать дальше?", reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user = update.message.from_user
    username = user.username if user.username else 'Не указан'
    signup_type = context.user_data.get('signup_type')
    location = context.user_data.get('selected_location', 'Не указано')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_input = text.split(maxsplit=1)
    if len(user_input) == 2:
        name, phone = user_input
        if signup_type == 'neurosmena':
            sheet.append_row([name, phone, username, 'Нейросмена 2.0', timestamp])
            update.message.reply_text('Спасибо за заявку на нейросмену 2.0! Мы свяжемся с вами.')
        elif signup_type == 'contact_manager':
            sheet.append_row([name, phone, username, 'Связь с менеджером', timestamp])
            update.message.reply_text('Спасибо! Мы свяжемся с вами по указанным контактным данным.')
        elif signup_type == 'location':
            sheet.append_row([name, phone, username, location, timestamp])
            update.message.reply_text(f'Спасибо за заявку! Мы свяжемся с вами. Локация: {location}')
        else:
            sheet.append_row([name, phone, username, 'Общая заявка', timestamp])
            update.message.reply_text('Спасибо за заявку! Мы свяжемся с вами.')

        context.user_data['signup_type'] = None
        context.user_data['selected_location'] = None
        show_main_menu(update, context)
    else:
        update.message.reply_text('Пожалуйста, укажите ФИО и номер телефона в формате: ФИО Номер телефона')

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == 'signup':
        context.bot.send_photo(chat_id=chat_id, photo=open('images/trial_lesson.png', 'rb'))
        context.bot.send_message(
            chat_id=chat_id,
            text='Бесплатное пробное занятие — это возможность познакомиться с нашими услугами.\n\n'
                 'Пожалуйста, укажите Ваше ФИО и номер телефона в формате: ФИО Номер телефона'
        )
    elif query.data == 'locations':
        context.bot.send_photo(chat_id=chat_id, photo=open('images/locations.jpg', 'rb'))
        keyboard = [[InlineKeyboardButton(location, callback_data=f'location_{i}')] for i, location in enumerate(LOCATIONS)]
        keyboard.append([InlineKeyboardButton("Назад", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text='Выберите локацию:', reply_markup=reply_markup)
    elif query.data.startswith('location_'):
        index = int(query.data.split('_')[1])
        location = LOCATIONS[index]
        context.user_data['selected_location'] = location
        context.user_data['signup_type'] = 'location'
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Вы выбрали локацию: {location}\n\n'
                 'Бесплатное пробное занятие — это возможность познакомиться с нашими услугами.\n\n'
                 'Пожалуйста, укажите Ваше ФИО и номер телефона в формате: ФИО Номер телефона'
        )
    elif query.data == 'courses':
        context.bot.send_photo(chat_id=chat_id, photo=open('images/courses.jpg', 'rb'))
        keyboard = [[InlineKeyboardButton(course[0], callback_data=f'course_{i}')] for i, course in enumerate(COURSES)]
        keyboard.append([InlineKeyboardButton("Назад", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text='Выберите курс:', reply_markup=reply_markup)
    elif query.data.startswith('course_'):
        index = int(query.data.split('_')[1])
        course = COURSES[index]
        with open(course[1], 'rb') as presentation:
            context.bot.send_document(chat_id=chat_id, document=presentation)
    elif query.data == 'neurosmena':
        context.bot.send_message(chat_id=chat_id, text=texts.NEUROSMENA_TEXT)
        context.user_data['signup_type'] = 'neurosmena'
    elif query.data == 'contact_manager':
        context.bot.send_photo(chat_id=chat_id, photo=open('images/contact_manager.png', 'rb'))
        context.bot.send_message(
            chat_id=chat_id,
            text='⭐️Оставьте свои контактные данные (имя и номер телефона), чтобы мы могли связаться с вами'
        )
        context.user_data['signup_type'] = 'contact_manager'
    elif query.data == 'back':
        show_main_menu(update, context)
    else:
        context.bot.send_message(chat_id=chat_id, text='Неизвестное действие.')

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
