import telebot
from dotenv import load_dotenv
import os

from handlers import fronts, checkin #,links


# Loading dotenv data
load_dotenv()

# Getting bot token and name
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")

# Instanciatin th bot
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start']) 
def start(msg: telebot.types.Message):
    bot.send_message(msg.chat.id, "Eu sou o bot do CodeLab")

#creates the command /fronts
fronts.show_fronts(bot)

checkin_BOT= checkin.Check_in(bot)

#handlers.links.show_links(bot)

bot.infinity_polling()