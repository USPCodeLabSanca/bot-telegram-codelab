from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji, Message, CallbackQuery

from handlers.abstract import msg_handler
from utils.errors import catch_callbackquery_errors, catch_message_errors

from dependencies.internal.suggestions_db import SuggestionsDB
from dependencies.internal.bot_errors import DBError, PoorUseOfCommand, ExecutionError

from random import choice
import json
from datetime import datetime
import requests
import aiohttp

class SuggestionMain(msg_handler):
    def __init__(self, BOT):
        """A classe SuggestionMain envia um menu para o usuário contendo opções de ações 
        (vizualizar ou adicionar) e aconselha sobre como contribuir da melhor maneira"""

        super().__init__(BOT) # Inicializa a classe pai com a instância do bot

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        # Construção do menu com opções e ajuda
        menu = '<b>O que você deseja realizar?</b>\n\n'

        menu += '➕ Contribuir com uma sugestão de melhoria para o BOT_A_SER_NOMEADO:\n/suggestion_add\n\n'
        menu += '📂 Ver sugestões pendentes para o BOT_A_SER_NOMEADO:\n/suggestion_list\n\n'

        menu += 'Para cooperar com uma sugestão clara e bem elaborada, é recomendado'
        menu += ' o uso do comando /suggestion_guide para ler instruções, dicas e exemplos de'
        menu += ' como construir uma issue de maneira adequada e também o uso comando /suggestion_list'
        menu += ' para evitar issues repetidas ou muito similares'

        # Envia o menu para o usuário
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id)


