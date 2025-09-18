import telebot
from telebot import types

# comando de teste que mostra as frentes do grupo
def show_fronts(bot):

    @bot.message_handler(commands=['fronts']) 
    def start(msg: telebot.types.Message):
        fronts = 'No CodeLabSanca🧪, temos cinco frentes principais:\n📚 Dev. Learn\n💻 Dev. Boost\n🎉 Dev. Hack.\n🥚 Dev. Clara\n🙅‍♂️ Dev. Hire \n\n\n\n👉 Sobre qual você quer saber?'

        markup = types.InlineKeyboardMarkup()

        learn_button = types.InlineKeyboardButton('📚 Dev. Learn', callback_data='learn_button')
        boost_button = types.InlineKeyboardButton('💻 Dev. Boost', callback_data='boost_button')
        hack_button = types.InlineKeyboardButton('🎉 Dev. Hack', callback_data='hack_button')
        clara_button = types.InlineKeyboardButton('🥚 Dev. Clara', callback_data='clara_button')
        hire_button = types.InlineKeyboardButton('🙅‍♂️ Dev. Hire', callback_data='hire_button')

        markup.add(learn_button, boost_button, hack_button, clara_button, hire_button)

        bot.send_message(msg.chat.id, fronts, reply_markup=markup)


    @bot.callback_query_handler()
    def resposta_botao(call:types.CallbackQuery):
        match call.data:
            case 'learn_button':
                bot.send_message(call.message.chat.id, '📚 O *Dev\\. Learn* é a frente mais educativa do grupo\\.\nSão os integrantes responsáveis por ministrar *diferentes cursos em diversas tecnologias*, para estudantes tanto de *dentro* quanto de *fora* da *USP* 🏫\\.', parse_mode="MarkdownV2")
            case 'boost_button':
                bot.send_message(call.message.chat.id, '💻 O *Dev\\. Boost* é a frente mais técnica do grupo\\.\nO foco principal da frente é desenvolver *projetos práticos* através da elaboração de sub\\-grupos onde diversas tecnologias são *praticadas* e *implementadas* 🧪\\.', parse_mode="MarkdownV2")
            case 'hack_button':
                bot.send_message(call.message.chat.id, '🎉 O *Dev\\. Hack* é a frente mais criativa do grupo\\.\nÉ o grupo responsável por _idealizar_, _organizar_ e _implementar_ *hackatons*\\.\nSão os membros na função de pensar em ideias criativas e dinâmicas para tornar esses eventos *divertidos* e *bem organizados* 🍕\\.', parse_mode="MarkdownV2")
            case 'clara_button':
                bot.send_message(call.message.chat.id, '🥚 O *Dev\\. Clara* é a frente focada em resolver *questões técnicas* dadas em _entrevistas de emprego_ treinando e incentivando os membros a desenvolver a solução e explicar o que está sendo feito\n 🧑‍💼Tudo isso com a ajuda de outros membros\\.', parse_mode="MarkdownV2")
            case 'hire_button':
                bot.send_message(call.message.chat.id, '🙅‍♂️ O *Dev\\. Hire* é a frente na qual postamos *dicas* sobre _empregos e oportunidades_\\.\n Todos os membros estão automaticamente nessa frente 😁\\!', parse_mode = "MarkdownV2")
