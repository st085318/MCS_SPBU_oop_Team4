from src.yandex_organization import find_clubs_in_yandex
from src.test_questions import questions
from src.recommendation import tech_recommendation, art_recommendation, artistic_recommendation, \
    humanitarian_recommendation, sport_recommendation, creative_recommendation, literature_recommendation
from telebot import types
import src.new_database as db
import json
import telebot
import math

# Получаем учётные данные
with open(r"../credentials/credentials.json") as f:
    credentials = json.load(f)[1]
bot = telebot.TeleBot(credentials["telegram_bot_token"])
apikey = credentials["yandex_key"]


@bot.message_handler(commands=['start'])
def start_handler(message):
    # Начало работы бота
    try:
        del_markup = telebot.types.ReplyKeyboardRemove()
        if db.is_user_client_or_club(message.chat.id).is_unknown:
            bot.send_message(message.chat.id, "Здравствуйте, я готов помочь вам с поиском кружков!",
                             reply_markup=del_markup)
            client_name = bot.send_message(message.chat.id, "Как к Вам обращаться?")
            bot.register_next_step_handler(client_name, get_clients_city)
        else:
            markup = telebot.types.ReplyKeyboardMarkup()
            markup.add('Поиск кружков', 'Пройти тест')
            markup.row('Смена локации', 'Личный кабинет')
            bot.send_message(message.chat.id, "Привет, давно не виделись", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=['help'])
def help_information(message):
    # Команда /help, получить список команд
    bot.send_message(message.chat.id,
                     'Поиск кружков:\n\n'
                     'Поиск кружков возможен в радиусе по выбору(если вы до этого поделились геопозицией), '
                     'если радиус не важен(или если вы не поделились геопозицией), '
                     'то поиск будет осущетслен по кружкам в вашем городе.\n\n'
                     'Пройти тест:\n\n'
                     'Тест состоит из 35 вопросов, '
                     'на каждый из которых возможен один из 4х предложенных вариантов ответа. '
                     'Тест НЕВОЗМОЖНО завершить досрочно.\n\n'
                     'Личный кабинет:\n\n'
                     'В личном кабинете находится информация о вас: имя, город и ваша одаренность\n\n'
                     'Смена локации:\n\n'
                     'Предоставляет доступ к вашей текущей геопозиции. Геопозиция будет сохранена, '
                     'для поиска кружков рядом с вами.\n\n'
)