class SuggestionAdd(msg_handler):
    def __init__(self, BOT, suggestion_db: SuggestionsDB, git_link: str, git_api: str, git_token: str, session: aiohttp.ClientSession ):
        """A classe SuggestionAdd recebe a sugestão com qual o usuário deseja contribuir.
        Primeiro é decidido qual tipo de sugestão será adicionada, depois faz-se a validação
        e a confirmação. A manutenção do banco de dados também é feita aqui"""

        super().__init__(BOT)

        self.DB = suggestion_db # A clase do banco de dados de sugestões
        self.git_link = git_link # O link para as issues do BOT_A_SER_NOMEADO no github do Codelab
        self.user_states = {} # Dicionário que guarda os estados de usuários
        self.git_api = git_api
        self.git_token = git_token
        self.session = session

        self.callbackquery_handler() # Aciona as callback_queries
        self.state_handler() # Aciona o manejo de estados



    def cancel_btn(self, level: int):
        """Retorna um botão de cancelar para incluir nos keyboards"""
        return InlineKeyboardButton(text='❌ Cancelar', callback_data=f'suggestion_cancel_add_{level}')

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        # Aqui é construido o menu para selecionar qual tipo de issue será adicionado
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

        #BOTÃO DE CANCELAR
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_cancel_add'))
        @catch_callbackquery_errors(self.BOT)
        async def cancel(call: CallbackQuery):

            level = int(call.data.split("_")[3])

            # Deleta a mensagem que possuia o botão de cancelar
            await self.BOT.delete_message(
                chat_id = call.message.chat.id,
                message_id= call.message.id
            )
            
            # Avisa o usuário do cancelamento
            await self.BOT.answer_callback_query(call.id, text= "❌ Adição de sugestão cancelada!")

            # Se o nível de cancelamento for 2 ou 3, é necessário remover o usuário do dicionário de estados
            if level in (2, 3,) and call.from_user.id in self.user_states.keys():
                del self.user_states[call.from_user.id]           

        # BOTÃO DE QUAL CATEGORIA
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_add'))
        @catch_callbackquery_errors(self.BOT)
        async def what_to_add(call: CallbackQuery):
            type_of_issue = (call.data.split('_'))[2]

            await self.BOT.answer_callback_query(call.id, text=f'Opção selecionada: {type_of_issue.capitalize()}')
            
            # Explicação de como enviar sugestão
            explaning_format = f'Por favor, me envie a sua sugestão ({type_of_issue}) seguindo o seguinte formato:\n\n'
            explaning_format+= 'Titulo da sugestão: descrição da sua ideia ou do bug encontrado'

            # Keyboard com botão de cancelar
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(self.cancel_btn(2))

            # Edita o menu inicial (do método __call__) para pedir que o usuário envie a sugestão
            asking_for_suggestion = await self.BOT.edit_message_text(
                text=explaning_format,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=keyboard
            )

            # Adiciona o usuário no dicionário de estados, para que seja possível ler a sugestão que ele incrementa
            self.user_states[call.from_user.id] = {
                "state": "awaiting_suggestion",
                "type": type_of_issue,
                "message_id": asking_for_suggestion.id
            }

        # BOTÃO DE CONFIRMAR OU CANCELAR
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('suggestion_confirm'))
        @catch_callbackquery_errors(self.BOT, DBError)
        async def confirm_add(call: CallbackQuery):

            user_id = call.from_user.id

            # Verifica se o usuário está aguardando confirmação
            if (user_id not in self.user_states.keys() and self.user_states[user_id]['state'] != "awaiting_confirmation"):
                raise DBError()
            
            state_info = self.user_states.get(user_id)

            type_of_issue = state_info["suggestion_category"]
            suggestion_title = state_info["suggestion_title"]
            suggestion_body= state_info["suggestion_body"] 

            # Adiciona ao banco de dados
            result_db = await self.DB.add_db(type_of_issue, suggestion_title, suggestion_body)

            if not result_db.success:
                raise DBError()

            # Adiciona ao git
            result_git = await self.add_to_git(type_of_issue, suggestion_title, suggestion_body)
            result_git.raise_for_status()

            await self.BOT.answer_callback_query(call.id, text=f'🥳 Nova sugestão adicionada com sucesso!')

            # Mensagens de agradecimento e confirmação
            hyperlink_to_git = f'<a href="{self.git_link}">issues</a>'
            thanks_message1 = f'Nova sugestão adicionada com sucesso!\n • Para ver por aqui uma lista das sugestões pedentes, use o comando /suggestion_list\n • Para ver as sugestões pendentes no github, acesse as {hyperlink_to_git} abertas no repositório do telegram_bot'
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

            # Remove o usuário do dicionário de estados
            del self.user_states[call.from_user.id] 

    def state_handler(self):
        @self.BOT.message_handler(func=lambda msg: msg.from_user.id in self.user_states.keys())
        async def handle_suggestion_input(msg: Message):
            user_id = msg.from_user.id
            state_info = self.user_states.get(user_id)

            # Verifica qual o estado do usuário 
            if not state_info or state_info["state"] != "awaiting_suggestion":
                return 

            type_of_issue = state_info["type"]
            message_id_to_delete_inline_keyboard = state_info["message_id"]

            # Remove o usuário do dicionário de estados
            del self.user_states[user_id]

            # Chama a função que processa a sugestão
            await self.new_suggestion(msg, type_of_issue, message_id_to_delete_inline_keyboard)

    @catch_message_errors(PoorUseOfCommand)
    async def new_suggestion(self, msg: Message, type_of_issue: str, message_id_to_delete_inline_keyboard: int):

        # Deleta o botão de cancelar da mensagem que pediu pela sugestão
        await self.BOT.edit_message_reply_markup(
            chat_id=msg.chat.id,
            message_id=message_id_to_delete_inline_keyboard,
            reply_markup=None
        )

        # Validação de titulo e corpo de texto
        if msg.text.find(':') == -1:
            raise PoorUseOfCommand(
                error_text='É necessário separar o título e o corpo de texto com dois-pontos (:)!',
                reply=True
                )
        
        # Validação de tamanho
        if len(msg.text) > 600:
            raise PoorUseOfCommand(
                error_text='Você excedeu o tamanho máximo de caracteres permitidos por sugestão (600)!',
                reply=True
                )

        # Extração do título e corpo de texto
        suggestion = msg.text.split(':', 1)
        suggestion_title = suggestion[0].strip()
        suggestion_body = suggestion[1].strip()

        # Dá uma reaçãozinha para o usuário
        emojis = ['😍', '🔥', '❤', '😁', '💯', '🎉', '🤩', '👍']
        await self.BOT.set_message_reaction(msg.chat.id, msg.id, [ReactionTypeEmoji(choice(emojis))])

        # Adiciona o usuário ao dicionário de estados como "aguardando confirmação"
        self.user_states[msg.from_user.id] = {
            "state": "awaiting_confirmation",
            "suggestion_category": type_of_issue,
            "suggestion_title": suggestion_title,
            "suggestion_body": suggestion_body
        }

        # Mensagem de confirmação
        preview_of_suggestion = f'Confirme para mim, vamos adicionar a seguinte issue:\n\n'
        preview_of_suggestion += f'[{type_of_issue.upper()}]: <b>{suggestion_title}</b>\n'   
        preview_of_suggestion += f'<i>{suggestion_body}</i>'

        # Keyboard de confirmação
        btn1 = InlineKeyboardButton(text= "✅ Confirmar", callback_data= f"suggestion_confirm")
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn1, self.cancel_btn(3))

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=preview_of_suggestion,
            message_thread_id=msg.message_thread_id,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    async def add_to_git(self, type_of_issue: str, title: str, body: str):
        
        #Adiciona a issue ao github do codelab

        # Valida a categoria
        if type_of_issue == "feature":
            label = ["idea", "enhancement"]
            type = type_of_issue

        elif type_of_issue == "fix":
            label = ["bug", "Change"]
            type = "bug"

        elif type_of_issue == "outro":
            label = []
            type = None
            
        else:
            raise ValueError('Categoria de sugestão inválida!')

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.git_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        json = {
            "title": f"{type_of_issue.capitalize()}: {title}",
            "body": body,
            "labels": label,
            "type": type
        }

        response = await self.session.post(self.git_api, headers=headers, json=json)
        return response
     

