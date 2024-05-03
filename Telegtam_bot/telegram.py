import telebot
from telebot import types
from training_schedule import training_schedule


# Задаємо токен вашого бота Телеграм
TELEGRAM_BOT_TOKEN = '7043652644:AAF69ahGAIVgyCJiNyLY8jfrlURc26qzXVk'

# Ініціалізуємо бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Змінна для зберігання даних про користувача
user_data = {}


# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Створюємо клавіатуру з кнопками
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("🏋️‍♂️ Записатись на групове тренування")
    button2 = types.KeyboardButton("👀 Мої записи")
    button3 = types.KeyboardButton("❌ Скасувати запис")
    button4 = types.KeyboardButton("ℹ️ Про нас")
    button5 = types.KeyboardButton("📞 Контакти")
    keyboard.add(button1)
    keyboard.add(button2, button3)
    keyboard.add(button4, button5)

    # Вітаємо користувача та надсилаємо клавіатуру з кнопками
    welcome_message = "Вітаємо у ArmyFitness! Оберіть опцію:"
    bot.reply_to(message, welcome_message, reply_markup=keyboard)

# Обробник команди /restart
@bot.message_handler(commands=['restart'])
def restart(message):
    # Відправляємо повідомлення вітання знову
    send_welcome(message)  # Відправляємо повідомлення вітання знову

# Обробник для команди /help
@bot.message_handler(commands=['help'])
def help_command(message):
    # Текст повідомлення з контактним номером телефону та смайликом
    help_text = "Зв'яжись з нами, якщо у тебе виникнуть питання: +380 (68) 685 19 03 📞"
    # Відправлення повідомлення з текстом
    bot.reply_to(message, help_text)



# Обробник вибору опції 1 - "Записатись на групове тренування 🏋️‍♂️"
@bot.message_handler(func=lambda message: message.text ==
                     "🏋️‍♂️ Записатись на групове тренування"
                     )
def request_name_and_surname(message):
    # Запитуємо ім'я та прізвище користувача
    bot.reply_to(message, "Будь ласка, введіть своє ім'я та прізвище:")
    # Зберігаємо стан - очікуємо ім'я та прізвище
    bot.register_next_step_handler(message, save_name_and_surname)


# Функція для зберігання імені та прізвища користувача
def save_name_and_surname(message):
    # Розділяємо ім'я та прізвище
    name_and_surname = message.text.split()
    # Зберігаємо ім'я та прізвище користувача в словнику user_data
    user_data['name'] = name_and_surname[0]
    user_data['surname'] = name_and_surname[1] if len(name_and_surname) > 1 else ''
    # Переходимо до наступного кроку - запиту на введення номеру телефону
    request_phone(message)


# Функція для запиту номеру телефону
def request_phone(message):
    # Відправляємо спеціальну кнопку для поділу номера телефону
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Поділитися номером телефону", request_contact=True)
    keyboard.add(button)
    bot.reply_to(message, "Будь ласка, натисніть кнопку нижче, щоб поділитися своїм номером телефону:", reply_markup=keyboard)


# Обробник для отримання номера телефону
@bot.message_handler(content_types=['contact'])
def save_phone(message):
    # Зберігаємо номер телефону користувача в словнику user_data
    user_data['phone'] = message.contact.phone_number
    # Переходимо до наступного кроку - вибору виду тренування
    choose_training_type(message)


# Функція для вибору виду тренування
def choose_training_type(message):
    # Створюємо клавіатуру з кнопками для вибору виду тренування
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("KANGOO JUMPS")
    button2 = types.KeyboardButton("Силова FULL BODY")
    button3 = types.KeyboardButton("Розтяжка STRETCHING")
    button4 = types.KeyboardButton("TRX")
    keyboard.add(button1, button2, button3, button4)

    # Запитуємо вибір користувача
    bot.reply_to(message, "Оберіть вид тренування:", reply_markup=keyboard)


# Обробник для вибору виду тренування
@bot.message_handler(func=lambda message: message.text in ["KANGOO JUMPS", "Силова FULL BODY", "Розтяжка STRETCHING", "TRX"])
def save_training_type(message):
    # Зберігаємо вибраний вид тренування в словнику user_data
    user_data['training_type'] = message.text

    if message.text == "KANGOO JUMPS":
        # Отримуємо розклад для обраного тренування з файлу training_schedule.py
        schedule = training_schedule.get(message.text)

        if schedule:
            # Створюємо клавіатуру з кнопками для вибору дати та часу тренування
            keyboard = types.InlineKeyboardMarkup()
            for item in schedule:
                button = types.InlineKeyboardButton(
                    text=item, callback_data=item
                    )
                keyboard.add(button)
            bot.reply_to(message, f"Оберіть бажану дату та час тренування {message.text}:", reply_markup=keyboard)
        else:
            bot.reply_to(message, "На жаль, розклад для обраного тренування відсутній.")
    else:
        # Отримуємо розклад для обраного тренування з файлу training_schedule.py
        schedule = training_schedule.get(message.text)

        if schedule:
            # Створюємо клавіатуру з кнопками для вибору дати та часу тренування
            keyboard = types.InlineKeyboardMarkup()
            for item in schedule:
                button = types.InlineKeyboardButton(text=item, callback_data=item)
                keyboard.add(button)
            bot.reply_to(message, f"Оберіть бажану дату та час тренування {message.text}:", reply_markup=keyboard)
        else:
            bot.reply_to(message, "На жаль, розклад для обраного тренування відсутній.")


