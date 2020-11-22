import requests
from src.parser import ArgParser
from sys import argv
from src.handle import HandleCondition


class TelegramBot:
    _token = None
    url = None
    _modes = {'general': [], 'client': [], 'host': []}
    _active_handlers = []
    _mode = None

    def __init__(self, token):
        self._token = token
        self.url = 'https://api.telegram.org/bot' + token + '/'
        self._init_handlers()

    def _init_handlers(self):
        self._modes['general'] = [HandleCondition(self.start, commands=['/start', '/help'])]
        self._modes['client'] = []
        self._modes['host'] = []

        _mode = 'general'
        self._active_handlers = self._modes['general']
        self._set_my_commands()

    def change_mode(self, mode):
        self._mode = mode
        self._active_handlers = self._modes['general']
        if self._mode != 'general':
            self._active_handlers += self._modes[self._mode]
        self._set_my_commands()

    def _send_message(self, chat, text):
        method = 'sendMessage'
        data = {'chat_id': chat, 'text': text}
        response = requests.post(self.url + method, data)
        return response

    def _set_my_commands(self):
        command_list = []
        for handler in self._active_handlers:
            for command in handler.commands:
                if command not in [cmd['command'] for cmd in command_list]:
                    command_list.append({'command': command, 'description': command[1:]})
        method = 'setMyCommands'
        params = {'commands':command_list}
        response = requests.post(self.url + method, json=params)
        print(response)
        return response

    def _get_me(self):
        method = 'getMe'
        response = requests.post(self.url + method)
        return response

    def _get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        data = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.url + method, data)
        result_json = response.json()['result']
        return result_json

    def _get_last_update(self):
        get_result = self._get_updates()
        try:
            last_update = get_result[-1]
        except IndexError:
            raise IndexError
        return last_update

    @staticmethod
    def _get_chat_id(update):
        chat_id = update['message']['chat']['id']
        return chat_id

    def polling(self, non_stop=False, it_num=100):
        new_offset = None
        while non_stop or (it_num > 0):
            self._get_updates(new_offset)

            try:
                update = self._get_last_update()
            except IndexError:
                continue

            last_update_id = update['update_id']

            print(update)
            chat_id = self._get_chat_id(update)
            for handler in self._active_handlers:
                if handler.check_and_run(update):
                    break
            else:
                self._send_message(chat_id, 'Unknown command...')

            new_offset = last_update_id + 1
            if not non_stop:
                it_num -= 1

    def start(self, update):
        chat_id = self._get_chat_id(update)
        text = ("Hello! This is a test bot for our project!\n"
                "Our work is still in progress, though...\n"
                "You can type /start or /help to see this message again"
                )
        self._send_message(chat_id, text)


def main():
    args = ArgParser().parse_args(argv[1:])
    bot = TelegramBot(args.token)
    bot.polling(non_stop=True)


if __name__ == '__main__':
    main()
