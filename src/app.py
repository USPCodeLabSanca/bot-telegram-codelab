import telebot
from dotenv import load_dotenv
import os

from handlers import fronts, checkin, setCommands, codelab #,links

# Loading dotenv data
load_dotenv()

# Getting bot token and name
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")

# Instanciatin th bot
bot = telebot.TeleBot(TOKEN)

# Puts the commands in the command menu
bot.set_my_commands(setCommands.COMANDOS)

@bot.message_handler(commands=['start']) 
def start(msg: telebot.types.Message):
    bot.send_message(msg.chat.id, "Eu sou o bot do CodeLab")

#creates the command /fronts
fronts.show_fronts(bot)

#creates the command /codelab
codelab.say_codelab(bot)

#creates the command /checkin_* 
checkin_BOT= checkin.Check_in(bot)

#links.show_links(bot)

bot.infinity_polling()