# Обробник для зберігання обраної дати та часу тренування
@bot.callback_query_handler(func=lambda call: True)
def save_training_date_and_time(call):
    # Зберігаємо обрану дату та час тренування в словнику user_data
    user_data['training_date_and_time'] = call.data
    if user_data['training_type'] == "KANGOO JUMPS":
        # Запитуємо розмір взуття лише для тренування KANGOO JUMPS
        bot.send_message(call.message.chat.id, "Будь ласка, введіть свій розмір взуття:")
        # Зберігаємо стан - очікуємо розмір взуття
        bot.register_next_step_handler(call.message, save_shoe_size)
    else:
        # В інших випадках відразу відправляємо заключне повідомлення
        send_final_message(call.message)


# Заключне повідомлення після запису
def send_final_message(message):
    # Формуємо текст повідомлення
    google_maps_link = "https://maps.app.goo.gl/qkmrEqqbpF64iNm38"
    final_message = f"Дякуємо за запис, {user_data['name']}! 🎉\n"
    final_message += f"Чекаємо на тренуванні з {user_data['training_type']}! 💪🏼 \n\n"
    final_message += f"🗓️ Дата та час тренування: {user_data['training_date_and_time']}. \n"
    final_message += f"📍 Місце зустрічі: {google_maps_link} \n"
    final_message += "📞 Контактний номер телефону: +380 (68) 685 19 03"
    bot.send_message(message.chat.id, final_message)


# Обробник для збереження розміру взуття
def save_shoe_size(message):
    try:
        # Перевіряємо, чи коректно введений розмір взуття
        shoe_size = int(message.text)
        # Перевіряємо, чи розмір взуття знаходиться у діапазоні 34-46
        if 34 <= shoe_size <= 46:
            user_data['shoe_size'] = shoe_size
            # Відправляємо заключне повідомлення
            send_final_message(message)
        else:
            # Якщо розмір взуття не знаходиться у діапазоні 34-46, повідомляємо користувача
            bot.reply_to(
                message,
                "Будь ласка, введіть розмір взуття у діапазоні від 34 до 46."
            )
            # Продовжуємо запитувати розмір взуття
            bot.register_next_step_handler(message, save_shoe_size)
    except ValueError:
        # Якщо введений розмір взуття не є цілим числом, повідомляємо користувача про помилку та просимо ввести розмір взуття знову
        bot.reply_to(
            message,
            "Будь ласка, введіть розмір взуття у форматі цілого числа."
        )
        # Продовжуємо запитувати розмір взуття
        bot.register_next_step_handler(message, save_shoe_size)


# Обробник для кнопки "Контакти 📞"
@bot.message_handler(func=lambda message: message.text == "📞 Контакти")
def contact_us(message):
    contact_text = (
        "📞 <b>Контактний номер телефону:</b> \n+380 (68) 685 19 03\n\n"
        "📍 <b>Знайти нас:</b> Натисніть кнопку, щоб знайти нас на Google Maps: <a href='https://maps.app.goo.gl/qkmrEqqbpF64iNm38'>Відкрити на Google Maps</a>\n\n"
        "🌐 <b>Сайт:</b> Відвідайте наш <a href='https://w.wlaunch.net/i/armyfitness/b/e62e1248-c4f3-11ee-b6a9-252e06c66558/s'>веб-сайт</a> для детальної інформації про розклад тренувань та послуги студії.\n\n"
        "📺 <b>Instagram:</b> Слідкуйте за нами у <a href='https://www.instagram.com/armyfitness.kyiv/'>Instagram</a> і дізнавайтеся про наші останні події та тренування!\n\n"
        "👤 <b>Facebook:</b> Підписуйтесь на нашу сторінку у <a href='https://www.facebook.com/armyfitnessstudio/'>Facebook</a> та беріть участь у наших спільнотах та акціях!"
    )

    bot.reply_to(message, contact_text, parse_mode='HTML')


# Обробник для кнопки "Про нас ℹ️"
@bot.message_handler(func=lambda message: message.text == "ℹ️ Про нас")
def about_us(message):
    about_text = (
        "<b> ARMY fitness studio </b>\n\n"
        "Наша студія про любов до себе та свого тіла, ми закохуємо дівчат в спорт, мотивуємо та надихаємо ставати кращими кожен день! "
        "Наша місія - це здорове, красиве тіло та щаслива і задоволена ТИ! З нами схудло більше 1000 дівчат без дієт та жорстких обмежень 💪🏼🌟"
    )
    bot.reply_to(message, about_text, parse_mode='HTML')


# Запускаємо бота
bot.polling()