@bot.message_handler(content_types=["location"])
def save_location(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Поиск кружков', 'Пройти тест')
    markup.row('Смена локации', 'Личный кабинет')
    if message.location is not None:
        db.Client.update_field(message.chat.id, "latitude", message.location.latitude)
        db.Client.update_field(message.chat.id, "longitude", message.location.longitude)
        bot.send_message(message.chat.id, "Ваше местоположение обновлено!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Не удалось получить местоположение!", reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def react_photo(message):
    bot.send_message(message.chat.id, "Красиво, но я не знаю, что с этим делать ¯\\_(ツ)_/¯")


# Команды, совершаемые ботом


def bot_start_test(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Да', 'Нет')
    msg = bot.send_message(message.chat.id, "Вы собираетесь пройти тестирование для определения рода Ваших "
                                            "занятий.\n"
                                            "Тест не очень длинный, но может занять некоторое время.\n"
                                            "Повторное прохождение теста перезапишет Ваши предпочтения.\n"
                                            "Приступить?", reply_markup=markup)
    bot.register_next_step_handler(msg, member_test)


@bot.message_handler(content_types=['text'])
def read_messages(message):
    # В зависимости от нажатой кнопки, бот выполнит определенную команду
    if message.text == "Личный кабинет":
        personal_account(message)
    elif message.text == "Смена локации":
        bot_get_location(message)
    elif message.text == "Пройти тест":
        bot_start_test(message)
    elif message.text == "Поиск кружков":
        get_search_border(message)
    else:

        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add('Поиск кружков', 'Пройти тест')
        markup.row('Смена локации', 'Личный кабинет')

        bot.send_message(message.chat.id, "Простите, я не знаю такой команды...", reply_markup=markup)


def personal_account(message):
    def tag_from_db_to_word(tag_name):
        if tag_name == "art":
            return "Искусство"
        elif tag_name == "sport":
            return "Спорт"
        elif tag_name == "tech":
            return "Технические науки"
        elif tag_name == "creative":
            return "Творческая одаренность"
        elif tag_name == "artistic":
            return "Артистическая одаренность"
        elif tag_name == "literature":
            return "Литературная одаренность одаренность"
        elif tag_name == "humanitarian":
            return "Гуманитарные науки"

    account_markup = telebot.types.ReplyKeyboardMarkup()
    account_markup.add('Изменить имя', 'Изменить город')
    account_markup.row('Выйти в меню')
    name = db.Client.get_name(message.chat.id)
    city = db.Client.get_city(message.chat.id)
    talents = get_talent(message.chat.id)
    client_talents = ""
    for talent in talents:
        if talent[0] >= 8 or talent[1] == talents[-1][1]:
            client_talents += " " + tag_from_db_to_word(talent[1]) + "\n"
    bot.send_message(message.chat.id, f"Имя:{name}\nГород:{city}\nТаланты:{client_talents}")
    msg = bot.send_message(message.chat.id, "Хотите что-то изменить?", reply_markup= account_markup)
    bot.register_next_step_handler(msg, change_account_info)


def change_account_info(message):
    del_markup = telebot.types.ReplyKeyboardRemove()
    if message.text == "Изменить имя":
        name_msg = bot.send_message(message.chat.id, "Введите новое имя", reply_markup= del_markup)
        bot.register_next_step_handler(name_msg, change_name)
    elif message.text == "Изменить город":
        city_msg = bot.send_message(message.chat.id, "Введите новый город", reply_markup= del_markup)
        bot.register_next_step_handler(city_msg, change_city)
    else:
        start_markup = telebot.types.ReplyKeyboardMarkup()
        start_markup.add('Поиск кружков', 'Пройти тест')
        start_markup.row('Смена локации', 'Личный кабинет')
        bot.send_message(message.chat.id, "Вы вышли в меню", reply_markup=start_markup)
        return


def change_name(message):
    db.Client.update_field(message.chat.id, "client_name", message.text)
    bot.send_message(message.chat.id, "Данные обновлены!")
    start_markup = telebot.types.ReplyKeyboardMarkup()
    start_markup.add('Поиск кружков', 'Пройти тест')
    start_markup.row('Смена локации', 'Личный кабинет')
    bot.send_message(message.chat.id, "Вы вышли в меню", reply_markup=start_markup)


def change_city(message):
    db.Client.update_field(message.chat.id, "city", message.text)
    bot.send_message(message.chat.id, "Данные обновлены!")
    start_markup = telebot.types.ReplyKeyboardMarkup()
    start_markup.add('Поиск кружков', 'Пройти тест')
    start_markup.row('Смена локации', 'Личный кабинет')
    bot.send_message(message.chat.id, "Вы вышли в меню", reply_markup=start_markup)


def bot_get_location(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение",
                     reply_markup=keyboard)


def member_test(message, test_step=0):
    # Тест по выяснению предпочтений, вопросы берутся из текстового файла. При определенных ответах
    # У участника изменяются соответсвующие значения тегов
    try:
        def you_good_at(user_id):
            talent = get_talent(user_id)[-1][1]
            if talent == "art":
                return "А Вы хороши в Искусстве!"
            elif talent == "sport":
                return "Да ты будущая звезда Спорта!"
            elif talent == "tech":
                return "Мне кажется, что ты увлекаешься техническими науками!"
            elif talent == "creative":
                return "У тебя явная творческая одаренность"
            elif talent == "artistic":
                return "Да ты будущий артист!"
            elif talent == "literature":
                return "Похоже, что ты умеешь обращаться с словом!"
            elif talent == "humanitarian":
                return "Мне кажется, что ты увлекаешься гуманитарными науками!"

        def next_step():
            if test_step == 35:
                del_markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, "Тест пройден, информация сохранена!", reply_markup=del_markup)
                mark = telebot.types.ReplyKeyboardMarkup()
                mark.add('Поиск кружков', 'Пройти тест')
                mark.row('Смена локации', 'Личный кабинет')
                bot.send_message(message.chat.id, you_good_at(message.chat.id), reply_markup=mark)
                return
            else:
                msg = bot.send_message(message.chat.id, questions[test_step], reply_markup=markup)
                bot.register_next_step_handler(msg, member_test, test_step + 1)

        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add('Точно да', 'Скорее да')
        markup.row('Затрудняюсь ответить', 'Скорее нет')
        if test_step == 0:
            if message.text == 'Да':
                db.Tag.set_tags(message.chat.id, 0, 0, 0, 0, 0, 0, 0)
                msg = bot.send_message(message.chat.id, questions[0], reply_markup=markup)
                bot.register_next_step_handler(msg, member_test, test_step + 1)
            elif message.text == 'Нет':
                start_markup = telebot.types.ReplyKeyboardMarkup()
                start_markup.add('Поиск кружков', 'Пройти тест')
                start_markup.row('Смена локации', 'Личный кабинет')
                bot.send_message(message.chat.id, "Отмена теста.", reply_markup=start_markup)
                return
        elif message.text == 'Точно да':
            if test_step % 7 == 0:
                db.Tag.add_tags(message.chat.id, 0, 2, 0, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 1:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, 0, 2)
                next_step()
            elif test_step % 7 == 2:
                db.Tag.add_tags(message.chat.id, 2, 0, 0, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 3:
                db.Tag.add_tags(message.chat.id, 0, 0, 2, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 4:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 2, 0, 0, 0)
                next_step()
            elif test_step % 7 == 5:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, 2, 0)
                next_step()
            elif test_step % 7 == 6:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 2, 0, 0)
                next_step()
        elif message.text == 'Скорее да':
            if test_step % 7 == 0:
                db.Tag.add_tags(message.chat.id, 0, 1, 0, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 1:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, 0, 1)
                next_step()
            elif test_step % 7 == 2:
                db.Tag.add_tags(message.chat.id, 1, 0, 0, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 3:
                db.Tag.add_tags(message.chat.id, 0, 0, 1, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 4:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 1, 0, 0, 0)
                next_step()
            elif test_step % 7 == 5:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, 1, 0)
                next_step()
            elif test_step % 7 == 6:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 1, 0, 0)
                next_step()
        elif message.text == 'Затрудняюсь ответить':
            db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, 0, 0)
            next_step()
        elif message.text == 'Скорее нет':
            if test_step % 7 == 0:
                db.Tag.add_tags(message.chat.id, 0, -1, 0, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 1:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, 0, -1)
                next_step()
            elif test_step % 7 == 2:
                db.Tag.add_tags(message.chat.id, -1, 0, 0, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 3:
                db.Tag.add_tags(message.chat.id, 0, 0, -1, 0, 0, 0, 0)
                next_step()
            elif test_step % 7 == 4:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, -1, 0, 0, 0)
                next_step()
            elif test_step % 7 == 5:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, 0, -1, 0)
                next_step()
            elif test_step % 7 == 6:
                db.Tag.add_tags(message.chat.id, 0, 0, 0, 0, -1, 0, 0)
                next_step()
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите один из предложенных вариантов.",
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, member_test, test_step)
        return
    except BaseException as e:
        print(e)


