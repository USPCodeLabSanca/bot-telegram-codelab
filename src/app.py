import telebot
from dotenv import load_dotenv
import os

from handlers import fronts, checkin, setCommands, codelab #,links
from handlers.codelab import CodelabHandler
# Carregando as chaves no .env
load_dotenv()

# Constantes para instanciar o bot
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")


# Lista de nomes CORRETÍSSIMOS do grupo Codelab
CODELAB_NAME_LIST = [
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

# Função compositora para associar o bot aos handlers desenvolvidos
# Criando esses handlers por injeção de dependências
def create_bot(TOKEN):
    #instanciando o bot
    bot = telebot.TeleBot(TOKEN)

    # Injetando as dependências nas features
    codelab = CodelabHandler(bot, CODELAB_NAME_LIST)

    # Composição das featrues no bot
    bot.register_message_handler(codelab, commands=['codelab'])

    return bot

if __name__ == "__main__":
    bot = create_bot(TOKEN)
    bot.infinity_polling()
