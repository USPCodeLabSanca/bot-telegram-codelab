from handlers.abstract import msg_handler
from utils.errors import catch_message_errors
from telebot.types import ReactionTypeEmoji, Message
from random import choice

class Start(msg_handler):
    def __init__(self, BOT):
        super().__init__(BOT)

    @catch_message_errors()
    async def __call__(self, msg: Message):

        start_message = f"Olá, Codelaber! "
        start_message += f"Eu sou o BOT_A_SER_NOMEADO, o assistente virtual do Codelab no Telegram. "
        start_message += f"Digite /help para ver uma lista breve das minhas funcionalidades e comandos!"

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=start_message,
            message_thread_id=msg.message_thread_id
        )

    