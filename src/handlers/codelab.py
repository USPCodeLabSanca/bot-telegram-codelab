import telebot
from telebot import types
import random

# Lista de nomes CORRETÍSSIMOS do grupo Codelab
INNER_NAME_LIST = [
    'Codelab',
    'COdElAb',
    'COODELABES',
    'codecode',
    'Codaleb',
    'Codslabs',
    'CodeLabs',
    'CodLabs',
    'CodeLabe',
    'Code.lab',
    'Code\n\nlabe!',
    'Cadelob',
    '0x 43 6F 64 65 6C 61 62',
    '01100011 01101111 01100100 01100101 01101100 01100001 01100010',
    'G4n3sh?!?!?!?',
]

def say_codelab(bot):

    # Retorna um nome aleatório do codelab como resposta
    @bot.message_handler(commands=['codelab'])
    def codelab(msg: telebot.types.Message):
        randomName = random.choice(INNER_NAME_LIST)
        bot.send_message(msg.chat.id, f'Meu grupo chama {randomName}!')
