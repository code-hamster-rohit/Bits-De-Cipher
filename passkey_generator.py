import random

class Passkey:
    def __init__(self, length):
        self.__length = length
        self.passkey = self.__generate_passkey()
    def __generate_passkey(self):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=self.__length))
