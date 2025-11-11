from abc import abstractmethod, ABC
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot

class msg_handler(ABC):
    def __init__(self, BOT: AsyncTeleBot, **dependencies):
        self.BOT = BOT

        for key, value in dependencies.items():
            setattr(self, key, value)

    @abstractmethod
    async def __call__(self, msg:Message):
        pass









    