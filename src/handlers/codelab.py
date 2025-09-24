import telebot
import random

# Handler para o comando /
class CodelabHandler():
    def __init__(self, bot, codelab_name_list):
        self._bot = bot
        self._name_list = codelab_name_list

    # Escolhe aleatóriamente um nome errado do grupo para enviar na resposta
    def __call__(self, message):
        if not self._name_list:
            msg = "O meu grupo se chama Codelab!"
        else:
            name = random.choice(self._name_list)
            msg = "O meu grupo se chama " + name + "!"

        # Chamando a injeção do método de envio da mensagem
        self._bot.send_message(message.chat.id, msg)

