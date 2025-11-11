from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji, Message, CallbackQuery

from handlers.abstract import msg_handler
from handlers.errors import catch_callbackquery_errors, catch_message_errors

from dependencies.internal.suggestions_db import SuggestionsDB
from dependencies.internal.bot_errors import DBError, PoorUseOfCommand

from random import choice

class SuggestionMain(msg_handler):
    def __init__(self, BOT):
        super().__init__(BOT)

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        menu = '<b>O que você deseja realizar?</b>\n\n'

        menu += '➕ Contribuir anonimamente com uma sugestão de melhoria para o BOT_A_SER_NOMEADO:\n/suggestion_add\n\n'
        menu += '📂 Ver sugestões pendentes para o BOT_A_SER_NOMEADO:\n/suggestion_list\n\n'

        menu += 'Para cooperar com uma sugestão clara e bem elaborada, é recomendado'
        menu += ' o uso do comando /sugestion_guide para ler instruções, dicas e exemplos de'
        menu += ' como construir uma issue de maneira adequada'
                                   
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id)

class SuggestionAdd(msg_handler):
    def __init__(self, BOT, suggestion_db: SuggestionsDB, git_link: str):
        super().__init__(BOT)

        self.DB = suggestion_db
        self.git_link = git_link
        self.user_states = {}

        self.callbackquery_handler()
        self.state_handler()

    def cancel_btn(self, level: int):
        return InlineKeyboardButton(text='❌ Cancelar', callback_data=f'suggestion_cancel_add_{level}')

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        menu = '<b>Com que tipo de sugestão você quer contribuir ao bot?</b>\n\n'
        menu += '🐛 Reportar um bug que ocorre quando você usa o bot: FIX \n\n'
        menu += '✨ Sugerir uma nova funcionalidade para o bot: FEATURE \n\n'
        menu += '🤖 Outro tipo de sugestão/comentário: OUTRO \n\n'

        btn1 = InlineKeyboardButton(text='🐞 FIX', callback_data= 'suggestion_add_fix')
        btn2 = InlineKeyboardButton(text='🌟 FEATURE', callback_data= 'suggestion_add_feature')
        btn3 = InlineKeyboardButton(text='💬 OUTRO', callback_data= 'suggestion_add_outro')

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn1, btn2, btn3, self.cancel_btn(1))
                                   
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            reply_markup= keyboard,
            parse_mode='HTML',
            message_thread_id = msg.message_thread_id)

        await self.DB.maintenance_db()

    def callbackquery_handler(self):

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_cancel_add'))
        @catch_callbackquery_errors(self.BOT)
        async def cancel(call: CallbackQuery):

            level = int(call.data.split("_")[3])

            await self.BOT.delete_message(
                chat_id = call.message.chat.id,
                message_id= call.message.id
                )
            
            await self.BOT.answer_callback_query(call.id, text= "❌ Adição de sugestão cancelada!")

            if level in (2, 3,):
                if call.from_user.id in self.user_states.keys():
                    del self.user_states[call.from_user.id]           

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_add'))
        @catch_callbackquery_errors(self.BOT)
        async def what_to_add(call: CallbackQuery):
            type_of_issue = (call.data.split('_'))[2]

            await self.BOT.answer_callback_query(call.id, text=f'Opção selecionada: {type_of_issue.capitalize()}')
            
            explaning_format = f'Por favor, me envie a sua sugestão ({type_of_issue}) seguindo o seguinte formato:\n\n'
            explaning_format+= 'Titulo da sugestão: descrição da sua ideia ou do bug encontrado'

            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(self.cancel_btn(2))

            asking_for_suggestion = await self.BOT.edit_message_text(
                text=explaning_format,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=keyboard
            )

            self.user_states[call.from_user.id] = {
                "state": "awaiting_suggestion",
                "type": type_of_issue,
                "message_id": asking_for_suggestion.id
            }

        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('suggestion_confirm'))
        @catch_callbackquery_errors(self.BOT, DBError)
        async def confirm_add(call: CallbackQuery):

            user_id = call.from_user.id

            if (user_id not in self.user_states.keys() and self.user_states[user_id]['state'] != "awaiting_confirmation"):
                raise DBError(keyboard=None)
            
            state_info = self.user_states.get(user_id)

            type_of_issue = state_info["suggestion_category"]
            suggestion_title = state_info["suggestion_title"]
            suggestion_body= state_info["suggestion_body"] 

            result = await self.DB.add_db(type_of_issue, suggestion_title, suggestion_body)

            if not result.success:
                raise DBError(keyboard=None)
        
            await self.BOT.answer_callback_query(call.id, text=f'🥳 Nova sugestão adicionada com sucesso!')

            hyperlink_to_git = f'<a href="{self.git_link}">issues</a>'
            
            thanks_message1 = f'Nova sugestão adicionada com sucesso!\n • Para ver por aqui uma lista das sugestões pedentes, use o comando /suggestions_list\n • Para ver as sugestões pendentes no github, acesse as {hyperlink_to_git} abertas no repositório do telegram_bot'
            thanks_message2 = f'Muito obrigado pela sua contribuição! 😉'

            await self.BOT.edit_message_text(
                text=thanks_message1,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                disable_web_page_preview=True,
                parse_mode='HTML',
                reply_markup=None
            )

            await self.BOT.send_message(
                chat_id= call.message.chat.id,
                text= thanks_message2,
                message_thread_id= call.message.message_thread_id
            )

            del self.user_states[call.from_user.id] 

    def state_handler(self):
        @self.BOT.message_handler(func=lambda msg: msg.from_user.id in self.user_states.keys())
        async def handle_suggestion_input(msg: Message):
            user_id = msg.from_user.id
            state_info = self.user_states.get(user_id)

            if not state_info or state_info["state"] != "awaiting_suggestion":
                return 

            type_of_issue = state_info["type"]
            message_id_to_delete_inline_keyboard = state_info["message_id"]

            del self.user_states[user_id]

            await self.new_suggestion(msg, type_of_issue, message_id_to_delete_inline_keyboard)

    @catch_message_errors(PoorUseOfCommand)
    async def new_suggestion(self, msg: Message, type_of_issue: str, message_id_to_delete_inline_keyboard: int):

        await self.BOT.edit_message_reply_markup(
            chat_id=msg.chat.id,
            message_id=message_id_to_delete_inline_keyboard,
            reply_markup=None
        )

        emojis=['😍', '🔥', '❤', '😁', '💯', '🎉', '🤩', '👍']
        await self.BOT.set_message_reaction(msg.chat.id, msg.id, [ReactionTypeEmoji(choice(emojis))])


        if msg.text.find(':') == -1:
            raise PoorUseOfCommand('A formatação da sua sugestão está deviante do esperado!')

        suggestion = msg.text.split(':', 1)

        suggestion_title = suggestion[0].strip()
        suggestion_body = suggestion[1].strip()

        self.user_states[msg.from_user.id] = {
            "state": "awaiting_confirmation",
            "suggestion_category": type_of_issue,
            "suggestion_title": suggestion_title,
            "suggestion_body": suggestion_body
        }

        preview_of_suggestion = f'Confirme para mim, vamos adicionar a seguinte issue:\n\n'
        preview_of_suggestion += f'[{type_of_issue.upper()}]: <b>{suggestion_title}</b>\n'   
        preview_of_suggestion += f'<i>{suggestion_body}</i>'

        confirm_btn = InlineKeyboardButton(text= "✅ Confirmar", callback_data= f"suggestion_confirm")
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(confirm_btn, self.cancel_btn(3))

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=preview_of_suggestion,
            message_thread_id=msg.message_thread_id,
            parse_mode='HTML',
            reply_markup=keyboard
        )


