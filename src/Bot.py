from ExerciseType import ExerciseType
from Appointment import Appointment
from Exercise import Exercise
from Client import Client
from FitnessSheet import FitnessSheet
import telebot
from telebot import types
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from enum import Enum


class SelectedWorkflow(Enum):
    NONE = 0
    CREATE_APPOINTMENT = 1
    GET_APPOINTMENTS = 2
    DELETE_APPOINTMENT = 3
    GIVE_FEEDBACK = 4


class BotCache:
    def __init__(self, client: Client = None):
        self.__client: Client = client
        self.__workflow: SelectedWorkflow = SelectedWorkflow.NONE
        self.__appointments: list[Appointment] = []
        self.__new_to_bot = False

    def get_client(self) -> Client:
        return self.__client

    def set_client(self, client: Client):
        self.__new_to_bot = self.__client is None
        self.__client = client

    def is_new_to_bot(self) -> bool:
        is_new: bool = self.__new_to_bot
        self.__new_to_bot = False
        return is_new

    def get_workflow(self) -> SelectedWorkflow:
        return self.__workflow

    def set_workflow(self, workflow: SelectedWorkflow):
        self.__workflow = workflow

    def get_appointments(self) -> list[Appointment]:
        return self.__appointments

    def reset_appointments(self):
        self.__appointments = []

    def set_appointments(self, appointments: list[Appointment]):
        self.__appointments = appointments

    def add_appointment(self, appointment: Appointment):
        self.__appointments.append(appointment)


