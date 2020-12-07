import os
import sys
import telebot
import ast
from telebot import types
from string import Template
from database import add_new_club, add_new_client, add_member_to_club, update_user_data, \
    get_id_members_of_club, get_id_clubs_of_client, is_user_client_or_club, out_member_from_club, create_db, \
    get_clubs_to_join, get_club_id_from_club_name, get_name_from_client_id, get_name_from_club_id

# Telegram your token
bot = telebot.TeleBot("")


@bot.message_handler(commands=['start'])
def start_handler(message):
        msg = bot.send_message(message.chat.id, "Hello everyone. Please, stay home!")
        if is_user_client_or_club(message.chat.id) is None:
            markup = types.ReplyKeyboardMarkup()
            markup.row('Я ищу кружок')
            markup.row('Я есть кружок')
            bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
            bot.register_next_step_handler(msg, get_name_to_register)


@bot.message_handler(commands=['help'])
def help_information(message):
        bot.send_message(message.chat.id, "It's help!")
        if is_user_client_or_club(message.chat.id) == 1:
            msg = bot.send_message(message.chat.id, 'Отправьте: \n"Описание", чтобы изменить описание своего клуба\n'
                                                    '"Участники", чтобы узнать список участников клуба')
        else:
            msg = bot.send_message(message.chat.id, 'Отправьте: \n'
                                                    '"Фамилия", чтобы поменять свою фамилию\n'
                                                    '"Записаться", записаться на клуб\n'
                                                    '"Уйти", чтобы уйти из клуба')


@bot.message_handler(content_types=['text'])
def read_messages(message):
    if is_user_client_or_club(message.chat.id) == 1:
        if message.text == "Описание":
            msg = bot.send_message(message.chat.id, "Введите новое описание")
            bot.register_next_step_handler(msg, add_club_description)
        #elif message.text == "Название":
        #    msg = bot.send_message(message.chat.id, "Введите новое название")
        #    bot.register_next_step_handler(msg, add_club_name)
        elif message.text == "Участники":
            members = get_id_members_of_club(message.chat.id)
            if members is None:
                bot.send_message(message.chat.id, "У вас нет членов")
            else:
                list_of_members = members.split(";")
                members = ""
                for member in list_of_members:
                    members += get_name_from_client_id(int(member)) + "\n"
                bot.send_message(message.chat.id, str(members))
        else:
            bot.send_message(message.chat.id, "WHAT?!?!?")
    elif is_user_client_or_club(message.chat.id) == 2:
        if message.text == "Фамилия":
            msg = bot.send_message(message.chat.id, "Введите новую фамилию")
            bot.register_next_step_handler(msg, add_client_surname)
        elif message.text == "Записаться":
            clubs = get_clubs_to_join()
            ans = ""
            for key, value in clubs.items():
                if value is None:
                    value = "Описание не предоставлено"
                ans = str(key)+":\n"+str(value)+"\n\n"

            bot.send_message(message.chat.id, "Список клубов и их описание"
                                              "введите название клуба, "
                                              "если хотетите записаться, или esc, чтобы выйти из режима записи")
            msg = bot.send_message(message.chat.id, ans)

            bot.register_next_step_handler(msg, join_to_club)
        elif message.text == "Уйти":
            msg = bot.send_message(message.chat.id, "Введите название клуба, который вы хотите покинуть")
            bot.register_next_step_handler(msg, quit_from_club)
        else:
            bot.send_message(message.chat.id, "WHAT?!?!?")


@bot.message_handler(content_types=['photo'])
def react_photo(message):
    bot.send_message(message.chat.id, "So beautifully!")


def get_name_to_register(message):
    try:
        if message.text == 'Я ищу кружок':
            client_name = bot.send_message(message.chat.id, "Как к вам обращаться?")
            bot.register_next_step_handler(client_name, add_client)
        else:
            msg = bot.send_message(message.chat.id, "Как называется ваш кружок?")
            bot.register_next_step_handler(msg, add_club)
            print(message.chat.id)
        del_markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Не волнуйтесь - ваши данные в руках делитантов!", reply_markup=del_markup)
    except Exception as e:
        bot.reply_to(message, e)


def add_client(message):
    user_id = message.from_user.id
    add_new_client(user_id, message.text)
    bot.send_message(message.chat.id, "Поздравляем, " + message.text + ".")
    bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
    bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду /help")


def add_client_surname(message):
    update_user_data(message.chat.id, "second_name", message.text, "client")
    bot.send_message(message.chat.id, "Поздравляем - " + message.text)


def join_to_club(message):
    if message.text == "esc":
        pass
    else:
        club_id = get_club_id_from_club_name(message.text)
        if club_id is None:
            bot.send_message(message.chat.id, "Такого клуба нет")
        else:
            add_member_to_club(int(club_id), message.chat.id)
            bot.send_message(int(club_id), "К вам записался " + str(get_name_from_client_id(int(message.chat.id))))
            bot.send_message(message.chat.id, "Вы записаны!")


def quit_from_club(message):
    club_id = get_club_id_from_club_name(message.text)
    if club_id is None:
        bot.send_message(message.chat.id, "Вы не ходили на такой клуб")
    else:
        out_member_from_club(int(club_id), message.chat.id)
        bot.send_message(int(club_id), "От вас ушёл " + str(get_name_from_client_id(int(message.chat.id))))
        bot.send_message(message.chat.id, "Вы ушли от " + message.text)


def add_club_description(message):
    update_user_data(message.chat.id, "description", message.text, "club")
    print(message.text)


def add_club(message):
    user_id = message.from_user.id
    is_register = 0
    while not is_register:
        is_register = add_new_club(user_id, message.text)
        if not is_register:
            add_club()


if __name__ == '__main__':
    create_db()
    bot.polling(none_stop=True)
