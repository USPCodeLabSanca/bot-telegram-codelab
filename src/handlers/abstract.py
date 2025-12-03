from abc import abstractmethod, ABC
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot

class msg_handler(ABC):
    def __init__(self, BOT: AsyncTeleBot):
        self.BOT = BOT

    @abstractmethod
    async def __call__(self, msg:Message):
        pass









    