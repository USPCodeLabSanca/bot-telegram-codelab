import telebot
from telebot import types
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReactionTypeEmoji
from handlers.abstract import msg_handler
from utils.errors import catch_message_errors, PoorUseOfCommand, catch_callbackquery_errors
from random import choice

class FeedbackMain(msg_handler):
    def __init__(self, bot: telebot.TeleBot, feedback_add: 'FeedbackAdd' = None, feedback_guide: 'FeedbackHelper' = None):
        """Copiando o excelente trabalho feito pela Cecília no handler suggestions, a classe 
        FeedbackMain gerencia o fluxo de feedbacks dos usuários, incluindo sugestões, reclamações e elogios.
        Envia um menu para o usuário escolher o tipo de feedback que deseja fornecer e aconselha sobre como 
        contribuir de forma construtiva.
        """
        super().__init__(bot)
        # optional delegate to start the add flow
        self.feedback_add = feedback_add
        self.feedback_guide = feedback_guide

        # register a callback handler to delegate top-level feedback choices
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('feedback_yes'))
        async def _delegate_to_add(call: CallbackQuery):
            # if a FeedbackAdd instance was injected, call its __call__ with the message
            if hasattr(self, 'feedback_add') and self.feedback_add is not None:
                # call FeedbackAdd.__call__ with the original message
                await self.feedback_add.__call__(call.message)
            else:
                # fallback: acknowledge the callback so the client doesn't hang
                await self.BOT.answer_callback_query(call.id, text='Fluxo de feedback indisponível no momento.')

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('feedback_no'))
        @catch_callbackquery_errors(self.BOT)
        async def feedback_declined(call: CallbackQuery):
            await self.BOT.send_message(
                chat_id = call.message.chat.id, 
                text = "Tudo bem! Se mudar de ideia, estou aqui para ajudar.", 
                parse_mode='HTML', 
                message_thread_id=call.message.message_thread_id
            )

        @self.BOT.callback_query_handler(func=lambda call: call.data == 'feedback_guide')
        @catch_callbackquery_errors(self.BOT)
        async def show_guide(call: CallbackQuery):
            if hasattr(self, 'feedback_guide') and self.feedback_guide is not None:
                await self.feedback_guide.__call__(call.message)
            else:
                await self.BOT.answer_callback_query(call.id, text='Guia de feedback indisponível no momento.')

    @catch_message_errors()
    async def __call__(self, message: Message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Sim", callback_data="feedback_yes"))
        keyboard.add(types.InlineKeyboardButton("Não", callback_data="feedback_no"))
        keyboard.add(types.InlineKeyboardButton("📚 Dicas", callback_data="feedback_guide"))

        advice_text = (
            """Para contribuir de forma <b>construtiva</b> 🏗️, por favor siga estas diretrizes:

    🎯 <b>Seja claro e específico</b> sobre o que você está sugerindo ou reclamando.
    🤝 Mantenha um <b>tom respeitoso</b> e profissional.
    💡 <b>Forneça exemplos ou contextos</b> quando possível.
    🚫 <b>Evite linguagem ofensiva</b> ou ataques pessoais.

           
        <b>Gostaria de enviar um Feedback anônimo para os coordenadores do grupo?</b> 👇"""
        )

        await self.BOT.send_message(
            chat_id=message.chat.id,
            text=advice_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

class FeedbackAdd(msg_handler):
    def __init__(self, bot:telebot.TeleBot, target_chat_id: int):
        """A classe FeedbackAdd gerencia a adição de feedbacks dos usuários, incluindo sugestões, reclamações e elogios.
        Após o usuário selecionar o tipo de feedback, esta classe orienta o usuário a enviar sua mensagem de feedback.
        """
        super().__init__(bot)

        self.user_states = {} # Dicionário para rastrear o estado dos usuários
        self.target_chat_id = target_chat_id # ID do chat onde os feedbacks serão enviados

        self.callbackquery_handler()

        self.BOT.register_message_handler(
            self.new_feedback,
            func=lambda msg: msg.from_user.id in self.user_states.keys()
        )

    def cancel_btn(self, level: int):
        """Retorna um botão de cancelar para incluir nos keyboards"""
        return types.InlineKeyboardButton(text='❌ Cancelar', callback_data=f'feedback_cancel_add_{level}')

    @catch_message_errors()
    async def __call__(self, msg: Message):

        # Texto de Abertura (combina com a parte anterior)
        menu_abertura = "Escolha o tipo de feedback que deseja fornecer: 👇"

        # Menu para selecionar o tipo de feedback (Com formatação HTML)
        menu_feedback = (
            "• <b>Sugestão</b> ✨: Ideias para melhorar o bot ou adicionar novas funcionalidades.\n\n"
            
            "• <b>Reclamação</b> 🐞: Problemas ou falhas que você encontrou ao usar o bot.\n\n"
            
            "• <b>Elogio</b> 🥳: Comentários positivos sobre o bot ou suas funcionalidades."
        )

        menu = f"{menu_abertura}\n\n{menu_feedback}"

        btn1 = InlineKeyboardButton("Sugestão", callback_data="feedback_add_sugestão")
        btn2 = InlineKeyboardButton("Reclamação", callback_data="feedback_add_reclamação")
        btn3 = InlineKeyboardButton("Elogio", callback_data="feedback_add_elogio")
        keyboard = InlineKeyboardMarkup().add(btn1).add(btn2).add(btn3).add(self.cancel_btn(1))

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=menu,
            reply_markup=keyboard,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id
        )

    def callbackquery_handler(self):

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('feedback_cancel_add'))
        @catch_callbackquery_errors(self.BOT)
        async def cancel(call: CallbackQuery):

            level = int(call.data.split('_')[-1])

            #deleta a mensagem que possuia o botão de cancelar
            await self.BOT.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )

            #Avisa o cancelamento
            await self.BOT.answer_callback_query(call.id, text = "Adição de feedback cancelada.")

            if level in (2, 3,) and call.from_user.id in self.user_states.keys():
                del self.user_states[call.from_user.id]

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('feedback_add_'))
        @catch_callbackquery_errors(self.BOT)
        async def feedback_type_selected(call: CallbackQuery):
            
            type_of_feedback = call.data.split('_')[-1] #sugestão, elogio ou recalamação

            await self.BOT.answer_callback_query(call.id, text = f'Você selecionou: {type_of_feedback.capitalize()}')

            #Mensagem de instrução para o usuário
            instruction_text = (
                f"Por favor, envie sua/seu <b>{type_of_feedback}</b> ✍️ detalhada como uma mensagem separada.\n\n"
                "Certifique-se de ser <b>claro e específico</b> em seu feedback.\n\n"
                "Você pode cancelar a qualquer momento clicando no botão abaixo."
            )

            #Atualiza o estado do usuário
            #Store both the thread id and the instruction message id (so we can edit its markup later)
            sent = await self.BOT.send_message(
                chat_id=call.message.chat.id,
                text=instruction_text,
                reply_markup=InlineKeyboardMarkup().add(self.cancel_btn(2)),
                parse_mode='HTML'
            )

            self.user_states[call.from_user.id] = {
                'state': 'awaiting_feedback',
                'type': type_of_feedback,
                'message_thread_id': call.message.message_thread_id,
                'instruction_message_id': sent.message_id,
            }


        #botão de cancelar ou confirmar
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('feedback_confirm_add_'))
        @catch_callbackquery_errors(self.BOT)
        async def confirm_feedback(call: CallbackQuery):

            user_id = call.from_user.id

            if (user_id not in self.user_states or self.user_states[user_id]['state'] != 'awaiting_confirmation'):
                raise PoorUseOfCommand("Você não está no estado correto para confirmar um feedback.")
            
            state_info = self.user_states[user_id]

            type_of_feedback = state_info['type']
            feedback_message = state_info['feedback_message']
            Message_thread_id = state_info['message_thread_id']

            #Envia o feedback para o chat alvo
            feedback_text = (
                "🔔 <b>Novo feedback recebido!</b>\n\n"
                
                f"<b>Tipo:</b> {type_of_feedback.capitalize()}\n\n"
                
                f"<b>Mensagem:</b>\n{feedback_message}"
            )

            await self.BOT.send_message(
                chat_id=self.target_chat_id,
                text=feedback_text,
                parse_mode='HTML'
            )

            #Avisa o usuário
            await self.BOT.answer_callback_query(call.id, text = "Seu feedback foi enviado com sucesso. Obrigado!")

            #Limpa o estado do usuário
            del self.user_states[user_id]

    @catch_message_errors(PoorUseOfCommand)
    async def new_feedback(self, message: Message):
        user_id = message.from_user.id

        if (user_id not in self.user_states or self.user_states[user_id]['state'] != 'awaiting_feedback'):
            raise PoorUseOfCommand("Você não está no estado correto para enviar um feedback.")

        type_of_feedback = self.user_states[user_id]['type']

        # Armazena a mensagem de feedback
        self.user_states[user_id]['feedback_message'] = message.text
        self.user_states[user_id]['state'] = 'awaiting_confirmation'

        # Remove o botão de cancelar da mensagem de instrução (usamos o id salvo em 'instruction_message_id')
        try:
            await self.BOT.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=self.user_states[user_id].get('instruction_message_id') or self.user_states[user_id].get('message_thread_id'),
                reply_markup=None
            )
        except Exception:
            # Se a mensagem já foi deletada ou não encontrada, apenas prossiga — não queremos quebrar o fluxo do usuário
            pass

        # Dá uma reaçãozinha para o usuário
        emojis = ['😍', '🔥', '❤', '😁', '💯', '🎉', '🤩', '👍']
        await self.BOT.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji(choice(emojis))])

        # Mensagem de confirmação
        confirmation_text = (
            f"Você está prestes a enviar o seguinte {type_of_feedback}:\n\n"
            f"{message.text}\n\n"
            "Por favor, confirme se deseja enviar este feedback."
        )

        btn_confirm = InlineKeyboardButton("✅ Confirmar", callback_data="feedback_confirm_add_3")
        keyboard = InlineKeyboardMarkup().add(btn_confirm).add(self.cancel_btn(3))

        await self.BOT.send_message(
            chat_id=message.chat.id,
            text=confirmation_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

class FeedbackHelper(msg_handler):
    def __init__(self, bot: telebot.TeleBot):
        """A classe FeedbackHelper fornece dicas e melhores práticas para os usuários ao fornecer feedback.
        Ela pode ser chamada para lembrar os usuários sobre como contribuir de forma construtiva.
        """
        super().__init__(bot)

    @catch_message_errors()
    async def __call__(self, message: Message):
        advice_text = (
            "📝 <b>Dicas para fornecer feedback construtivo:</b>\n\n"
            
            "🎯 Seja <b>claro e específico</b> sobre o que você está sugerindo ou reclamando.\n"
            
            "🤝 Mantenha um <b>tom respeitoso</b> e profissional.\n"
            
            "💡 Forneça <b>exemplos ou contextos</b> quando possível.\n"
            
            "🚫 Evite linguagem ofensiva ou ataques pessoais.\n\n"
            
            "⭐ <i>Obrigado por ajudar a melhorar nosso bot!</i>"
        )

        await self.BOT.send_message(
            chat_id=message.chat.id,
            text=advice_text,
            parse_mode='HTML'
        )