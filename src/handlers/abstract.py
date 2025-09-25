from abc import abstractmethod, ABC
from telebot.types import Message
from telebot import TeleBot

class msg_handler(ABC):
    def __init__(self, nossoBOT:TeleBot, **dependencies):
        self.BOT= nossoBOT

        for key, value in dependencies.items():
            setattr(self, key, value)

    @abstractmethod
    def __call__(self, msg:Message):
        pass

    @abstractmethod
    def callbacks(self):
        pass









    