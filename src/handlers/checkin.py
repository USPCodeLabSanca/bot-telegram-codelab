from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji, Message, CallbackQuery

from handlers.abstract import msg_handler
from dependencies.internal.abstract_db import internal_database

from random import choice
       
class handler_DB():
    def __init__(self, bot:TeleBot, DB:internal_database):
        """A classe handler_DB foi feita para auxiliar as ações comumente realizadas pelos comandos checkin
        
        :Param bot: o nosso Telebot com o token de utilização
        :Param database: o banco de dados do checkin"""

        self.DB= DB #O banco de dados

        self.BOT= bot #O bot do telegram

    def getDB(self, topic_id: int | None, chat_id: int):
        """O método getDB() acessa o banco de dados atrás dos dados inseridos por um usuário
        :Param chat_id: O id do usuário que pediu os dados
        :Return: dicionário com os dados separados por categoria | None, se não houver dados"""
        return self.DB.extrai_db(topic_id, chat_id)
    
    def is_DB_empty(self, check_atual: dict | None, chat_id: int, topic_id:int|None):
        """O método is_DB_empty() verifica se existem dados para o usuário que requisitou
        :Param check_atual: o return do método getDB
        :Param chat_id: O id do usuário que pediu os dados
        :Return: bool, True se existirem dados, False se não"""

        if not check_atual:
            self.BOT.send_message(chat_id,'Não há nada no seu check-in semanal no momento :( ', message_thread_id=topic_id)
            return True
        
        else:
            return False
       
class main_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependencies):
        super().__init__(nossoBOT, **dependencies)
        
    def __call__(self, msg: Message):
        topic = msg.message_thread_id

        menu = '<b>O que você deseja realizar?</b>\n\n'
        menu += '➕ Adicionar um novo item ao meu check-in:\n/checkin_add\n\n'
        menu += '🔎 Ver uma prévia simples do que já está no seu check-in:\n/checkin_preview\n\n'
        menu += '✨ Formatar o check-in atual:\n/checkin_format\n\n'
        menu += '🚮 Deletar o check-in atual:\n/checkin_clear\n\n'
                                   
        self.BOT.send_message(msg.chat.id, menu, parse_mode='HTML', message_thread_id= topic)

        self.DATABASE.manutencao_db()


class add_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        self.callbacks()

    def __call__(self, msg: Message):
        topic = msg.message_thread_id

        btn1_add= InlineKeyboardButton(text="✅ Adicionar tarefa realizada ✅", callback_data= "add_tar")
        btn2_add= InlineKeyboardButton(text="🚧 Adicionar dificuldade/bloqueio 🚧", callback_data= "add_des")
        btn3_add= InlineKeyboardButton(text="💬 Adicionar Comentário opicional 💬", callback_data= "add_com")

        inline_keyboard_add= InlineKeyboardMarkup(row_width=1)
        inline_keyboard_add.add(btn1_add, btn2_add, btn3_add)
        

        self.BOT.send_message(msg.chat.id, 'O que você quer adicionar ao seu check-in semanal?', reply_markup= inline_keyboard_add, message_thread_id=topic)
        
    def callbacks(self):
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('add'))
        def oque_vamos_adicionar(call: CallbackQuery):
            self.BOT.answer_callback_query(call.id)

            mensagens_para_cada_opcao = {
            'add_tar': 'Qual foi a tarefa realizada? \nPara anular, responda "none"',
            'add_des': 'Qual foi a dificuldade encontrada? \nPara anular, responda "none"',
            'add_com': 'Qual comentario a ser adicionado? \nPara anular, responda "none"'
            }

            topic= call.message.message_thread_id

            if call.data in mensagens_para_cada_opcao.keys():
                self.BOT.send_message(call.message.chat.id, mensagens_para_cada_opcao[call.data], message_thread_id=topic)
                self.BOT.register_next_step_handler_by_chat_id(call.message.chat.id, self.new_item, call.data, topic)


    def new_item(self, msg:Message, categoria: str, topic_id: int | None):
        answer= msg.text.lower().strip()
        if (answer== 'none'):
            return
        
        topic= topic_id or msg.message_thread_id

        if (categoria=='add_tar'):
            cat= 'tasks'
            prefix =  f'✅ Tarefa adicionada'
            error= False
            
        elif (categoria=='add_des'):
            cat= 'challenges'
            prefix= f'🚧 Dificuldade adicionada'
            error= False
            
        elif (categoria=='add_com'):
            cat= "comments"
            prefix = f'💬 Comentário adicionado'
            error = False
           
        else:
            error= True

        if error:
            self.BOT.send_message(msg.chat.id, f'Erro ao acrescentar: <i>{answer.capitalize()}</i>\nDeseja tentar adicionar um novo item? /checkin_add', parse_mode='HTML', message_thread_id=topic)

        else:          
            self.DATABASE.add_db(-1 if not topic else topic, msg.chat.id, cat, answer.capitalize())
            self.BOT.send_message(msg.chat.id, f'{prefix}: <i>{answer.capitalize()}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML', message_thread_id=topic)