class SuggestionList(msg_handler):
    def __init__(self, BOT, suggestion_db: SuggestionsDB, git_link: str):
        """A classe SuggestionList envia uma lista de issues em aberto para o usuário"""
        super().__init__(BOT)

        self.DB = suggestion_db # A clase do banco de dados de sugestões
        self.git_link = git_link # O link para as issues do BOT_A_SER_NOMEADO no github do Codelab

        self.callbackquery_handler() # Aciona as callback_queries

    def cancel_btn(self, level: int):
        """Retorna um botão de cancelar para incluir nos keyboards"""
        return InlineKeyboardButton(text='❌ Cancelar', callback_data=f'suggestion_cancel_list_{level}')

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        #Constrói o menu com os botões de cada tipo de issue

        menu = '<b>Quais issues em aberto você quer ver?</b>\n\n'
        btn1 = InlineKeyboardButton(text='📄 TODOS', callback_data= 'suggestion_list_all')
        btn2 = InlineKeyboardButton(text='🐛 FIX', callback_data= 'suggestion_list_fix')
        btn3 = InlineKeyboardButton(text='✨ FEATURE', callback_data= 'suggestion_list_feature')
        btn4 = InlineKeyboardButton(text='🤖 OUTRO', callback_data= 'suggestion_list_outro')

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn1, btn2, btn3, btn4, self.cancel_btn(1))
                                   
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            reply_markup=keyboard,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id)
        

    def callbackquery_handler(self):

        # BOTÃO DE CANCELAR
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_cancel_list'))
        @catch_callbackquery_errors(self.BOT)
        async def cancel(call: CallbackQuery):

            await self.BOT.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.id
            )
            
            await self.BOT.answer_callback_query(call.id, text= "❌ Envio de lista de issues cancelada!")

        # BOTÃO DE QUAL CATEGORIA ENVIAR
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_list'))
        @catch_callbackquery_errors(self.BOT, DBError)
        async def what_to_send(call: CallbackQuery):
            
            # Encontra a categoria de issues que será buscada na database
            type_of_issue = (call.data.split('_'))[2]

            await self.BOT.answer_callback_query(call.id, text=f'Opção selecionada: {type_of_issue.capitalize()}')
           
           # Valida a categoria
            if type_of_issue not in ['all', 'feature', 'fix', 'outro']:
                raise ValueError('Categoria de sugestão inválida!')
            
            type_of_issue_list = ["feature", "fix", "outro"] if type_of_issue == "all" else [type_of_issue]
            
            # Busca no banco de dados
            result = await self.DB.get_all_suggestions() if type_of_issue == "all" else await self.DB.get_specific_suggestions(type_of_issue)

            if not result.success:
                raise DBError()
            
            # Caso a database estiver vazia
            if result.data == None:
                hyperlink_to_git = f'<a href="{self.git_link}">github</a>'

                await self.BOT.edit_message_text(
                    text=f'Não há issues em aberto {"desta categoria " if type_of_issue != "all" else ""}aqui no Telegram. Confira no {hyperlink_to_git} do projeto!',
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    reply_markup=None,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                return            

            await self.BOT.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.id
            )
                
            suggestions_dict = {category: [] for category in type_of_issue_list}
            
            for category in type_of_issue_list:
                # Quebra as listas grandes de sugestões em listas menores de até 5 itens
                smaller_lists = [result.data[category][i:i + 5] for i in range(0, len(result.data[category]), 5)]
                suggestions_dict[category] = smaller_lists if smaller_lists else [[]]              

            for category, small_lists in suggestions_dict.items():
                
                # Define o plural da categoria escolhida
                plural = f'{category}s' if category in ('feature', 'outro') else f'{category}es'

                for index, small_list in enumerate(small_lists):
                    if small_list:
                        # Cabeçalho da mensagem
                        formatted =  f'<b>{plural.upper()}: [{index * 5 + 1} a {index * 5 + len(small_list)}]</b>\n\n' 

                        # Issues formatadas
                        formatted += ''.join(f'    <b>-></b> <i>{title}:</i> {body}\n\n' for title, body in small_list)

                        await self.BOT.send_message(
                            chat_id=call.message.chat.id,
                            text=formatted,
                            parse_mode='HTML',
                            message_thread_id=call.message.message_thread_id
                        )

                    else:
                        formatted = f'<b>Não há issues do tipo {plural}!</b>'

                        await self.BOT.send_message(
                            chat_id=call.message.chat.id,
                            text=formatted,
                            parse_mode='HTML',
                            message_thread_id=call.message.message_thread_id
                        )

            # Informações do git
            hyperlink_to_git = f'<a href="{self.git_link}">issues</a>'            
            git_info = f'Para ver essas sugestões no github, acesse as {hyperlink_to_git} abertas no repositório do telegram_bot'
            
            await self.BOT.send_message(
                chat_id=call.message.chat.id,
                text=git_info,
                parse_mode='HTML',
                disable_web_page_preview=True,
                message_thread_id=call.message.message_thread_id
            )


