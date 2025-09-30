import telebot
import random
from telebot.types import Message

from handlers.abstract import msg_handler

# Handler para o comando /codelab
class CodelabHandler(msg_handler):
    def __init__(self, bot, codelab_name_list):
        super().__init__(bot, name_list=codelab_name_list)


    # Escolhe aleatóriamente um nome errado do grupo para enviar na resposta
    def __call__(self, msg: Message):
        if not self.name_list:
            answer = "O meu grupo se chama Codelab!"
        else:
            name = random.choice(self.name_list)
            answer = "O meu grupo se chama " + name + "!"

        # Chamando a injeção do método de envio da mensagem
        self.BOT.send_message(msg.chat.id, answer)

