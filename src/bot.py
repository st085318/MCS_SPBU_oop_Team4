import os
import sys
import telebot
import ast
from telebot import types
from string import Template
import src.database as db

# Telegram your token
bot = telebot.TeleBot("")


@bot.message_handler(commands=['start'])
def start_handler(message):
    msg = bot.send_message(message.chat.id, "Привет, не болей!")
    if db.is_user_client_or_club(message.chat.id) is None:
        markup = types.ReplyKeyboardMarkup()
        markup.row('Я ищу кружок')
        markup.row('Я есть кружок')
        bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
        bot.register_next_step_handler(msg, get_name_to_register)


@bot.message_handler(commands=['help'])
def help_information(message):
    bot.send_message(message.chat.id, "It's help!")
    if db.is_user_client_or_club(message.chat.id) == 1:
        msg = bot.send_message(message.chat.id, 'Отправьте: \n"Описание", чтобы изменить описание своего клуба\n'
                                                '"Участники", чтобы узнать список участников клуба')
    else:
        msg = bot.send_message(message.chat.id, 'Отправьте: \n'
                                                '"Фамилия", чтобы поменять свою фамилию\n'
                                                '"Записаться", записаться на клуб\n'
                                                '"Уйти", чтобы уйти из клуба')


@bot.message_handler(content_types=['text'])
def read_messages(message):
    if db.is_user_client_or_club(message.chat.id) == 1:
        if message.text == "Описание":
            del_markup = types.ReplyKeyboardRemove()
            msg = bot.send_message(message.chat.id, "Введите новое описание", reply_markup=del_markup)
            bot.register_next_step_handler(msg, add_club_description)
        # elif message.text == "Название":
        #    msg = bot.send_message(message.chat.id, "Введите новое название")
        #    bot.register_next_step_handler(msg, add_club_name)
        elif message.text == "Участники":
            members = db.get_id_members_of_club(message.chat.id)
            if members is None:
                bot.send_message(message.chat.id, "У вас нет членов")
            else:
                list_of_members = members.split(";")
                members = ""
                for member in list_of_members:
                    members += db.get_name_from_client_id(int(member)) + "\n"
                bot.send_message(message.chat.id, str(members))
        else:
            bot.send_message(message.chat.id, "Простите, я не знаю такой команды...")
    elif db.is_user_client_or_club(message.chat.id) == 2:
        if message.text == "Фамилия":
            del_markup = types.ReplyKeyboardRemove()
            msg = bot.send_message(message.chat.id, "Введите новую фамилию", reply_markup=del_markup)
            bot.register_next_step_handler(msg, add_client_surname)
        elif message.text == "Записаться":
            clubs = db.get_clubs_to_join()
            ans = ""
            for key, value in clubs.items():
                if value is None:
                    value = "Описание не предоставлено"
                ans += str(key) + ":\n" + str(value) + "\n\n"
            del_markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Список клубов и их описание. "
                                              "Введите название клуба, "
                                              "если хотетите записаться, или esc, чтобы выйти из режима записи",
                             reply_markup=del_markup)
            msg = bot.send_message(message.chat.id, ans)

            bot.register_next_step_handler(msg, join_to_club)
        elif message.text == "Уйти":
            del_markup = types.ReplyKeyboardRemove()
            msg = bot.send_message(message.chat.id, "Введите название клуба, который вы хотите покинуть",
                                   reply_markup=del_markup)
            bot.register_next_step_handler(msg, quit_from_club)
        elif message.text == "Тест":
            markup = types.ReplyKeyboardMarkup()
            markup.row('Да', 'Нет')
            msg = bot.send_message(message.chat.id, "Вы собираетесь пройти тестирование для определения рода Ваших "
                                                    "занятий.\n"
                                                    "Тест не очень длинный, но может занять некоторое время.\n"
                                                    "Повторное прохождение теста перезапишет Ваши предпочтения.\n"
                                                    "Приступить?", reply_markup=markup)
            bot.register_next_step_handler(msg, member_test)
        else:
            bot.send_message(message.chat.id, "Простите, я не знаю такой команды...")


