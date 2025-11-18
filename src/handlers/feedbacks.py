import telebot
from telebot import types
from telebot.types import Message
from handlers.abstract import msg_handler

class Feedback(msg_handler):
    def __init__(self, bot, target):
        super().__init__(bot)
        self.target = target
        self.register_callback_handler()
        pass

    async def __call__(self, msg: telebot.types.Message):
        feedback = "Gostaria de enviar um feedback anônimo para os coordenadores do grupo?"

        markup = types.InlineKeyboardMarkup()

        yes_button = types.InlineKeyboardButton('Sim', callback_data='feedback_yes')
        no_button = types.InlineKeyboardButton('Não', callback_data='feedback_no')

        markup.add(yes_button, no_button)

        await self.BOT.send_message(msg.chat.id, feedback, reply_markup=markup, message_thread_id=msg.message_thread_id)


    def register_callback_handler(self):
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('feedback_'))
        async def handle_feedback_query(call:types.CallbackQuery):
            
            topic = call.message.message_thread_id
            chat_id = call.message.chat.id

            if call.data == 'feedback_yes':
                await self.BOT.send_message(
                    chat_id, 'Ótimo\\! Pode enviar sua mensagem\\!\nTodos os Feedbacks serão enviados anonimamente\\!', 
                    parse_mode="MarkdownV2", 
                    message_thread_id=topic
                )

                @self.BOT.message_handler(func=lambda msg: msg.chat.id == chat_id)
                async def feedback_collector(msg: types.Message):
                # Chama sua função de recebimento
                    await self.receiveFeedback(msg, topic)

                # # Remove o handler depois de capturar 1 mensagem
                #     self.BOT.remove_message_handler(feedback_collector)


            elif call.data == 'feedback_no':
                await self.BOT.send_message(
                    chat_id,
                    'Sem problemas\\!\nEnvio de Feedback cancelado',
                    parse_mode="MarkdownV2",
                    message_thread_id=topic
                )

    async def receiveFeedback(self, message: Message, topic: int = None):
            user_text = message.text

            try:

                await self.BOT.send_message(
                    self.target,
                    f'Novo feedback anônimo:\n\n\n{user_text}\n',
                    message_thread_id=topic
                )

                await self.BOT.send_message(
                    message.chat.id,
                    'Obrigado!\nSeu Feedback foi enviado com sucesso',
                    message_thread_id=topic
                )


            except Exception as e:
                await self.BOT.send_message(
                    message.chat.id,
                    f'Ocorreu um erro ao enviar seu feedback\\: {e}',
                    message_thread_id=topic
                )


        