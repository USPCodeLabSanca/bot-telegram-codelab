import json
import random

import telebot
from telebot.types import Message

from handlers.abstract import msg_handler
from utils.isAdmin import admin_only

# Handler para o comando /codelab


class CodelabHandler(msg_handler):
    def __init__(self, bot, codelab_name_json):
        # Lendo os dados no json
        with open(codelab_name_json, "r", encoding="utf-8") as file:
            dados = json.load(file)

        # Criando a classe com a lista de nomes como dependência
        super().__init__(bot, name_list=dados["codelab_name_list"])

    # Escolhe aleatóriamente um nome errado do grupo para enviar na resposta
    async def __call__(self, msg: Message):
        if not self.name_list:
            answer = "O meu grupo se chama Codelab!"
        else:
            name = random.choice(self.name_list)
            answer = "O meu grupo se chama " + name + "!"

        topic = msg.message_thread_id

        # Chamando a injeção do método de envio da mensagem
        await self.BOT.send_message(msg.chat.id, answer, message_thread_id=topic)