class SuggestionHelper(msg_handler):
    def __init__(self, BOT, examples_json):
        """A classe SuggestionHelper envia um guia de como contribuir com uma sugestão da melhor maneira possível"""
        super().__init__(BOT)
        
        with open(examples_json, "r", encoding="utf-8") as file:
            self.examples_dict = json.load(file) # Exemplos de sugestões

        self.callbackquery_handler() # Aciona as callbackqueries

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        # Construção do guia 

        guide = '<b>GUIA PARA CONSTRUÇÃO DE ISSUES:</b>\n\n'

        guide1 = '<b>1. Regras:</b>\n'
        guide1 += '   <b>-></b> Uma issue deve conter um <b>título</b> e um <b>corpo de texto</b>, separados por dois-pontos (:)\n'
        guide1 += '   <b>-></b> Uma issue deve conter <b>no máximo 600</b> caractéres\n\n'
        
        guide2 = '<b>2. Instruções e dicas:</b>\n'
        guide2 += '   <b>-></b> A issues são divididas em <b>3</b> categorias:\n'
        guide2 += '      • <b>feature</b> - Descreve alguma ideia de funcionalidade nova que seria interessante implementar no bot\n'
        guide2 += '      • <b>fix</b> - Descreve algum bug que acontece durante o uso do bot\n'
        guide2 += '      • <b>outro</b> - Descreve algum outro tipo de sugestão que não seja um bug para consertar ou uma funcionalidade nova\n\n'

        guide2 += '   <b>-></b> Para redigir uma <b><i>feature</i></b>, recomenda-se incluir:\n'
        guide2 += '      • Descrição da "lacuna" que a sua sugestão preencheria\n'
        guide2 += '      • Descrição da solução que a sua sugestão apresenta para tal "lacuna"\n\n'

        guide2 += '   <b>-></b> Para redigir um <b><i>fix</i></b>, recomenda-se incluir:\n'
        guide2 += '      • Descrição do bug que está ocorrendo\n'
        guide2 += '      • Etapas de como outra pessoa poderia reproduzir o bug\n'
        guide2 += '      • Descrição do comportamento esperado, caso não existesse o bug\n'
        guide2 += '      • Caso você julgue pertinente, inclua contextos adicionais, como o seu sistema operacional, navegador, etc\n\n'

        guide2 += '   <b>-></b> Para redigir um <b><i>outro</i></b>, recomenda-se incluir qualquer informação que você julgar pertinente\n'

        guide3 = '<b>3. Exemplos práticos:</b>\n'
        guide3 += '   <b>-></b> Consulte abaixo alguns exemplos disponíveis de sugestões\n'

        btn1 = InlineKeyboardButton(text='🌟 Exemplo de sugestão de feature', callback_data='suggestion_example_feature')
        btn2 = InlineKeyboardButton(text='🐛 Exemplo de sugestão de fix', callback_data='suggestion_example_fix')
        btn3 = InlineKeyboardButton(text='💬 Exemplo de sugestão de outro', callback_data='suggestion_example_outro')

        keyboard = InlineKeyboardMarkup(row_width=1)

        keyboard.add(btn1, btn2, btn3)

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=guide,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id
        )

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=guide1,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id
        )

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=guide2,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id
        )

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=guide3,
            parse_mode='HTML',
            message_thread_id=msg.message_thread_id,
            reply_markup= keyboard
        )

    def callbackquery_handler(self):

        # BOTÃO DE EXEMPLO
        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('suggestion_example'))
        @catch_callbackquery_errors(self.BOT)
        async def example(call: CallbackQuery):
            
            type_of_issue = call.data.split("_")[2]

            await self.BOT.answer_callback_query(call.id, text= f"Mostrando exemplo de {type_of_issue}")

            suggestion_example = f'<b>EXEMPLO DE SUGESTÃO DE {type_of_issue.upper()}:</b>\n\n'
            suggestion_example += choice(self.examples_dict[type_of_issue])

            await self.BOT.send_message(
                chat_id=call.message.chat.id,
                text= suggestion_example,
                parse_mode='HTML',
                message_thread_id=call.message.message_thread_id
            )


