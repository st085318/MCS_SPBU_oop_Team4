import argparse


class ArgParser(argparse.ArgumentParser):
    def __init__(self):
        argparse.ArgumentParser.__init__(self)
        self.description = 'Telegram bot'
        self.add_argument('token', help='authorisation token', type=str)
        self.add_argument('-s', help='Silent mode - disable shell output (file output only)', action='store_true')