def get_clients_city(message):
    client_name = message.text
    city = bot.send_message(message.chat.id, "Из какого вы города?")
    bot.register_next_step_handler(city, add_client, client_name)


def add_client(message, client_name):
    # Добавление клиента в бд(сама регистрация)
    user_id = message.from_user.id
    db.Client.add_new_client(user_id, client_name, message.text)
    bot.send_message(message.chat.id, "Поздравляем, " + client_name + ".")
    bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
    markup = telebot.types.ReplyKeyboardMarkup()

    markup.add('Поиск кружков', 'Пройти тест')
    markup.row('Смена локации', 'Личный кабинет')
    bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду /help", reply_markup=markup)


def get_search_border(message):
    try:
        if db.Client.get_location(message.chat.id)["latitude"] is not None:
            markup = telebot.types.ReplyKeyboardMarkup()
            markup.add('1 км', '3 км')
            markup.row('5 км', 'Не имеет значения')
            msg = bot.send_message(message.chat.id, "Хотите ограничить область поиска кружков?", reply_markup=markup)
            bot.register_next_step_handler(msg, get_search_mode)
        else:
            get_search_mode(message)
    except BaseException as e:
        print(e)


def get_search_mode(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Рекомендованные кружки', 'Написать запрос самостоятельно')
    # markup.row('Выбрать из рекомендованных категорий')
    msg = bot.send_message(message.chat.id, "Выберите режим поиска", reply_markup=markup)
    bot.register_next_step_handler(msg, form_query_from_mode, message.text)


def get_talent(user_id):
    talents = db.Tag.get_tags(user_id)
    sorted_talents = []
    for key, value in talents.items():
        sorted_talents.append([value, key])
    sorted_talents.sort()
    return sorted_talents


def form_queries_from_tags(user_id):
    # Формирование запроса по тегам пользователя
    talent = get_talent(user_id)[-1][1]
    queries = []
    if talent == "art":
        queries = art_recommendation
    elif talent == "sport":
        queries = sport_recommendation
    elif talent == "tech":
        queries = tech_recommendation
    elif talent == "creative":
        queries = creative_recommendation
    elif talent == "artistic":
        queries = artistic_recommendation
    elif talent == "literature":
        queries = literature_recommendation
    elif talent == "humanitarian":
        queries = humanitarian_recommendation
    return queries


def get_recomm_clubs(location: {}, client_city: str, queries: []) -> []:
    clubs = []
    for query in queries:
        clubs.append(find_clubs_in_yandex(apikey, location, client_city, query))
    recommendation_clubs = []
    for i in range(10):
        for list_clubs in clubs:
            if i < len(list_clubs):
                recommendation_clubs.append(list_clubs[i])
    return recommendation_clubs


def form_query_from_mode(message, radius_search):
    if radius_search == "1 км" or radius_search == "3 км" or radius_search == "5 км":
        radius_search = float(radius_search[0])
        earth_rad = float(6371)
        client_location = db.Client.get_location(message.chat.id)
        r = math.sqrt(1 - (abs(client_location["latitude"]) / float(90)) ** 2) * earth_rad
        latitude_degree = float(180 * radius_search) / 40075.696
        longitude_degree = float(180 * radius_search) / float(2 * math.pi * r)
        location = {"longitude": client_location["longitude"],
                    "latitude": client_location["latitude"],
                    "latitude_degree": latitude_degree, "longitude_degree": longitude_degree}
    else:
        location = {"longitude": None,
                    "latitude": None,
                    "latitude_degree": None, "longitude_degree": None}
    if message.text == "Рекомендованные кружки":
        try:
            bot_show_clubs(message, location, form_queries_from_tags(message.chat.id))
        except BaseException as e:
            print(e)
    elif message.text == "Написать запрос самостоятельно":
        del_markup = telebot.types.ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, 'Введите запрос', reply_markup=del_markup)
        bot.register_next_step_handler(msg, bot_show_clubs, location, None)


