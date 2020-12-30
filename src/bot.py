from src.yandex_organization import find_clubs_in_yandex
from src.test_questions import questions
import src.new_database as db
import json
import telebot

# получаем учётные данные
with open(r"../credentials/credentials.json") as f:
    credentials = json.load(f)[1]
bot = telebot.TeleBot(credentials["telegram_bot_token"])
apikey = credentials["yandex_key"]


@bot.message_handler(commands=['start'])
def start_handler(message):
    # начало работы бота
    msg = bot.send_message(message.chat.id, "Привет, не болей!")
    if db.is_user_client_or_club(message.chat.id).is_unknown:
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row('Я ищу кружок')
        markup.row('Я есть кружок')
        bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
        bot.register_next_step_handler(msg, get_name_to_register)


@bot.message_handler(commands=['help'])
def help_information(message):
    # команда /help, получить список команд
    bot.send_message(message.chat.id, "It's help!")
    if db.is_user_client_or_club(message.chat.id).is_club:
        bot.send_message(message.chat.id, 'Отправьте: \n"Описание", чтобы изменить описание своего клуба\n'
                                          '"Участники", чтобы узнать список участников клуба')
    else:
        bot.send_message(message.chat.id, 'Нажмите: \n'
                                          '"Записаться", записаться на клуб-партнер\n'
                                          '"Уйти", чтобы уйти из клуба-партнера\n'
                                          '"Тест", чтобы пройти тест на определение предпочтений\n'
                                          '"Другие кружки", чтобы увидеть подходящие кружки из Яндекса')


# команды, совершаемые ботом
def bot_new_description(message):
    del_markup = telebot.types.ReplyKeyboardRemove()
    msg = bot.send_message(message.chat.id, "Введите новое описание", reply_markup=del_markup)
    bot.register_next_step_handler(msg, add_club_description)


def bot_clubs_and_info(message):
    clubs = db.Club.get_clubs_to_join()
    clubs_of_your_city = []
    for club in clubs:
        if club.city == db.Client.get_city(message.chat.id):
            description = str(club.description)
            if club.description is None:
                description = "Описание не предоставлено"

            one_more_club = ':\n'.join([str(club.name), description])
            clubs_of_your_city.append(one_more_club)
    ans = '\n\n'.join(clubs_of_your_city)
    if ans:
        del_markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Список клубов и их описание. "
                                          "Введите название клуба, "
                                          "если хотетите записаться, или esc, чтобы выйти из режима записи",
                         reply_markup=del_markup)
        msg = bot.send_message(message.chat.id, ans)

        bot.register_next_step_handler(msg, join_club)
    else:
        bot.send_message(message.chat.id, "У нас пока нет кружков в вашем городе(")


def bot_quit_from_club(message):
    del_markup = telebot.types.ReplyKeyboardRemove()
    msg = bot.send_message(message.chat.id, "Введите название клуба, который вы хотите покинуть",
                           reply_markup=del_markup)
    bot.register_next_step_handler(msg, quit_from_club)


