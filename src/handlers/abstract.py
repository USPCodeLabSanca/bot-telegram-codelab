from abc import abstractmethod, ABC
from telebot.types import Message
from telebot import TeleBot

class msg_handler(ABC):
    def __init__(self, nossoBOT:TeleBot):
        self.BOT= nossoBOT

    @abstractmethod
    async def __call__(self, msg:Message):
        pass









    