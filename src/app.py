import telebot
from dotenv import load_dotenv
import os

from handlers import fronts, checkin, setCommands, codelab #,links

# Carregando as chaves no .env
load_dotenv()

# Constantes para instanciar o bot
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")

# Instanciando o bot
bot = telebot.TeleBot(TOKEN)

# Instanciando o menu de comandos
bot.set_my_commands(setCommands.COMANDOS)

# Teste temporátrio??
@bot.message_handler(commands=['start']) 
def start(msg: telebot.types.Message):
    bot.send_message(msg.chat.id, "Eu sou o bot do CodeLab")

# Instanciando os comandos em /handler
fronts.show_fronts(bot)
codelab.say_codelab(bot)
checkin_BOT= checkin.Check_in(bot)
#links.show_links(bot)

# Rodando o bot
bot.infinity_polling()