def member_test(message, test_step=0):
    try:
        if message.text == 'Да':
            if test_step == 0:
                db.clear_client_tags(message.from_user.id)
            elif test_step == 1:
                db.add_science_client_tag(message.from_user.id, 2)
            elif test_step == 2:
                db.add_sport_client_tag(message.from_user.id, 2)
            elif test_step == 3:
                db.add_science_client_tag(message.from_user.id, 1)
                db.add_art_client_tag(message.from_user.id, 2)
            elif test_step == 4:
                db.add_art_client_tag(message.from_user.id, 1)
                db.add_sport_client_tag(message.from_user.id, 2)
            elif test_step == 5:
                db.add_art_client_tag(message.from_user.id, 2)
            elif test_step == 6:
                db.add_art_client_tag(message.from_user.id, 1)
                db.add_science_client_tag(message.from_user.id, 2)
            elif test_step == 7:
                db.add_art_client_tag(message.from_user.id, 2)
            elif test_step == 8:
                db.add_sport_client_tag(message.from_user.id, 2)
            elif test_step == 9:
                db.add_science_client_tag(message.from_user.id, 2)
            elif test_step == 10:
                db.add_art_client_tag(message.from_user.id, 2)
                db.add_science_client_tag(message.from_user.id, 1)
            # bot.register_next_step_handler(client_name, add_client)
            pass
        elif message.text == 'Нет':
            if test_step == 0:
                del_markup = types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, "Отмена теста.", reply_markup=del_markup)
                return
            elif test_step == 1:
                pass
            elif test_step == 2:
                db.add_sport_client_tag(message.from_user.id, -1)
            elif test_step == 3:
                db.add_sport_client_tag(message.from_user.id, -1)
            elif test_step == 4:
                db.add_sport_client_tag(message.from_user.id, -1)
            elif test_step == 5:
                pass
            elif test_step == 6:
                db.add_science_client_tag(message.from_user.id, -1)
            elif test_step == 7:
                pass
            elif test_step == 8:
                db.add_sport_client_tag(message.from_user.id, -1)
            elif test_step == 9:
                db.add_science_client_tag(message.from_user.id, -1)
            elif test_step == 10:
                pass
            # bot.register_next_step_handler(club_name, add_club)
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите один из предложенных вариантов.")
            bot.register_next_step_handler(msg, member_test, test_step)
            return

        if test_step == 0:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Учитесь новым знаниям очень быстро, схватывая всё на лету?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
            return
        elif test_step == 1:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Энергичны и нуждаетесь в большом объёме движений?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 2:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Часто читаете художественную литературу?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 3:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Имеете хорошую координацию движений?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 4:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Хорошо поёте?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 5:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Часто читаете научную или научно-популярную литературу?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 6:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Любите выражать свои чувства через лепку/рисование?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 7:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Предпочитаете проводить свободное время в подвижных играх?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 8:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Умеете составлять умозаключения?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 9:
            msg = bot.send_message(message.chat.id, "Вы можете сказать про себя, что Вы:\n"
                                                    "Сочиняете рассказы или стихи?")
            bot.register_next_step_handler(msg, member_test, test_step + 1)
        elif test_step == 10:
            del_markup = types.ReplyKeyboardRemove()
            msg = bot.send_message(message.chat.id, "Тест пройден, информация сохранена!", reply_markup=del_markup)
            return
        # club_name = bot.send_message(message.chat.id, "Как называется ваш кружок?")
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(content_types=['photo'])
def react_photo(message):
    bot.send_message(message.chat.id, "So beautiful!")


def get_name_to_register(message):
    # сначала получаем имя/название, а потом регистрируем
    try:
        del_markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Мы рады быть полезными Вам!", reply_markup=del_markup)
        if message.text == 'Я ищу кружок':
            client_name = bot.send_message(message.chat.id, "Как к Вам обращаться?")
            bot.register_next_step_handler(client_name, add_client)
        elif message.text == 'Я есть кружок':
            club_name = bot.send_message(message.chat.id, "Как называется Ваш кружок?")
            bot.register_next_step_handler(club_name, add_club)
            print(message.chat.id)
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите один из предложенных вариантов.")
            bot.register_next_step_handler(msg, get_name_to_register)
            return
        # only on Saturday
    except Exception as e:
        bot.reply_to(message, e)


def add_client(message):
    # добавление клиента в бд(сама регистрация)
    user_id = message.from_user.id
    db.add_new_client(user_id, message.text)
    bot.send_message(message.chat.id, "Поздравляем, " + message.text + ".")
    bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
    markup = types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Фамилия')
    markup.row('Тест')
    bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду /help", reply_markup=markup)


def add_client_surname(message):
    db.update_user_data(message.chat.id, "second_name", message.text, "client")
    markup = types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Фамилия')
    markup.row('Тест')
    bot.send_message(message.chat.id, "Поздравляем - " + message.text, reply_markup=markup)


def join_to_club(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Фамилия')
    markup.row('Тест')
    if message.text == "esc":
        pass
    else:
        club_id = db.get_club_id_from_club_name(message.text)
        if club_id is None:
            bot.send_message(message.chat.id, "Такого клуба нет", reply_markup=markup)
        else:
            db.add_member_to_club(int(club_id), message.chat.id)
            bot.send_message(int(club_id), "К вам записался " + str(db.get_name_from_client_id(int(message.chat.id))))
            bot.send_message(message.chat.id, "Вы записаны!", reply_markup=markup)


def quit_from_club(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('Записаться', 'Уйти')
    markup.row('Фамилия')
    markup.row('Тест')
    club_id = db.get_club_id_from_club_name(message.text)
    if club_id is None:
        bot.send_message(message.chat.id, "Вы не ходили на такой клуб", reply_markup=markup)
    else:
        db.out_member_from_club(int(club_id), message.chat.id)
        bot.send_message(int(club_id), "От вас ушёл " + str(db.get_name_from_client_id(int(message.chat.id))))
        bot.send_message(message.chat.id, "Вы ушли от " + message.text, reply_markup=markup)


def add_club_description(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('Участники')
    markup.row('Описание')
    db.update_user_data(message.chat.id, "description", message.text, "club")
    bot.send_message(message.chat.id, "Описание клуба изменено", reply_markup=markup)
    # print(message.text)


def add_club(message):
    # сама регистрация клуба(добавление в бд)
    user_id = message.from_user.id
    is_register = 0
    while not is_register:
        is_register = db.add_new_club(user_id, message.text)
        if not is_register:
            add_club()
    markup = types.ReplyKeyboardMarkup()
    markup.row('Спорт')
    markup.row('Наука')
    markup.row('Искусство')
    msg = bot.send_message("К какому направлению относится Ваш клуб?", reply_markup=markup)
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
        db.set_club_tags(message, art_value=tags["art"], sport_value=tags["sport"], science_value=tags["science"])
        markup = types.ReplyKeyboardMarkup()
        markup.row('Участники')
        markup.row('Описание')
        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
        bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду /help", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, e)


if __name__ == '__main__':
    db.create_db()
    bot.polling(none_stop=True)