class preview_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        self.db_handler= handler_DB(nossoBOT, self.DATABASE)

    def __call__(self, msg: Message):
        topic= msg.message_thread_id

        current_checkin=self.db_handler.getDB(-1 if not topic else topic, msg.chat.id)

        if self.db_handler.is_DB_empty(current_checkin, msg.chat.id, topic):
            return

        preview= f'Tarefas realizadas:\n'
        for tas in current_checkin['tasks']:
            preview+= f'    -{tas}\n'

        preview+= f'\nDesafios encontrados:\n'
        for cha in current_checkin['challenges']:
                preview+= f'    -{cha}\n'
        
        preview+= f'\nComentários adicionais:\n'
        for com in current_checkin['comments']:
            preview+= f'    -{com}\n'

        self.BOT.send_message(msg.chat.id, preview, message_thread_id=topic)


class format_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)

        self.db_handler= handler_DB(nossoBOT, self.DATABASE)

    def __call__(self, msg: Message):

        topic= msg.message_thread_id

        current_checkin=self.db_handler.getDB(-1 if not topic else topic, msg.chat.id)

        if self.db_handler.is_DB_empty(current_checkin, msg.chat.id, topic):
            return

        reply= f'<b>Check-in semanal</b>\n\n'

        reply+= '✅ Progresso dessa semana:\n'
        for tas in current_checkin['tasks']:
            reply+= f' • {tas.capitalize()}\n'

        reply+= '\n🚧 Bloqueios / dificuldades:\n'
        for chal in current_checkin['challenges']:
            reply+= f' • {chal.capitalize()}\n'

        reply+= '\n💬 Comentários adicionais (opcional):\n'
        for com in current_checkin['comments']:
            reply+= f' • {com.capitalize()}\n'

        checkin_sent= self.BOT.send_message(msg.chat.id, reply, parse_mode='HTML', message_thread_id=topic)
        emojis=['😍', '🔥', '❤', '😁', '💯', '🦄', '🎉', '🤩', '👍']
        self.BOT.set_message_reaction(checkin_sent.chat.id, checkin_sent.id, [ReactionTypeEmoji(choice(emojis))])

class clear_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        self.callbacks()

        self.db_handler= handler_DB(nossoBOT, self.DATABASE)
        
    def __call__(self, msg: Message):
        topic= msg.message_thread_id

        current_checkin=self.db_handler.getDB(-1 if not topic else topic, msg.chat.id)

        if self.db_handler.is_DB_empty(current_checkin, msg.chat.id, topic):
            return
        
        btn1_clear= InlineKeyboardButton(text="SIM", callback_data= "clear_sim")
        btn2_clear= InlineKeyboardButton(text="NÃO", callback_data= "clear_nao")
        inline_keyboard_clear= InlineKeyboardMarkup(row_width=2)
        inline_keyboard_clear.add(btn1_clear, btn2_clear)
        
        if msg.chat.type== 'private':
            warning= '<b>WARNING:</b> Tem certeza que você deseja apagar o seu check-in atual?\n<b>Essa ação não pode ser desfeita!</b>'

        else:
            warning= '<b>WARNING:</b> Tem certeza que você deseja apagar o check-in atual de <u>todo</u> o grupo? <b>Essa ação não pode ser desfeita!</b>'

        self.BOT.send_message(msg.chat.id, warning, reply_markup= inline_keyboard_clear, parse_mode='HTML', message_thread_id=topic)

        
    def callbacks(self):
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('clear'))
        def temCerteza(call: CallbackQuery):

            topic = call.message.message_thread_id

            if call.data == "clear_sim":
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Pronto! Check-in semanal esvaziado!', message_thread_id=topic)

                self.DATABASE.deleta_db(-1 if not topic else topic, call.message.chat.id)

            elif call.data == 'clear_nao':
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Ok! Seu check-in não foi esvaziado!', message_thread_id=topic)

            else:
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id, 'Erro ao processar o comando /checkin_clear', message_thread_id=topic)