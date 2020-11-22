class HandleCondition:
    method = None
    # Array of strings
    commands = None

    def __init__(self, method, commands=None):
        self.method = method
        self.commands = commands

    def check(self, update) -> bool:
        if 'message' in update:
            if self.commands is not None and 'text' in update['message']:
                for command in self.commands:
                    if command in update['message']['text']:
                        return True
        return False

    def check_and_run(self, update):
        if self.check(update):
            self.method(update)
            return True
        return False
