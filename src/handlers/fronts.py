import telebot

# comando de teste que mostra as frentes do grupo
def show_fronts(bot):
    @bot.message_handler(commands=['fronts']) 
    def start(msg: telebot.types.Message):
        fronts = 'In Sanca CodeLab we have dev.boost, dev.learn, dev.hack'

        bot.send_message(msg.chat.id, fronts)