class BuggedCommand(msg_handler):
    def __init__(self, BOT):
        """A classe BuggedCommand é um exemplo de comando mal funcional para ilustrar o SuggestionHelper"""
        
        super().__init__(BOT)
        self.callbackquery_handler()

    @catch_message_errors() 
    async def __call__(self, msg: Message):

        today = datetime.now()

        #Não é pra funcionar quintas feiras
        if today.weekday() == 3:
            return
        
        menu = '😃 Eu sou um bug!'
        btn1 = InlineKeyboardButton(text='bug 1', callback_data= 'bug_1')
        btn2 = InlineKeyboardButton(text='bug 2', callback_data= 'bug_2')

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn1, btn2)


        #Envia 2 vezes a mesma mensagem                        
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            reply_markup= keyboard,
            parse_mode='HTML',
            message_thread_id = msg.message_thread_id)
        
        await self.BOT.send_message(
            msg.chat.id,
            menu,
            reply_markup= keyboard,
            parse_mode='HTML',
            message_thread_id = msg.message_thread_id)
        

    def callbackquery_handler(self):

        @self.BOT.callback_query_handler(func=lambda call: call.data.startswith('bug_2'))
        @catch_callbackquery_errors(self.BOT)
        async def error(call: CallbackQuery):
           
            await self.BOT.answer_callback_query(call.id, text= "⚠️ ERRO!!!")

            raise ExecutionError(edit_msg=call.message)
