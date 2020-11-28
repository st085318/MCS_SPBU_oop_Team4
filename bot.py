import os
import sys
import telebot
from telebot import types
from string import Template
from database import add_new_club, add_new_client, add_member_to_club, update_user_data, \
    get_id_members_of_club, get_id_clubs_of_client, is_user_client_or_club, out_member_from_club

# Telegram your token
bot = telebot.TeleBot("1439682687:AAHlGwcG-CUXtZ4vimJ6-u8ynFe0humkuVc")


@bot.message_handler(commands=['start'])
def start_handler(message):
        msg = bot.send_message(message.chat.id, "Hello everyone. Please, stay home!")
        if is_user_client_or_club(message.chat.id) is None:
            markup = types.ReplyKeyboardMarkup()
            markup.row('Я ищу кружок')
            markup.row('Я есть кружок')
            bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)
            bot.register_next_step_handler(msg, process_registration)


@bot.message_handler(commands=['help'])
def help_information(message):
        bot.send_message(message.chat.id, "It's help!")
        if is_user_client_or_club(message.chat.id) == 1:
            msg = bot.send_message(message.chat.id, 'Отправьте: \n"Описание", чтобы изменить описание своего клуба\n'
                                                    '"Название", чтобы поменять название своего клуба\n'
                                                    '"Участники", чтобы узнать список участников клуба')
        else:
            msg = bot.send_message(message.chat.id, 'Отправьте: \n'
                                                    '"Имя", чтобы изменить своё имя\n'
                                                    '"Фамилия", чтобы поменять свою фамилию\n'
                                                    '"Записаться", записаться на клуб\n'
                                                    '"Уйти", чтобы уйти из клуба')


@bot.message_handler(content_types=['text'])
def read_messages(message):
    if is_user_client_or_club(message.chat.id) == 1:
        if message.text == "Описание":
            msg = bot.send_message(message.chat.id, "Введите новое описание")
            bot.register_next_step_handler(msg, add_club_name)
        elif message.text == "Название":
            msg = bot.send_message(message.chat.id, "Введите новое название")
            bot.register_next_step_handler(msg, add_club_name)
        elif message.text == "Участники":
            members = get_id_members_of_club(message.chat.id)
            bot.send_message(message.chat.id, str(members))
        else:
            bot.send_message(message.chat.id, "WHAT?!?!?")
    elif is_user_client_or_club(message.chat.id) == 2:
        if message.text == "Имя":
            msg = bot.send_message(message.chat.id, "Введите новое имя")
            bot.register_next_step_handler(msg, add_client_name)
        elif message.text == "Фамилия":
            msg = bot.send_message(message.chat.id, "Введите новую фамилию")
            bot.register_next_step_handler(msg, add_client_name)
        elif message.text == "Записаться":
            msg = bot.send_message(message.chat.id, "Введите id клуба")
            bot.register_next_step_handler(msg, join_to_club)
        elif message.text == "Уйти":
            msg = bot.send_message(message.chat.id, "Введите id клуба")
            bot.register_next_step_handler(msg, quit_from_club)
        else:
            bot.send_message(message.chat.id, "WHAT?!?!?")


@bot.message_handler(content_types=['photo'])
def react_photo(message):
    bot.send_message(message.chat.id, "So beautifully!")


def process_registration(message):
    try:
        user_id = message.from_user.id
        if message.text == 'Я ищу кружок':
            add_new_client(user_id)
            print("hi, client")
        else:
            add_new_club(user_id)
            print("hi, club")
            print(message.chat.id)
        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
        del_markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Если хотите узнать функционал, введите команду help",
                         reply_markup=del_markup)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def add_client_name(message):
    update_user_data(message.chat.id, "first_name", message.text, "client")
    bot.send_message(message.chat.id, "Поздравляем - " + message.text)


def add_client_surname(message):
    update_user_data(message.chat.id, "second_name", message, "client")
    bot.send_message(message.chat.id, "Поздравляем - " + message)


def join_to_club(message):
    add_member_to_club(int(message.text), message.chat.id)
    bot.send_message(int(message.text), "К вам записался " + str(message.chat.id))


def quit_from_club(message):
    out_member_from_club(int(message.text), message.chat.id)
    bot.send_message(int(message.text), "От вас ушёл " + str(message.chat.id))


def add_club_description(message):
    update_user_data(message.chat.id, "description", message.text, "club")
    print(message.text)


def add_club_name(message):
    update_user_data(message.chat.id, "club_name", message.text, "club")
    bot.send_message(message.chat.id, "Поздравляем - " + message.text)


bot.polling(none_stop=True)