def bot_start_test(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Да', 'Нет')
    msg = bot.send_message(message.chat.id, "Вы собираетесь пройти тестирование для определения рода Ваших "
                                            "занятий.\n"
                                            "Тест не очень длинный, но может занять некоторое время.\n"
                                            "Повторное прохождение теста перезапишет Ваши предпочтения.\n"
                                            "Приступить?", reply_markup=markup)
    bot.register_next_step_handler(msg, member_test)


def bot_show_other_clubs(message):
    tag_query = form_query_from_tags(message.from_user.id)
    clubs = find_clubs_in_yandex(apikey, db.Client.get_city(message.chat.id), tag_query)
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
        markup.add('Записаться', 'Уйти')
        markup.row('Фамилия', 'Другие кружки')
        markup.row('Тест')
        bot.send_message(message.chat.id, "Простите, подходящих кружков не найдено", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def read_messages(message):
    # в зависимости от нажатой кнопки, бот выполнит определенную команду
    if db.is_user_client_or_club(message.chat.id).is_club:
        if message.text == "Описание":
            bot_new_description(message)
        elif message.text == "Участники":
            members = db.Membership.get_id_members_of_club(message.chat.id)
            if members is None:
                bot.send_message(message.chat.id, "У вас нет членов")
            else:
                members = '\n'.join(members.split(";"))
                bot.send_message(message.chat.id, str(members))
        else:
            bot.send_message(message.chat.id, "Простите, я не знаю такой команды...")
    elif db.is_user_client_or_club(message.chat.id).is_client:
        if message.text == "Записаться":
            bot_clubs_and_info(message)
        elif message.text == "Уйти":
            bot_quit_from_club(message)
        elif message.text == "Тест":
            bot_start_test(message)
        elif message.text == "Другие кружки":
            bot_show_other_clubs(message)
        else:
            markup = telebot.types.ReplyKeyboardMarkup()
            markup.add('Записаться', 'Уйти')
            markup.row('Тест', 'Другие кружки')
            bot.send_message(message.chat.id, "Простите, я не знаю такой команды...", reply_markup=markup)


def member_test(message, test_step=0):
    # тест по выяснению предпочтений, вопросы берутся из текстового файла. При определенных ответах
    # у участника изменяются соответсвующие значения тегов
    try:
        if message.text == 'Да':
            if test_step == 0:
                db.Tag.set_tags(message.from_user.id, 0, 0, 0)
            elif test_step == 1:
                db.Tag.add_tags(message.from_user.id, 0, 2, 0)
            elif test_step == 2:
                db.Tag.add_tags(message.from_user.id, 2, 0, 0)
            elif test_step == 3:
                db.Tag.add_tags(message.from_user.id, 0, 1, 0)
                db.Tag.add_tags(message.from_user.id, 0, 0, 2)
            elif test_step == 4:
                db.Tag.add_tags(message.from_user.id, 0, 0, 1)
                db.Tag.add_tags(message.from_user.id, 2, 0, 0)
            elif test_step == 5:
                db.Tag.add_tags(message.from_user.id, 0, 0, 2)
            elif test_step == 6:
                db.Tag.add_tags(message.from_user.id, 0, 0, 1)
                db.Tag.add_tags(message.from_user.id, 0, 2, 0)
            elif test_step == 7:
                db.Tag.add_tags(message.from_user.id, 0, 0, 2)
            elif test_step == 8:
                db.Tag.add_tags(message.from_user.id, 2, 0, 0)
            elif test_step == 9:
                db.Tag.add_tags(message.from_user.id, 0, 2, 0)
            elif test_step == 10:
                db.Tag.add_tags(message.from_user.id, 0, 0, 2)
                db.Tag.add_tags(message.from_user.id, 0, 1, 0)
            pass
        elif message.text == 'Нет':
            if test_step == 0:
                markup = telebot.types.ReplyKeyboardMarkup()
                markup.add('Записаться', 'Уйти')
                markup.row('Тест', 'Другие кружки')
                bot.send_message(message.chat.id, "Отмена теста.", reply_markup=markup)
                return
            elif test_step == 1:
                pass
            elif test_step == 2:
                db.Tag.add_tags(message.from_user.id, -1, 0, 0)
            elif test_step == 3:
                db.Tag.add_tags(message.from_user.id, -1, 0, 0)
            elif test_step == 4:
                db.Tag.add_tags(message.from_user.id, -1, 0, 0)
            elif test_step == 5:
                pass
            elif test_step == 6:
                db.Tag.add_tags(message.from_user.id, 0, -1, 0)
            elif test_step == 7:
                pass
            elif test_step == 8:
                db.Tag.add_tags(message.from_user.id, -1, 0, 0)
            elif test_step == 9:
                db.Tag.add_tags(message.from_user.id, 0, -1, 0)
            elif test_step == 10:
                pass
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите один из предложенных вариантов.")
            bot.register_next_step_handler(msg, member_test, test_step)
            return

        if test_step == 0:
            msg = bot.send_message(message.chat.id, questions[0])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
            return
        elif test_step == 1:
            msg = bot.send_message(message.chat.id, questions[1])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 2:
            msg = bot.send_message(message.chat.id, questions[2])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 3:
            msg = bot.send_message(message.chat.id, questions[3])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 4:
            msg = bot.send_message(message.chat.id, questions[4])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 5:
            msg = bot.send_message(message.chat.id, questions[5])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 6:
            msg = bot.send_message(message.chat.id, questions[6])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 7:
            msg = bot.send_message(message.chat.id, questions[7])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 8:
            msg = bot.send_message(message.chat.id, questions[8])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 9:
            msg = bot.send_message(message.chat.id, questions[9])
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 10:
            del_markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Тест пройден, информация сохранена!", reply_markup=del_markup)
            mark = telebot.types.ReplyKeyboardMarkup()
            mark.add('Записаться', 'Уйти')
            mark.row('Тест', 'Другие кружки')
            bot.send_message(message.chat.id, "А вы хороши!", reply_markup=mark)
            return
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(content_types=['photo'])
def react_photo(message):
    bot.send_message(message.chat.id, "Красиво, но я не знаю, что с этим делать ¯\\_(ツ)_/¯")


def get_name_to_register(message):
    # сначала получаем имя/название, а потом регистрируем
    try:
        del_markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Мы рады быть полезными Вам!", reply_markup=del_markup)
        if message.text == 'Я ищу кружок':
            client_name = bot.send_message(message.chat.id, "Как к Вам обращаться?")
            bot.register_next_step_handler(client_name, get_clients_city)
        elif message.text == 'Я есть кружок':
            club_name = bot.send_message(message.chat.id, "Как называется Ваш кружок?")
            bot.register_next_step_handler(club_name, get_clubs_name)
            print(message.chat.id)
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите один из предложенных вариантов.")
            bot.register_next_step_handler(msg, get_name_to_register)
            return
    except Exception as e:
        bot.reply_to(message, e)


def get_clients_city(message):
    client_name = message.text
    city = bot.send_message(message.chat.id, "Из какого вы города?")
    bot.register_next_step_handler(city, add_client, client_name)


def add_client(message, client_name):
    # добавление клиента в бд(сама регистрация)
    user_id = message.from_user.id
    db.Client.add_new_client(user_id, client_name, message.text)
    bot.send_message(message.chat.id, "Поздравляем, " + client_name + ".")
    bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Тест', 'Другие кружки')
    bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду /help", reply_markup=markup)


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


def add_club_description(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Участники')
    markup.row('Описание')
    db.Club.update_field(message.chat.id, "description", message.text)
    bot.send_message(message.chat.id, "Описание клуба изменено", reply_markup=markup)


def get_clubs_name(message):
    club_name = message.text
    club_with_name_exists = db.Club.get_id_from_name(club_name)
    if club_with_name_exists is None:
        city = bot.send_message(message.chat.id, "Из какого вы города?")
        bot.register_next_step_handler(city, add_club, club_name)
    else:
        bot.send_message(message.chat.id,
                         "Кружок с таким именем уже существует - придумайте другое название")
        bot.register_next_step_handler(message.chat.id, get_clubs_name)


def add_club(message, club_name):
    # сама регистрация клуба(добавление в бд)
    user_id = message.from_user.id
    db.Club.add_new_club(user_id, club_name, message.text)
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Спорт')
    markup.row('Наука')
    markup.row('Искусство')
    msg = bot.send_message(message.chat.id, "К какому направлению относится Ваш клуб?", reply_markup=markup)
    bot.register_next_step_handler(msg, add_club_tags)


def add_club_tags(message):
    try:
        if message.text == 'Спорт':
            tags = {"art": 0, "sport": 3, "science": 0}
        elif message.text == 'Наука':
            tags = {"art": 0, "sport": 0, "science": 3}
        elif message.text == 'Искусство':
            tags = {"art": 3, "sport": 0, "science": 0}
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите один из предложенных вариантов.")
            bot.register_next_step_handler(msg, add_club_tags)
            return
        db.Tag.set_tags(message, tags["sport"], tags["science"], tags["art"])
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row('Участники')
        markup.row('Описание')
        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
        bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду /help", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, e)


def show_clubs_from_yandex(message, clubs, number_of_club):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Тест', 'Другие кружки')
    if number_of_club >= len(clubs):
        bot.send_message(message.chat.id, "Больше кружков не найдено", reply_markup=markup)
    else:
        if message.text == 'Выйти в меню':
            bot.send_message(message.chat.id, "Вы перешли в меню", reply_markup=markup)
        elif message.text == "Далее >":
            club_to_show_in_message = "\n".join([club for club in clubs[number_of_club:number_of_club+5]])
            number_of_club += 5
            markup = telebot.types.ReplyKeyboardMarkup()
            markup.add('Выйти в меню', "Далее >")
            msg = bot.send_message(message.chat.id, club_to_show_in_message, reply_markup=markup)
            bot.register_next_step_handler(msg, show_clubs_from_yandex, clubs, number_of_club)
        else:
            bot.send_message(message.chat.id, "Я вас не понимаю", reply_markup=markup)


def form_query_from_tags(user_id):
    # формирование запроса по тегам пользователя
    tags = db.Tag.get_tags(user_id)
    for field in ["art", "sport", "science"]:
        if tags[field] is None:
            tags[field] = 0
    best_tag = max(tags, key=tags.get)
    if best_tag == "science":
        return "Образовательный центр"
    elif best_tag == "art":
        return "Центр творчества"
    else:
        return "Секция"


if __name__ == '__main__':
    db.create_db()
    bot.polling(none_stop=True)
