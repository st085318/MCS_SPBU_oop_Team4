import requests
from src.parser import ArgParser
from sys import argv


class TelegramBot:
    def __init__(self, token):
        self.url = 'https://api.telegram.org/bot' + token + '/'

    def send_message(self, chat, text):
        method = 'sendMessage'
        params = {'chat_id': chat, 'text': text}
        response = requests.post(self.url + method, params)
        return response

    def get_me(self):
        method = 'getMe'
        response = requests.post(self.url + method)
        return response

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.url + method, params)
        result_json = response.json()['result']
        return result_json

    def get_last_update(self):
        get_result = self.get_updates()
        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]
        return last_update


def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id


def main():
    args = ArgParser().parse_args(argv[1:])
    bot = TelegramBot(args.token)
    update = bot.get_last_update()
    print(bot.get_me().json())
    chat_id = get_chat_id(update)
    bot.send_message(chat_id, 'Hi there!')


if __name__ == '__main__':
    main()
