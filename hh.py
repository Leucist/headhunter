import telebot
from telebot.apihelper import ApiException

import config
import json
import time
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

# adm_functions = ['Вакансии', 'Черный список', 'Установить частоту оповещений', 'Рассылка', 'Провести опрос']
adm_functions = ['Вакансии', 'Черный список', 'Просмотреть Базу Данных', 'Отправить сообщение-вопрос', 'Рассылка']
vacancy_functions = ["Добавить вакансию", "Удалить вакансию", "Просмотреть текущий список вакансий"]
black_list_functions = ['Добавить пользователя в черный список', 'Удалить пользователя из черного списка',
                        'Просмотреть черный список']
black_id, questions, branches = [], [], []
admin_id = 1064282294

with open("black_list.json", "r", encoding="UTF-8") as blackList:
    black_data = json.loads(blackList.read())
    for user in black_data['users']:
        black_id.append(user['id'])


@bot.message_handler(commands=['start'], func=lambda message: message.chat.id not in black_id)
def start(message):
    initialisation(message)
    markup = back_markup()
    bot.send_message(message.chat.id,
                     "Здравствуй, <b>{0.first_name}</b>!\nЯ - <b>{1.first_name}</b>, бот-рекрутер компании N.\nНажмите на кнопку ниже, чтобы просмотреть список филиалов компании и доступных вакансий в них.\nКакая-то Вас заинтересует — можете пройти анкетирование прямо здесь!".format(
                         message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == admin_id:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for function in adm_functions:
            item = types.KeyboardButton(function)
            markup.add(item)
        item = types.KeyboardButton("Назад ➤")
        markup.add(item)
        sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
        bot.register_next_step_handler(sent, admin_after)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.")


def admin_after(message):
    markup = back_markup()
    if message.from_user.id == admin_id:
        if message.text == "Рассылка":
            sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?", reply_markup=markup)
            bot.register_next_step_handler(sent, mailing)
        elif message.text == "Вакансии":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for function in vacancy_functions:
                item = types.KeyboardButton(function)
                markup.add(item)
            sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
            bot.register_next_step_handler(sent, admin_after)
        elif message.text == vacancy_functions[0]:
            with open("vacancy.json", "r", encoding="UTF-8") as vac_file:
                data = json.loads(vac_file.read())
                for branch in data['vacancies']:
                    branches.append(branch)
                    bot.send_message(message.chat.id, branch, reply_markup=markup)
            sent = bot.send_message(message.chat.id, "Выберите филиал >", reply_markup=None)
            bot.register_next_step_handler(sent, vacancy_handler, -1)
        elif message.text == vacancy_functions[1]:
            vacancy_handler(message, 1)
        elif message.text == vacancy_functions[2]:
            vacancy_handler(message, 2)
        elif message.text == 'Черный список':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for function in black_list_functions:
                item = types.KeyboardButton(function)
                markup.add(item)
            sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
            bot.register_next_step_handler(sent, admin_after)
        elif message.text == black_list_functions[0]:
            sent = bot.send_message(message.chat.id,
                                    "Введите данные пользователя, которого Вы хотите добавить в черный список: ",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, black_list_handler, 0)
        elif message.text == black_list_functions[1]:
            black_list_handler(message, 1)
        elif message.text == black_list_functions[2]:
            black_list_handler(message, 2)
        elif message.text == 'Просмотреть Базу Данных':
            show_database()
        # elif message.text == 'Установить частоту оповещений':
        #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #     item1 = types.KeyboardButton("Раз в неделю")
        #     item2 = types.KeyboardButton("Через день")
        #     item3 = types.KeyboardButton("Каждый день")
        #     markup.add(item1, item2, item3)
        #     sent = bot.send_message(message.chat.id,
        #                             "С какой частотой вы хотите получать уведомления о приходящих заявках",
        #                             reply_markup=markup)
        #     bot.register_next_step_handler(sent, notifications)
        elif message.text == 'Отправить сообщение-вопрос':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Всем")
            item2 = types.KeyboardButton("Выбрать пользователя")
            markup.add(item1, item2)
            sent = bot.send_message(message.chat.id,
                                    "Разослать опрос всем пользователям или выбрать конкретного пользователя?",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, admin_after)
        elif message.text.lower() == 'всем':
            sent = bot.send_message(message.chat.id, "Опрос на какую тему Вы хотите провести?", reply_markup=None)
            bot.register_next_step_handler(sent, mailing, arguments=True)
        elif message.text == 'Выбрать пользователя':
            with open("user_base.json", "r", encoding="UTF-8") as database:
                data = json.loads(database.read())
                for s_user in data['users']:
                    bot.send_message(message.chat.id,
                                     "id: " + str(s_user['id']) + "; Имя: " + s_user['first_name'] + ";",
                                     reply_markup=None)
            sent = bot.send_message(message.chat.id, "Выберите желаемого пользователя и отправьте его id",
                                    reply_markup=None)
            bot.register_next_step_handler(sent, q_user)
        elif message.text == "Назад ➤":
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda message: message.chat.id not in black_id)
def chat(message):
    initialisation(message)
    # keyboard
    markup = back_markup()
    if message.chat.type == 'private':
        # if message.from_user.id == 1064282294:
        if message.text.lower() == 'привет':
            bot.send_message(message.chat.id,
                             "Здравствуй, <b>{0.first_name}</b>!\nЯ - <b>{1.first_name}</b>, бот-рекрутер компании N.\nНажмите на кнопку ниже, чтобы просмотреть список филиалов компании и доступных вакансий в них.\nКакая-то Вас заинтересует — можете пройти анкетирование прямо здесь!".format(
                                 message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)
        elif message.text == "Выбрать филиал":
            branches.clear()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("Назад ➤")
            markup.add(item)
            with open("vacancy.json", "r", encoding="UTF-8") as vac_file:
                data = json.loads(vac_file.read())
                bot.send_message(message.chat.id, "Вот список филиалов:", reply_markup=None)
                for branch in data['vacancies']:
                    branches.append(branch)
                    bot.send_message(message.chat.id, branch, reply_markup=None)
                sent = bot.send_message(message.chat.id, "Выберите один из них >",
                                        reply_markup=None)
                bot.register_next_step_handler(sent, user_handler)
        elif message.text == "Назад ➤":
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)


def user_handler(message):
    markup = back_markup()
    if message.text == "Назад ➤":
        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
        return -1
    for branch in branches:
        if message.text == branch:
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
            with open("vacancy.json", "r", encoding="UTF-8") as database:
                data = json.loads(database.read())
                bot.send_message(message.chat.id,
                                 'На данный момент в нашей компании, филиале "' + branch + '" доступны следующие вакансии:',
                                 reply_markup=None)
                vacancies = []
                for vac in data['vacancies'][branch]:
                    vacancies.append(vac)
                    bot.send_message(message.chat.id, "id: " + str(vac['id']) + ". Должность: " + vac["name"],
                                     reply_markup=None)
                if not vacancies:
                    bot.send_message(message.chat.id, "Нет доступных вакансий.", reply_markup=None)
                    return 1
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Введите id или должность нужной вакансии",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, pre_questionnaire, vacancies, branch)
            break
    else:
        bot.send_message(message.chat.id,
                         "Филиал по Вашему запросу не найден.\nВозможно, допущена ошибка в введенных данных.",
                         reply_markup=markup)


def pre_questionnaire(message, vacancies, branch):
    if message.text == "Назад ➤":
        markup = back_markup()
        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
    try:
        vac_id = int(message.text)
    except ValueError:
        vac_id = message.text.strip()
    for vac in vacancies:
        if vac_id == vac['id'] or vac_id == vac['name']:
            bot.send_message(message.chat.id,
                             'Вы выбрали вакансию на должность "' + vac['name'] + '".', reply_markup=None)
            if vac['extraInfo'] is not None:
                bot.send_message(message.chat.id, 'Вот дополнительная информация относительно данной вакансии: «'
                                 + str(vac['extraInfo']) + '».', reply_markup=None)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("Назад ➤")
            markup.add(item)
            bot.send_message(message.chat.id,
                             'Сейчас Вам будет представлен ряд вопросов, на которые Вам потребуется ответить:',
                             reply_markup=markup)
            questions = vac['questions']
            answers = []
            appForm = {"branch": branch, "vacancy_name": vac['name'], "vacancy_id": vac['id'], "answers": answers}
            questionnaire(message, 0, questions, appForm)
            break


def questionnaire(message, num, questions, appForm, start_time=None):
    if start_time is not None:
        final_time = time.time() - start_time
        appForm['answers'].append({"answer": message.text, "time": int(final_time)})
    if message.text == "Назад ➤":
        markup = back_markup()
        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
    else:
        if num >= len(questions):
            with open("interviewees.json", "r", encoding="UTF-8") as interviewees_base:
                data = json.loads(interviewees_base.read())
                pid = message.from_user
                data['items'] += 1
                techInfo = {"id": pid.id, "first_name": pid.first_name, "last_name": pid.last_name,
                            "username": pid.username}
                user = {"techInfo": techInfo, "appForm": appForm}
                data['users'].append(user)
                database_write(data, "interviewees.json")
                bot.send_message(message.chat.id,
                                 "Готово!\nВопросы закончились, форма успешно заполнена.\nВ случае утверждения Вас на должность, с Вами свяжутся.")
                # --------------------------------------------------------------------------------------
                with open("notification.txt", "w", encoding="UTF-8") as notification_file:
                    notification_file.write(
                        "Филиал: " + appForm['branch'] + ".\nДолжность(название,id): " +
                        appForm['vacancy_name'] + ", " + str(appForm['vacancy_id'])
                        + ".\nФорма:\n")
                    i = 0
                    for obj in appForm['answers']:
                        i += 1
                        notification_file.write(
                            str(i) + ") Ответ: «" + obj['answer'] + "»; Время: " + str(obj['time'])
                            + "с.\n")
                    last_name = techInfo['last_name']
                    username = techInfo['username']
                    if last_name is None:
                        last_name = "Не указано"
                    if username is None:
                        username = "Не указано"
                    notification_file.write("|| Контакты >\nID: " + str(techInfo['id']) + ",\nИмя: " +
                                            techInfo['first_name'] + ",\nФамилия: " + last_name +
                                            ",\nЛогин Telegram: " + username +
                                            ".\n\n----------------------------------------------\n\n")
                with open("notification.txt", "r", encoding="UTF-8") as notification_file:
                    bot.send_message(admin_id, "Рассылка форм соискателей >")
                    bot.send_document(admin_id, notification_file)
                del appForm
                return 0
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Назад ➤")
        markup.add(item)
        sent = bot.send_message(message.chat.id, questions[num], reply_markup=markup)
        start_time = time.time()
        bot.register_next_step_handler(sent, questionnaire, num + 1, questions, appForm, start_time)


def black_list_handler(message, direction):
    global past_black_user
    if direction == 0:
        with open("user_base.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            try:
                search_param = int(message.text)
            except ValueError:
                search_param = message.text
                place = search_param.find("@")
                search_param = search_param[place + 1:]
            finally:
                i = 0
                for s_user in data['users']:
                    if s_user['id'] == search_param or s_user['username'] == search_param:
                        new_black_user = data['users'][i]
                        del data['users'][i]
                        data['items'] -= 1
                        database_write(data, "user_base.json")
                        with open("black_list.json", "r", encoding="UTF-8") as blackList:
                            data = json.loads(blackList.read())
                            black_id.append(new_black_user['id'])
                            data['users'].append(new_black_user)
                            all_data = {"items": data['items'] + 1, "users": data['users']}
                            database_write(all_data, "black_list.json")
                        bot.send_message(message.chat.id, "Сделано!", reply_markup=None)
                        return
                    i += 1
    if message.text == "Назад ➤":
        admin(message)
        return -1
    else:
        with open("black_list.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            if direction == 5:
                data['items'] = data['items'] - 1
                try:
                    obj_id = int(message.text)
                except ValueError:
                    bot.send_message(message.chat.id, "Недопустимое значение идентификатора.", reply_markup=None)
                    return 1
                i = 0
                for obj in data['users']:
                    if obj['id'] == obj_id:
                        past_black_user = data['users'][i]
                        del data['users'][i]
                        break
                    i += 1
                database_write(data, "black_list.json")
                with open("user_base.json", "r", encoding="UTF-8") as white_list_base:
                    data = json.loads(white_list_base.read())
                    data['items'] = data['items'] + 1
                    data['users'].append(past_black_user)
                    database_write(data, "user_base.json")
                bot.send_message(message.chat.id, "Готово!", reply_markup=None)
                return 0
            for obj in data['users']:
                bot.send_message(message.chat.id, "id: " + str(obj['id']) + ". Имя: " + obj["first_name"],
                                 reply_markup=None)
            if direction == 1:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Выберите пользователя, которого хотите удалить (id)",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, black_list_handler, 5)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for function in adm_functions:
                    item = types.KeyboardButton(function)
                    markup.add(item)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Полный список доступных пользователей ↑",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, admin_after)


def vacancy_handler(message, direction):
    global new_vacancy_name, vacancy_branch
    if message.text == "Назад ➤":
        admin(message)
        return -1
    if direction == -1:
        vacancy_branch = message.text.strip()
        sent = bot.send_message(message.chat.id, "Принято.\nНапишите должность новой вакансии: ", reply_markup=None)
        bot.register_next_step_handler(sent, vacancy_handler, 0)
    elif direction == 0:
        new_vacancy_name = message.text
        sent = bot.send_message(message.chat.id,
                                "Принято.\nТеперь установим список вопросов. Отправьте сообщение с вопросом.")
        bot.register_next_step_handler(sent, question_handler)
        return
    else:
        with open("vacancy.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            if direction == 5:
                data['items'] = data['items'] - 1
                try:
                    obj_id = int(message.text)
                except ValueError:
                    bot.send_message(message.chat.id, "Недопустимое значение идентификатора.", reply_markup=None)
                    return 1
                for branch in data['vacancies']:
                    i = 0
                    for obj in data['vacancies'][branch]:
                        if obj['id'] == obj_id:
                            del data['vacancies'][branch][i]
                            break
                        i += 1
                    i += 1
                database_write(data, "vacancy.json")
                bot.send_message(message.chat.id, "Готово!", reply_markup=None)
                return 0
            for branch in data['vacancies']:
                bot.send_message(message.chat.id, branch + ":", reply_markup=None)
                for obj in data['vacancies'][branch]:
                    if obj == branch:
                        continue
                    bot.send_message(message.chat.id, "id: " + str(obj['id']) + ". Должность: " + obj["name"],
                                     reply_markup=None)
            if direction == 1:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Выберите вакансию, которую хотите удалить (id)",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, vacancy_handler, 5)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for function in adm_functions:
                    item = types.KeyboardButton(function)
                    markup.add(item)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Полный список доступных вакансий ↑",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, admin_after)


def question_handler(message):
    if message.text == "Назад ➤":
        bot.send_message(message.chat.id, "Принято.", reply_markup=None)
        admin(message)
    elif message.text.lower() == "далее":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Подтвердить")
        item2 = types.KeyboardButton("Назад ➤")
        markup.add(item1, item2)
        sent = bot.send_message(message.chat.id,
                                'Принято.\nЕсли необходимо ввести дополнительную информацию о вакансии, отправьте ее следующим сообщением, иначе — нажмите "Подтвердить".',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, vacancy_add, questions)
    else:
        questions.append(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Далее")
        item2 = types.KeyboardButton("Назад ➤")
        markup.add(item1, item2)
        sent = bot.send_message(message.chat.id,
                                'Принято.\nЕсли это все, напишите "Далее", иначе — отправьте следующий вопрос.',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, question_handler)


def vacancy_add(message, questions):
    all_data = {}
    extraInfo = None
    if message.text == "Назад ➤":
        bot.send_message(message.chat.id, "Принято.", reply_markup=None)
        admin(message)
    else:
        if message.text != "Подтвердить":
            extraInfo = message.text
        with open("vacancy.json", "r", encoding="UTF-8") as vac_base:
            data = json.loads(vac_base.read())
            try:
                branch = data['vacancies'][vacancy_branch]
            except KeyError:
                data['vacancies'][vacancy_branch] = []
                branch = data['vacancies'][vacancy_branch]
            all_data['items'] = data['items'] + 1
            all_data['last_id'] = data['last_id'] + 1
            new_vacancy = {"id": all_data['last_id'], "name": new_vacancy_name, "questions": questions,
                           "extraInfo": extraInfo}
            branch.append(new_vacancy)
            all_data['vacancies'] = data['vacancies']
            database_write(all_data, "vacancy.json")
            del questions
            bot.send_message(message.chat.id, "Готово!", reply_markup=None)


# async def notifications(message=None):
#     if message is not None:
#         if message.text == "Раз в неделю":
#             notifDelay = 604800
#         elif message.text == "Через день":
#             notifDelay = 172800
#         elif message.text == "Каждый день":
#             notifDelay = 86400
#         else:
#             return 1
#         TOKEN = config.TOKEN
#         with open("config.py", "w", encoding="UTF-8") as config_file:
#             config_file.write("TOKEN = '" + TOKEN + "'\nnotifDelay = '" + str(notifDelay) + "'")
#     else:
#         notifDelay = int(config.notifDelay)
#         with open("interviewees.json", "r", encoding="UTF-8") as database:
#             data = json.loads(database.read())
#             f = open("notification.txt", "w", encoding="UTF-8")
#             f.write("")
#             f.close()
#             with open("notification.txt", "a", encoding="UTF-8") as notification_file:
#                 for user in data['users']:
#                     notification_file.write("Филиал: " + user['appForm']['branch'] + ".\nДолжность(название,id): " +
#                                             user['appForm']['vacancy_name'] + ", " + str(user['appForm']['vacancy_id'])
#                                             + ".\nФорма: ")
#                     i = 0
#                     for obj in user['appForm']['answers']:
#                         i += 1
#                         notification_file.write(str(i) + ") Ответ: " + obj['answer'] + "; Время: " + str(obj['time'])
#                                                 + ".\n")
#                     last_name = user['techInfo']['last_name']
#                     username = user['techInfo']['username']
#                     if last_name is None:
#                         last_name = "Не указано"
#                     if username is None:
#                         username = "Не указано"
#                     notification_file.write("|| Контакты >\nID: " + user['techInfo']['id'] + ",\nИмя: " +
#                                             user['techInfo']['first_name'] + ",\nФамилия: " + last_name +
#                                             ",\nЛогин Telegram: " + username +
#                                             ".\n\n----------------------------------------------\n\n")
#         with open("notification.txt", "r", encoding="UTF-8") as notification_file:
#             bot.send_message(admin.id, "Рассылка форм соискателей >")
#             bot.send_document(admin_id, notification_file)
#             time.sleep(notifDelay)
#             notifications()


def q_user(message):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        markup = back_markup()
        bot.send_message(admin_id,
                         "Ошибка: Неверный формат id.\nПроверьте правильность введенных данных и попробуйте снова.",
                         reply_markup=markup)
        return 1
    else:
        sent = bot.send_message(admin_id, "Какой вопрос Вы хотели бы задать?\n(Отправьте его следующим сообщением)")
        bot.register_next_step_handler(sent, mailing, arguments=True, user_id=user_id)


def mailing(message, arguments=None, user_id=None):
    markup = back_markup()
    with open("user_base.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        if arguments:
            if user_id is not None:
                try:
                    sent = bot.send_message(user_id, message.text, reply_markup=markup)
                    bot.register_next_step_handler(sent, feedback, message.text)
                except ApiException:
                    bot.send_message(admin_id,
                                     "Вопрос не был отправлен, т.к. пользователь заблокировал бота или отправка сообщений ему невозможна.",
                                     reply_markup=markup)
                finally:
                    return 0
            for person in data['users']:
                try:
                    if person['id'] != message.from_user.id:
                        sent = bot.send_message(person['id'], message.text, reply_markup=markup)
                        bot.register_next_step_handler(sent, feedback, message.text)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            return 0
        if message.content_type == 'text':
            for person in data['users']:
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_message(person['id'], message.text, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'photo':
            raw = message.photo[2].file_id
            name = "mailing.jpg"
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as photo:
                photo.write(downloaded_file)
            for person in data['users']:
                photo = open(name, "rb")
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_photo(person['id'], photo, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    photo.close()
                    continue
                else:
                    photo.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'document':
            raw = message.document.file_id
            name = "mailing" + message.document.file_name[-4:]
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as document:
                document.write(downloaded_file)
            for person in data['users']:
                document = open(name, "rb")
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_document(person['id'], document, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    document.close()
                    continue
                else:
                    document.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Неподдерживаемый тип файла", reply_markup=markup)


def feedback(message, question):
    bot.send_message(admin_id,
                     'Ответ на Ваш вопрос "' + question + '" — "' + message.text + '" от:\n(id) ' + str(
                         message.from_user.id) + ',\n(name) '
                     + str(message.from_user.first_name))
    bot.send_message(message.chat.id, "Принято.\nБлагодарим за ответ!)")


def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Выбрать филиал")
    markup.add(item)
    return markup


def database_write(data, filename):
    with open(filename, "w", encoding="UTF-8") as database:
        json.dump(data, database, indent=1, ensure_ascii=False, separators=(',', ':'))


def show_database():
    try:
        filename = "interviewees.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "vacancy.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "user_base.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "black_list.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
    except FileNotFoundError:
        bot.send_message(admin_id, '[Ошибка] Файл БД "' + filename + '"не найден.', reply_markup=None)


def initialisation(message):
    pid = message.from_user
    all_data = {}
    filename = "user_base.json"
    with open(filename, "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        for i in data['users']:
            if i['id'] == pid.id:
                break
        else:
            if pid.is_bot:
                bot.send_message(message.chat.id, "Я с ботами не общаюсь : )", reply_markup=None)
                with open("black_list.json", "r", encoding="UTF-8") as blackList:
                    data = json.loads(blackList.read())
                    filename = "black_list.json"
                    black_id.append(pid.id)
            amount = int(data['items']) + 1
            data = data['users']
            user = {"id": pid.id, "first_name": pid.first_name, "last_name": pid.last_name,
                    "username": pid.username, "is_bot": pid.is_bot}
            data.append(user)
            all_data['items'] = amount
            all_data['users'] = data
            database_write(all_data, filename)


bot.polling(none_stop=True)