class Bot:
    __min_shoe_size = 34
    __max_shoe_size = 46
    __admin_id = 413423581

    def __init__(self, token: str, fitness_sheet: FitnessSheet):
        self.__fitness_sheet: FitnessSheet = fitness_sheet
        self.__exercise_types: {str, ExerciseType} = {}
        self.__make_exercise_types()
        self.__bot_cache: {str, BotCache} = {}

        self.__bot = telebot.TeleBot(token)
        self.__welcome_handler = self.__bot.message_handler(commands=['start'])(self.__send_welcome)
        self.__restart_handler = self.__bot.message_handler(commands=['restart'])(self.__restart)
        self.__help_handler = self.__bot.message_handler(commands=['help'])(self.__help_command)
        self.__contact_handler = self.__bot.message_handler(func=lambda message: message.text == "📞 Контакти")(self.__contact_us)
        self.__appointments_handler = self.__bot.message_handler(func=lambda message: message.text == "👀 Мої записи")(self.__my_appointments)
        self.__about_handler = self.__bot.message_handler(func=lambda message: message.text == "ℹ️ Про нас")(self.__about_us)
        self.__request_usr_data_handler = self.__bot.message_handler(func=lambda message: message.text == "🏋️‍♂️ Записатись на групове тренування")(self.__start_appointment_creation)
        self.__get_client_data_handler = self.__bot.message_handler(content_types=['contact'])(self.__get_phone_and_create_client)
        self.__save_training_type_handler = self.__bot.message_handler(func=lambda message: message.text in self.__exercise_types.keys())(self.__save_training_type)
        self.__callback_handler = self.__bot.callback_query_handler(func=lambda call: True)(self.__query_callback)
        self.__delete_appointments = self.__bot.message_handler(func=lambda message: message.text == "❌ Скасувати запис")(self.__delete_my_appointment)
        self.__feedback_command_handler = self.__bot.message_handler(commands=['feedback'])(self.__feedback_handler)

        # Запускаємо бота
        print('Polling...')
        self.__bot.polling()

    # Обробник команди /start
    def __send_welcome(self, message):
        self.__make_exercise_types()
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
        self.__bot.reply_to(message, welcome_message, reply_markup=keyboard)

    # Обробник команди /restart
    def __restart(self, message):
        self.__make_exercise_types()
        self.__set_workflow(message, SelectedWorkflow.NONE)
        self.__reset_client_appointments(message)
        # Відправляємо повідомлення вітання знову
        self.__send_welcome(message)  # Відправляємо повідомлення вітання знову

    # Обробник для команди /help
    def __help_command(self, message):
        # Текст повідомлення з контактним номером телефону та смайликом
        help_text = "Зв'яжись з нами, якщо у тебе виникнуть питання: +380 (68) 685 19 03 📞"
        # Відправлення повідомлення з текстом
        self.__bot.reply_to(message, help_text)

    # Обробник для команди /feedback
    def __feedback_handler(self, message):
        self.__set_workflow(message, SelectedWorkflow.GIVE_FEEDBACK)
        # Перевірка, чи відомий клієнт
        if self.__is_client_known(message):
            self.__get_feedback(message)
        else:
            # Якщо клієнт не відомий, просимо його спочатку надати контактні дані
            self.__request_user_data(message)

    def __get_feedback(self, message):
        self.__bot.send_message(message.chat.id, "Будь ласка, напишіть відгук:", reply_markup=types.ReplyKeyboardRemove())
        # Зберігаємо стан - очікуємо відгук
        self.__bot.register_next_step_handler(message, self.__send_feedback_to_admin)

    def __send_feedback_to_admin(self, message):
        self.__set_workflow(message, SelectedWorkflow.NONE)
        # Отримання тексту повідомлення від користувача
        self.__bot.send_message(message.chat.id, "Дякуємо за ваш відгук!")
        self.__admin_notification_feedback(message)
        self.__restart(message)

    def __is_client_known(self, message) -> bool:
        return message.chat.id in self.__bot_cache.keys() and \
               self.__bot_cache[message.chat.id] is not None and \
               self.__bot_cache[message.chat.id].get_client() is not None

    def __get_client(self, message) -> Client:
        if self.__is_client_known(message):
            return self.__bot_cache[message.chat.id].get_client()
        else:
            return None

    # Обробник для кнопки "Контакти 📞"
    def __contact_us(self, message):
        contact_text = (
            "📞 <b>Контактний номер телефону:</b> \n+380 (68) 685 19 03\n\n"
            "📍 <b>Знайти нас:</b> Натисніть кнопку, щоб знайти нас на Google Maps: <a href='https://maps.app.goo.gl/qkmrEqqbpF64iNm38'>Відкрити на Google Maps</a>\n\n"
            "📺 <b>Instagram:</b> Слідкуйте за нами у <a href='https://www.instagram.com/armyfitness.kyiv/'>Instagram</a> і дізнавайтеся про наші останні події та тренування!\n\n"
            "👤 <b>Facebook:</b> Підписуйтесь на нашу сторінку у <a href='https://www.facebook.com/armyfitnessstudio/'>Facebook</a> та беріть участь у наших спільнотах та акціях!\n\n"
            "🌐 <b>Сайт:</b> Відвідайте наш <a href='https://w.wlaunch.net/i/armyfitness/b/e62e1248-c4f3-11ee-b6a9-252e06c66558/s'>веб-сайт</a> для детальної інформації про розклад тренувань та послуги студії."
        )

        self.__bot.reply_to(message, contact_text, parse_mode='HTML')

    # Обробник для кнопки "Про нас ℹ️"
    def __about_us(self, message):
        about_text = (
            "<b> ARMY fitness studio </b>\n\n"
            "Наша студія про любов до себе та свого тіла, ми закохуємо дівчат в спорт, мотивуємо та надихаємо ставати кращими кожен день! "
            "Наша місія - це здорове, красиве тіло та щаслива і задоволена ТИ! З нами схудло більше 1000 дівчат без дієт та жорстких обмежень 💪🏼🌟\n\n"
            "<b>Kangoo Jumps:</b> кардіо без бігу, спалює до 1000 ккал за годину, розгружає суглоби, сприяє схудненню та піднімає настрій.\n\n"
            "<b>Силова Full Body:</b> силове тренування з вагою, формує рельєфне та сильне тіло, позбавляє від проблемних зон, надає струнку фігуру, красиві руки та прес.\n\n"
            "<b>Розтяжка Stretching:</b> це комплекс вправ для гнучкості тіла, релаксуюче тренування, що покращує поставу та розтяжку.\n\n"
            "<b>TRX:</b> тренування з власною вагою для всього тіла, підходить для всіх рівнів підготовки, розвиває силу, витривалість, гнучкість та рівновагу."
        )
        self.__bot.reply_to(message, about_text, parse_mode='HTML')

    # Обробник вибору опції 1 - "Записатись на групове тренування 🏋️‍♂️"
    def __start_appointment_creation(self, message):
        self.__make_exercise_types()
        self.__set_workflow(message, SelectedWorkflow.CREATE_APPOINTMENT)
        if self.__is_client_known(message):
            self.__choose_training_type(message)
        else:
            self.__request_user_data(message)

    # Функція для запиту номеру телефону
    def __request_user_data(self, message):
        # Відправляємо спеціальну кнопку для поділу номера телефону
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button = types.KeyboardButton(text="Поділитися номером телефону", request_contact=True)
        keyboard.add(button)
        self.__bot.reply_to(message, "Будь ласка, натисніть кнопку нижче, щоб поділитися своїм номером телефону:", reply_markup=keyboard)

    # Обробник для отримання номера телефону
    def __get_phone_and_create_client(self, message):
        # Зберігаємо номер телефону користувача в словнику user_data
        client: Client = Client(message.contact.user_id, message.contact.first_name, message.contact.last_name, message.contact.phone_number)
        self.__set_client(message, client)
        if self.__get_workflow(message) == SelectedWorkflow.CREATE_APPOINTMENT:
            # Переходимо до наступного кроку - вибору виду тренування
            self.__choose_training_type(message)
        elif self.__get_workflow(message) == SelectedWorkflow.GET_APPOINTMENTS:
            self.__show_appointments(message)
        elif self.__get_workflow(message) == SelectedWorkflow.DELETE_APPOINTMENT:
            self.__show_appointments(message)
        elif self.__get_workflow(message) == SelectedWorkflow.GIVE_FEEDBACK:
            self.__get_feedback(message)
        else:
            self.__restart(message)

    # Функція для вибору виду тренування
    def __choose_training_type(self, message):
        # Створюємо клавіатуру з кнопками для вибору виду тренування
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        for et in self.__exercise_types.keys():
            keyboard.add(types.KeyboardButton(et))

        # Запитуємо вибір користувача
        self.__bot.reply_to(message, "Оберіть вид тренування:", reply_markup=keyboard)

    # Make excersizetypes as a Dictionary
    def __make_exercise_types(self):
        ex_types: list[ExerciseType] = self.__fitness_sheet.get_exercise_types()
        for et in ex_types:
            self.__exercise_types[et.get_name()] = et

    def __save_training_type(self, message):
        # Зберігаємо вибраний вид тренування в словнику user_data
        ex_type_name = message.text
        self.__exercise_type = self.__exercise_types[ex_type_name]

        # Отримуємо розклад для обраного тренування
        exercises: list[Exercise] = self.__get_exercises()
        schedule: list[str] = []
        for ex in exercises:
            if ex.get_free_slots() > 0:
                schedule.append(ex.get_timestamp())

        if len(schedule) > 0:
            # Створюємо клавіатуру з кнопками для вибору дати та часу тренування
            keyboard = types.InlineKeyboardMarkup()
            for item in schedule:
                button = types.InlineKeyboardButton(text=item, callback_data=item)
                keyboard.add(button)
            self.__bot.reply_to(message, f"Оберіть бажану дату та час тренування {message.text}:", reply_markup=keyboard)
        else:
            self.__bot.reply_to(message, "На жаль, розклад для обраного тренування відсутній.")

    def __query_callback(self, call):
        if self.__get_workflow(call.message) == SelectedWorkflow.CREATE_APPOINTMENT:
            self.__create_appointment(call)
        elif self.__get_workflow(call.message) == SelectedWorkflow.GET_APPOINTMENTS:
            self.__restart(call.message)
        elif self.__get_workflow(call.message) == SelectedWorkflow.DELETE_APPOINTMENT:
            self.__delete_appointment(call)
        else:
            self.__restart(call.message)

    # Обробник для зберігання обраної дати та часу тренування
    def __create_appointment(self, call):
        if self.__get_workflow(call.message) != SelectedWorkflow.CREATE_APPOINTMENT:
            self.__restart(call.message)
        # Зберігаємо обрану дату та час тренування в словнику user_data
        self.__timestamp = call.data
        client: Client = self.__get_client(call.message)
        foot_size = 0 if client is None else client.get_foot_size()
        if self.__exercise_type.is_size_foot_required() and foot_size == 0:
            # Запитуємо розмір взуття лише для тренування KANGOO JUMPS
            self.__bot.send_message(call.message.chat.id, "Будь ласка, введіть свій розмір взуття:", reply_markup=types.ReplyKeyboardRemove())
            # Зберігаємо стан - очікуємо розмір взуття
            self.__bot.register_next_step_handler(call.message, self.__save_shoe_size)
        else:
            # В інших випадках відразу відправляємо заключне повідомлення
            self.__make_appointment(call.message)

    # Обробник для збереження розміру взуття
    def __save_shoe_size(self, message):
        try:
            # Перевіряємо, чи коректно введений розмір взуття
            shoe_size = int(message.text)
            # Перевіряємо, чи розмір взуття знаходиться у діапазоні 34-46
            if self.__min_shoe_size <= shoe_size <= self.__max_shoe_size:
                self.__get_client(message).set_foot_size(shoe_size)
                # Відправляємо заключне повідомлення
                self.__make_appointment(message)
            else:
                # Якщо розмір взуття не знаходиться у діапазоні 34-46, повідомляємо користувача
                self.__bot.reply_to(message, f"Будь ласка, введіть розмір взуття у діапазоні від {self.__min_shoe_size} до {self.__max_shoe_size}.", reply_markup=types.ReplyKeyboardRemove())
                # Продовжуємо запитувати розмір взуття
                self.__bot.register_next_step_handler(message, self.__save_shoe_size)
        except ValueError:
            # Якщо введений розмір взуття не є цілим числом, повідомляємо користувача про помилку та просимо ввести розмір взуття знову
            self.__bot.reply_to(message, "Будь ласка, введіть розмір взуття у форматі цілого числа.", reply_markup=types.ReplyKeyboardRemove())
            # Продовжуємо запитувати розмір взуття
            self.__bot.register_next_step_handler(message, self.__save_shoe_size)

    def __get_exercises(self) -> list[Exercise]:
        if self.__exercise_type is None:
            return None
        else:
            return self.__fitness_sheet.get_exercises(self.__exercise_type)

    def __make_appointment(self, message):
        appointment: Appointment = self.__fitness_sheet.make_appointment(self.__create_new_appointment(message))
        if appointment is None:
            final_message = "Помилка запису на курс"
            self.__bot.send_message(message.chat.id, final_message)
        else:
            self.__send_final_message(message, appointment)

    # Заключне повідомлення після запису
    def __send_final_message(self, message, appointment: Appointment):
        self.__set_workflow(message, SelectedWorkflow.NONE)
        # Формуємо текст повідомлення
        google_maps_link = "https://maps.app.goo.gl/qkmrEqqbpF64iNm38"
        final_message: str = ""
        if appointment.get_status() == Appointment.Status.SUCCESS:
            final_message = f"Дякуємо за запис, {appointment.get_client().get_first_name()}! 🎉\n"
            final_message += f"Чекаємо на тренуванні з {appointment.get_exercise().get_type().get_name()}! 💪🏼 \n\n"
            final_message += f"🗓️ Дата та час тренування: {appointment.get_exercise().get_timestamp()}. \n"
            final_message += f"📍 Місце зустрічі: {google_maps_link} \n"
            final_message += "📞 Контактний номер телефону: +380 (68) 685 19 03"
        elif appointment.get_status() == Appointment.Status.GROUPFULL:
            final_message = f"Вибачте, {appointment.get_client().get_first_name()}. Група повністю сформована. Оберіть інший час"
        elif appointment.get_status() == Appointment.Status.NOTFOUND:
            final_message = f"Вибачте, {appointment.get_client().get_first_name()}. заняття не знайдено"
        elif appointment.get_status() == Appointment.Status.ALREADY_ADDED:
            final_message = f"{appointment.get_client().get_first_name()}, ви вже зареєстровані на обраному занятті"
        elif appointment.get_status() == Appointment.Status.EXERCISE_IN_PAST:
            final_message = f"{appointment.get_client().get_first_name()}, нажаль, це заняття вже минуло"
        else:
            final_message = "Помилка запису на курс"

        if appointment.get_client().is_created():
            self.__admin_notification_new_client(message)

        if appointment.is_reserved_capacity():
            self.__admit_notification_reserved_capacity(appointment)

        self.__bot.send_message(message.chat.id, final_message)
        self.__restart(message)

    def __create_new_appointment(self, message) -> Appointment:
        exercises: list[Exercise] = self.__get_exercises()
        for ex in exercises:
            if ex.is_right_exercise_for_appointment(self.__exercise_type, self.__timestamp):
                return Appointment(self.__get_client(message), ex)
        return None

    def __my_appointments(self, message):
        self.__set_workflow(message, SelectedWorkflow.GET_APPOINTMENTS)
        if not self.__is_client_known(message):
            self.__request_user_data(message)
        else:
            self.__show_appointments(message)

    def __show_appointments(self, message):
        final_message: str = ""
        appointments: list[Appointment] = self.__fitness_sheet.get_appointments(self.__get_client(message), self.__get_workflow(message) == SelectedWorkflow.GET_APPOINTMENTS)
        self.__cache_appointments(message, appointments)
        # Створюємо клавіатуру з кнопками
        keyboard = types.InlineKeyboardMarkup()
        if len(appointments) > 0:
            for appointment in appointments:
                # button = types.KeyboardButton(str(appointment))
                button = types.InlineKeyboardButton(text=str(appointment), callback_data=str(appointment))
                keyboard.add(button)
            if self.__get_workflow(message) == SelectedWorkflow.DELETE_APPOINTMENT:
                final_message = "Оберіть тренування, яке хочете видалити:"
            elif self.__get_workflow(message) == SelectedWorkflow.GET_APPOINTMENTS:
                final_message = "Ось розклад Ваших тренувань:"
            else:
                self.__restart(message)
                return
        else:
            final_message = "Нажаль, тренування відсутні."

        button = types.InlineKeyboardButton(text="Назад", callback_data="Назад")
        keyboard.add(button)
        self.__bot.reply_to(message, final_message, reply_markup=keyboard)
        if self.__bot_cache[message.chat.id].is_new_to_bot() and self.__get_workflow(message) != SelectedWorkflow.DELETE_APPOINTMENT:
            self.__restart(message)

    def __delete_my_appointment(self, message):
        self.__set_workflow(message, SelectedWorkflow.DELETE_APPOINTMENT)
        if not self.__is_client_known(message):
            self.__request_user_data(message)
        else:
            self.__show_appointments(message)

    def __delete_appointment(self, call):
        final_message: str = ""
        appointments: list[Appointment] = self.__get_client_appointments(call.message)
        final_message = "Тренування не знайдено. Скасування не можливе."
        if appointments is not None and len(appointments) > 0:
            for appointment in appointments:
                if str(appointment) == call.data:
                    if self.__fitness_sheet.delete_appointment(appointment):
                        self.__admint_notifications_appointment_deleted(appointment)
                        final_message = f"Тренування скасовано: {str(appointment)}"
        self.__reset_client_appointments(call.message)
        self.__set_workflow(call.message, SelectedWorkflow.NONE)
        if call.data != "Назад":
            self.__bot.send_message(chat_id=call.message.chat.id, text=final_message)
        self.__restart(call.message)

    def __admin_notification_new_client(self, message):
        if self.__is_client_known(message) and self.__get_client(message).is_created():
            self.__bot.send_message(chat_id=self.__admin_id, text=f'New Client: {str(self.__get_client(message))}')
            self.__get_client(message).reset_created()

    def __admit_notification_reserved_capacity(self, appointment: Appointment):
        self.__bot.send_message(chat_id=self.__admin_id, text=f'Appointment in the RESERVED capacity: {str(appointment)}, client: {str(appointment.get_client())}')

    def __admint_notifications_appointment_deleted(self, appointment: Appointment):
        self.__bot.send_message(chat_id=self.__admin_id, text=f'Appointment canceled: {str(appointment)}, client: {str(appointment.get_client())}')

    def __admin_notification_feedback(self, message):
        # Відправлення повідомлення з відгуком адміністратору
        self.__bot.send_message(chat_id=self.__admin_id, text=f"Новий відгук від {self.__get_client(message).get_first_name()}: {message.text}")

    def __cache_appointments(self, message, appointments: list[Appointment]):
        bot_cache: BotCache = None if message.chat.id not in self.__bot_cache.keys() else self.__bot_cache[message.chat.id]
        if bot_cache is not None:
            bot_cache.set_appointments(appointments)

    def __get_client_appointments(self, message) -> list[Appointment]:
        if message.chat.id in self.__bot_cache.keys():
            return self.__bot_cache[message.chat.id].get_appointments()
        else:
            return None

    def __reset_client_appointments(self, message):
        if message.chat.id in self.__bot_cache.keys():
            self.__bot_cache[message.chat.id].reset_appointments()

    def __set_client(self, message, client: Client):
        if message.chat.id not in self.__bot_cache.keys():
            self.__bot_cache[message.chat.id] = BotCache(client)
        else:
            self.__bot_cache[message.chat.id].set_client(client)

    def __set_workflow(self, message, workflow: SelectedWorkflow):
        if message.chat.id not in self.__bot_cache.keys():
            self.__bot_cache[message.chat.id] = BotCache(None)
        self.__bot_cache[message.chat.id].set_workflow(workflow)

    def __get_workflow(self, message) -> SelectedWorkflow:
        if message.chat.id in self.__bot_cache.keys():
            return self.__bot_cache[message.chat.id].get_workflow()
        else:
            return SelectedWorkflow.NONE
