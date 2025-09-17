import telebot
from dotenv import load_dotenv
import os

import handlers.fronts

# Loading dotenv data
load_dotenv()

# Getting bot token and name
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")

# Instanciatin th bot
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start']) 
def start(msg: telebot.types.Message):
    bot.send_message(msg.chat.id, )

handlers.fronts.show_fronts(bot)

bot.infinity_polling()