class SuggestionList(msg_handler):
    def __init__(self, BOT, suggestion_db: SuggestionsDB, git_link: str):
        super().__init__(BOT)

        self.DB = suggestion_db
        self.git_link = git_link
        self.user_states = {}

        self.callbackquery_handler()

    def cancel_btn(self, level: int):
        return InlineKeyboardButton(text='❌ Cancelar', callback_data=f'suggestion_cancel_list_{level}')

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        menu = '<b>Quais issues em aberto você quer ver?</b>\n\n'
        btn0 = InlineKeyboardButton(text='📄 TODOS', callback_data= 'suggestion_list_all')
        btn1 = InlineKeyboardButton(text='🐛 FIX', callback_data= 'suggestion_list_fix')
        btn2 = InlineKeyboardButton(text='✨ FEATURE', callback_data= 'suggestion_list_feature')
        btn3 = InlineKeyboardButton(text='🤖 OUTRO', callback_data= 'suggestion_list_outro')

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn0, btn1, btn2, btn3, self.cancel_btn(1))
                                   
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            reply_markup= keyboard,
            parse_mode='HTML',
            message_thread_id = msg.message_thread_id)
        

    def callbackquery_handler(self):

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_cancel_list'))
        @catch_callbackquery_errors(self.BOT)
        async def cancel(call: CallbackQuery):

            await self.BOT.delete_message(
                chat_id = call.message.chat.id,
                message_id= call.message.id
            )
            
            await self.BOT.answer_callback_query(call.id, text= "❌ Envio de lista de issues cancelada!")

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_list'))
        @catch_callbackquery_errors(self.BOT, DBError)
        async def what_to_send(call: CallbackQuery):
            type_of_issue = (call.data.split('_'))[2]

            await self.BOT.answer_callback_query(call.id, text=f'Opção selecionada: {type_of_issue.capitalize()}')

            await self.BOT.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.id
            )
            
            if type_of_issue not in ['all', 'feature', 'fix', 'outro']:
                raise Exception(keyboard=None)
            
            type_of_issue_list = []

            if type_of_issue == "all":
                type_of_issue_list.append('feature')
                type_of_issue_list.append('fix')
                type_of_issue_list.append('outro')
                result = await self.DB.get_all_suggestions()
            
            else:
                type_of_issue_list.append(type_of_issue)
                result = await self.DB.get_specific_suggestions(type_of_issue)

            if not result.success:
                raise DBError(keyboard=None)
            
                       
            for category in type_of_issue_list:
                formatted = f'<b>{category.upper()}'

                if category in ('feature', 'outro'):
                    formatted += 'S:</b>\n\n'

                else:
                    formatted += 'ES:</b>\n\n'        

                for title, body in result.data[category]:
                    formatted += f'    -> <i>{title}: </i>'
                    formatted += f'{body}\n\n'

                await self.BOT.send_message(
                    chat_id=call.message.chat.id,
                    text=formatted,
                    parse_mode='HTML',
                    message_thread_id=call.message.message_thread_id
                )

            hyperlink_to_git = f'<a href="{self.git_link}">issues</a>'
            
            git_info = f'Para ver essas sugestões no github, acesse as {hyperlink_to_git} abertas no repositório do telegram_bot'
            
            await self.BOT.send_message(
                    chat_id =call.message.chat.id,
                    text=git_info,
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    message_thread_id=call.message.message_thread_id
            )


#class SuggestionHelper(msg_handler):
