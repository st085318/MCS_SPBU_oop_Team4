import requests
import argparse
from sys import argv


def create_parser():
    """
    Creates argument parser
    :return: parser - parser
    """
    parser = argparse.ArgumentParser(description='Telegram bot')
    parser.add_argument('token', help='authorisation token', type=str)
    parser.add_argument('-s', help='Silent mode - disable shell output (file output only)', action='store_true')
    return parser


def argument_parse(cmd_list):
    """
    Parses command prompt arguments
    :param cmd_list: list of arguments
    :return: list of parsed arguments
    """
    parser = create_parser()
    args_ = parser.parse_args(cmd_list)
    return args_


def get_updates_json(request):
    response = requests.get(request + 'getUpdates')
    return response.json()


def last_update(data):
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]


def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id


def send_message(url, chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response


def main():
    args = argument_parse(argv[1:])
    url = 'https://api.telegram.org/bot' + args.token + '/'
    chat_id = get_chat_id(last_update(get_updates_json(url)))
    send_message(url, chat_id, 'Hi there!')


if __name__ == '__main__':
    main()
