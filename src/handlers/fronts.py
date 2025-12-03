import telebot
from telebot import types
from telebot.types import Message
from handlers.abstract import msg_handler

class ShowFronts(msg_handler):
    def __init__(self, bot):
        super().__init__(bot)
        self.callback()

    async def __call__(self, msg: telebot.types.Message):
        fronts = 'No CodeLabSanca🧪, temos cinco frentes principais:\n📚 Dev. Learn\n💻 Dev. Boost\n🎉 Dev. Hack.\n🥚 Dev. Clara\n🙅‍♂️ Dev. Hire \n\n\n\n👉 Sobre qual você quer saber?'

        markup = types.InlineKeyboardMarkup()

        learn_button = types.InlineKeyboardButton('📚 Dev. Learn', callback_data='devlearn_button')
        boost_button = types.InlineKeyboardButton('💻 Dev. Boost', callback_data='devboost_button')
        hack_button = types.InlineKeyboardButton('🎉 Dev. Hack', callback_data='devhack_button')
        clara_button = types.InlineKeyboardButton('🥚 Dev. Clara', callback_data='devclara_button')
        hire_button = types.InlineKeyboardButton('🙅‍♂️ Dev. Hire', callback_data='devhire_button')

        markup.add(learn_button, boost_button, hack_button, clara_button, hire_button)

        await self.BOT.send_message(msg.chat.id, fronts, reply_markup=markup, message_thread_id=msg.message_thread_id)

    def callback(self):
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('dev'))
        async def resposta_botao(call:types.CallbackQuery):

            topic = call.message.message_thread_id

            match call.data:
                case 'devlearn_button':
                    await self.BOT.send_message(call.message.chat.id, '📚 O *Dev\\. Learn* é a frente mais educativa do grupo\\.\nSão os integrantes responsáveis por ministrar *diferentes cursos em diversas tecnologias*, para estudantes tanto de *dentro* quanto de *fora* da *USP* 🏫\\.', parse_mode="MarkdownV2", message_thread_id=topic)
                case 'devboost_button':
                    await self.BOT.send_message(call.message.chat.id, '💻 O *Dev\\. Boost* é a frente mais técnica do grupo\\.\nO foco principal da frente é desenvolver *projetos práticos* através da elaboração de sub\\-grupos onde diversas tecnologias são *praticadas* e *implementadas* 🧪\\.', parse_mode="MarkdownV2",  message_thread_id=topic)
                case 'devhack_button':
                    await self.BOT.send_message(call.message.chat.id, '🎉 O *Dev\\. Hack* é a frente mais criativa do grupo\\.\nÉ o grupo responsável por _idealizar_, _organizar_ e _implementar_ *hackatons*\\.\nSão os membros na função de pensar em ideias criativas e dinâmicas para tornar esses eventos *divertidos* e *bem organizados* 🍕\\.', parse_mode="MarkdownV2",  message_thread_id=topic)
                case 'devclara_button':
                    await self.BOT.send_message(call.message.chat.id, '🥚 O *Dev\\. Clara* é a frente focada em resolver *questões técnicas* dadas em _entrevistas de emprego_ treinando e incentivando os membros a desenvolver a solução e explicar o que está sendo feito\n 🧑‍💼Tudo isso com a ajuda de outros membros\\.', parse_mode="MarkdownV2",  message_thread_id=topic)
                case 'devhire_button':
                    await self.BOT.send_message(call.message.chat.id, '🙅‍♂️ O *Dev\\. Hire* é a frente na qual postamos *dicas* sobre _empregos e oportunidades_\\.\n Todos os membros estão automaticamente nessa frente 😁\\!', parse_mode = "MarkdownV2",  message_thread_id=topic)

        

