import telebot
from dotenv import load_dotenv
import os

from handlers import fronts, checkin, setCommands, codelab #,links
from handlers.codelab import CodelabHandler
from dependencies.internal import dados_checkin
# Carregando as chaves no .env
load_dotenv()

# Constantes para instanciar o bot
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")


# Lista de nomes CORRETÍSSIMOS do grupo Codelab
CODELAB_NAME_LIST = [
    'Codelab',
    'COdElAb',
    'C0DL4B',
    'COODELABES',
    'codecode',
    'Codaleb',
    'Codslabs',
    'CodeLabs',
    'CodLabs',
    'CodLab',
    'CodeLabe',
    'Code.lab',
    'Code\n\nlabe!',
    'Cadelob',
    '0x 43 6F 64 65 6C 61 62',
    '01100011 01101111 01100100 01100101 01101100 01100001 01100010',
    'G4n3sh?!?!?!?',
    'Code Laces'
]

# Função compositora para associar o bot aos handlers desenvolvidos
# Criando esses handlers por injeção de dependências
def create_bot(TOKEN):
    #instanciando o bot
    bot = telebot.TeleBot(TOKEN)

    #Instanciando as dependências dos bots
    checkin_DB= dados_checkin.Check_in_db()

    # Injetando as dependências nas features
    codelab = CodelabHandler(bot, CODELAB_NAME_LIST)
    checkin_main = checkin.checkin(bot, DATABASE=checkin_DB)
    checkin_add = checkin.add_checkin(bot, DATABASE=checkin_DB)
    checkin_clear= checkin.clear_checkin(bot, DATABASE=checkin_DB)
    checkin_format= checkin.format_checkin(bot, DATABASE=checkin_DB)
    checkin_preview = checkin.preview_checkin(bot, DATABASE=checkin_DB)

    # Composição das featrues no bot
    bot.register_message_handler(codelab, commands=['codelab'])
    bot.register_message_handler(checkin_main, commands=['checkin'])
    bot.register_message_handler(checkin_add, commands=['checkin_add'])
    bot.register_message_handler(checkin_clear, commands=['checkin_clear'])
    bot.register_message_handler(checkin_preview, commands=['checkin_preview'])
    bot.register_message_handler(checkin_format, commands=['checkin_format'])


    return bot

if __name__ == "__main__":
    bot = create_bot(TOKEN)
    bot.infinity_polling()