def bot_show_clubs(message, location, query=None):
    client_city = db.Client.get_city(message.chat.id)
    try:
        if query is not None:
            clubs = get_recomm_clubs(location, client_city, query)
        else:
            query = message.text
            clubs = find_clubs_in_yandex(apikey, location, client_city, query)
    except BaseException as e:
        print(e)
    del_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "А вот и они", reply_markup=del_markup)
    number_of_club = 0
    page_size = 5
    club_to_show_in_message = ""
    for club in clubs:
        number_of_club += 1
        club_to_show_in_message += club
        if number_of_club == page_size:
            break
    if club_to_show_in_message:
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add('Выйти в меню', "Далее >")
        msg = bot.send_message(message.chat.id, club_to_show_in_message, reply_markup=markup)
        bot.register_next_step_handler(msg, show_clubs_from_yandex, clubs, page_size)
    else:
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add('Поиск кружков', 'Пройти тест')
        markup.row('Смена локации', 'Личный кабинет')
        bot.send_message(message.chat.id, "Простите, подходящих кружков не найдено", reply_markup=markup)


def show_clubs_from_yandex(message, clubs, number_of_club):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Поиск кружков', 'Пройти тест')
    markup.row('Смена локации', 'Личный кабинет')
    if number_of_club >= len(clubs):
        bot.send_message(message.chat.id, "Больше кружков не найдено", reply_markup=markup)
    else:
        if message.text == 'Выйти в меню':
            bot.send_message(message.chat.id, "Вы перешли в меню", reply_markup=markup)
            return
        elif message.text == "Далее >":
            club_to_show_in_message = "\n".join([club for club in clubs[number_of_club:number_of_club + 5]])
            number_of_club += 5
            markup = telebot.types.ReplyKeyboardMarkup()
            markup.add('Выйти в меню', "Далее >")
            msg = bot.send_message(message.chat.id, club_to_show_in_message, reply_markup=markup)
            bot.register_next_step_handler(msg, show_clubs_from_yandex, clubs, number_of_club)
        else:
            bot.send_message(message.chat.id, "Я вас не понимаю", reply_markup=markup)


'''
def join_club(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Тест', 'Другие кружки')
    if message.text == "esc":
        bot.send_message(message.chat.id, "Вы записаны!", reply_markup=markup)
    else:
        club_id = db.Club.get_id_from_name(message.text)
        if club_id is None:
            bot.send_message(message.chat.id, "Такого клуба нет", reply_markup=markup)
        else:
            db.Membership.add_member_to_club(int(club_id), message.chat.id)
            bot.send_message(int(club_id), "К вам записался " + str(db.Client.get_name(int(message.chat.id))))
            bot.send_message(message.chat.id, "Вы записаны!", reply_markup=markup)


def quit_from_club(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Тест', 'Другие кружки')
    club_id = db.Club.get_id_from_name(message.text)
    if club_id is None:
        bot.send_message(message.chat.id, "Вы не ходили на такой клуб", reply_markup=markup)
    else:
        db.Membership.out_member_from_club(int(club_id), message.chat.id)
        bot.send_message(int(club_id), "От вас ушёл " + str(db.Client.get_name(int(message.chat.id))))
        bot.send_message(message.chat.id, "Вы ушли от " + message.text, reply_markup=markup)



def get_name_to_register(message):
    # Сначала получаем имя/название, а потом регистрируем
    try:
        del_markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Мы рады быть полезными Вам!", reply_markup=del_markup)
        client_name = bot.send_message(message.chat.id, "Как к Вам обращаться?")
        bot.register_next_step_handler(client_name, get_clients_city)
    except Exception as e:
        bot.reply_to(message, e)
'''

if __name__ == '__main__':
    db.create_db()
    bot.polling(none_stop=True)
