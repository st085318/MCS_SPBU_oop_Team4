import os
import sys
import telebot
from string import Template
from database import add_new_club, add_new_client, add_member_to_club, update_user_data, \
    get_id_members_of_club, get_id_clubs_of_client

# Telegram your token
bot = telebot.TeleBot("1439682687:AAHlGwcG-CUXtZ4vimJ6-u8ynFe0humkuVc")


@bot.message_handler(commands=['start'])
def start_handler(message):
        msg = bot.send_message(message.chat.id, "Hello everyone. Please, stay home!")
        bot.register_next_step_handler(msg, process_registration)


@bot.message_handler(commands=['help'])
def help_information(message):
        msg = bot.send_message(message.chat.id, "It's help!")
        #bot.register_next_step_handler(msg, process_firstname_step)


def process_registration(message):
    try:
        user_id = message.from_user.id
        if message.text == 1:
            add_new_client(user_id)
            print("hi, client")
        else:
            add_new_club(user_id)
            print("hi, club")
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_description_step(message):
    try:
        user_id = message.from_user.id
        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")


    except Exception as e:
        bot.reply_to(message, 'oooops')


bot.polling(none_stop=True)
