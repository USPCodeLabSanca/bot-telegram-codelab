from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji, Message, CallbackQuery

from handlers.abstract import msg_handler
       
class handler_DB():
    def __init__(self, bot:TeleBot, DB):
        """A classe handler_DB foi feita para auxiliar as ações comumente realizadas pelos comandos checkin
        
        :Param bot: o nosso Telebot com o token de utilização
        :Param database: o banco de dados do checkin"""

        self.DB= DB #O banco de dados

        self.BOT= bot #O bot do telegram

    def getDB(self, chat_id: int):
        """O método getDB() acessa o banco de dados atrás dos dados inseridos por um usuário
        :Param chat_id: O id do usuário que pediu os dados
        :Return: dicionário com os dados separados por categoria | None, se não houver dados"""

        return self.DB.extrai_db(chat_id)
    
    def is_DB_empty(self, check_atual: dict | None, chat_id: int):
        """O método is_DB_empty() verifica se existem dados para o usuário que requisitou
        :Param check_atual: o return do método getDB
        :Param chat_id: O id do usuário que pediu os dados
        :Return: bool, True se existirem dados, False se não"""

        if not check_atual:
            self.BOT.send_message(chat_id,'Não há nada no seu check-in semanal no momento :( ')
            return True
        
        else:
            return False
       
class checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        
    def __call__(self, msg: Message):
        redirect= f'<b>O que você deseja realizar?</b>\n\n'
        redirect+=f'➕ Adicionar um novo item ao meu check-in:\n/checkin_add\n\n'
        redirect+=f'🔎 Ver uma prévia simples do que já está no seu check-in:\n/checkin_preview\n\n'
        redirect+=f'✨ Formatar o check-in atual:\n/checkin_format\n\n'
        redirect+=f'🚮 Deletar o check-in atual:\n/checkin_clear\n\n'

        self.BOT.send_message(msg.chat.id, redirect, parse_mode='HTML')

        self.DATABASE.manutencao_db()
        
class add_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        self.callbacks()

    def __call__(self, msg: Message):
        btn1_add= InlineKeyboardButton(text="✅ Adicionar tarefa realizada ✅", callback_data= "add_tar")
        btn2_add= InlineKeyboardButton(text="🚧 Adicionar dificuldade/bloqueio 🚧", callback_data= "add_des")
        btn3_add= InlineKeyboardButton(text="💬 Adicionar Comentário opicional 💬", callback_data= "add_com")

        inline_keyboard_add= InlineKeyboardMarkup(row_width=1)
        inline_keyboard_add.add(btn1_add, btn2_add, btn3_add)

        self.BOT.send_message(msg.chat.id, 'O que você quer adicionar ao seu check-in semanal?', reply_markup= inline_keyboard_add)

    def callbacks(self):
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('add'))
        def oque_vamos_adicionar(call: CallbackQuery):
            self.BOT.answer_callback_query(call.id)

            mensagens_para_cada_opcao = {
            'add_tar': 'Qual foi a tarefa realizada? \nPara anular, responda "none"',
            'add_des': 'Qual foi a dificuldade encontrada? \nPara anular, responda "none"',
            'add_com': 'Qual comentario a ser adicionado? \nPara anular, responda "none"'
            }

            if call.data in mensagens_para_cada_opcao.keys():
                self.BOT.send_message(call.message.chat.id, mensagens_para_cada_opcao[call.data])
                self.BOT.register_next_step_handler(call.message, self.le_Resposta, call.data)


    def le_Resposta(self, msg:Message, categoria: str):

        answer= msg.text.lower().strip()

        if (answer== 'none'):
            return
        
        answer= answer.capitalize()
        if (categoria=='add_tar'):
            self.DATABASE.add_db(msg.from_user.id, msg.chat.id, 'tarefas', answer)
            self.BOT.send_message(msg.chat.id, f'✅ Tarefa adicionada: <i>{answer}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML')

        elif (categoria=='add_des'):
            self.DATABASE.add_db(msg.from_user.id, msg.chat.id, 'desafios', answer)
            self.BOT.send_message(msg.chat.id, f'🚧 Dificuldade adicionada: <i>{answer}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML')

        elif (categoria=='add_com'):
            self.DATABASE.add_db(msg.from_user.id, msg.chat.id, 'comentarios', answer)
            self.BOT.send_message(msg.chat.id, f'💬 Comentário adicionado: <i>{answer}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML')

        else:
            self.BOT.send_message(msg.chat.id, f'Erro ao acrescentar: <i>{answer}</i>\nDeseja tentar adicionar um novo item? /checkin_add', parse_mode='HTML')

class preview_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        self.db_handler= handler_DB(nossoBOT, self.DATABASE)

    def __call__(self, msg: Message):

        checkin_atual=self.db_handler.getDB(msg.chat.id)

        if self.db_handler.is_DB_empty(checkin_atual, msg.chat.id):
            return

        preview= f'Tarefas realizadas:\n'
        for t in checkin_atual['tarefas']:
            preview+= f'    -{t}\n'

        preview+= f'\nDesafios encontrados:\n'
        for d in checkin_atual['desafios']:
                preview+= f'    -{d}\n'
        
        preview+= f'\nComentários adicionais:\n'
        for c in checkin_atual['comentarios']:
            preview+= f'    -{c}\n'

        self.BOT.send_message(msg.chat.id, preview)


class format_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)

        self.db_handler= handler_DB(nossoBOT, self.DATABASE)

    def __call__(self, msg: Message):
        checkin_atual=self.db_handler.getDB(msg.chat.id)

        if self.db_handler.is_DB_empty(checkin_atual, msg):
            return

        title = (f'<b>Check-in semanal</b>')
        bullet_char = " • "
        reply= f'{title}\n\n'
        reply+= '✅ Progresso dessa semana:\n'
        for tar in checkin_atual['tarefas']:
            reply+= f'{bullet_char}{tar.capitalize()}\n'

        reply+= '\n🚧 Bloqueios / dificuldades:\n'
        for des in checkin_atual['desafios']:
            reply+= f'{bullet_char}{des.capitalize()}\n'

        reply+= '\n💬 Comentários adicionais (opcional):\n'
        for com in checkin_atual['comentarios']:
            reply+= f'{bullet_char}{com.capitalize()}\n'

        checkin_sent= self.BOT.send_message(msg.chat.id, reply, parse_mode='HTML')

        from random import choice
        from time import sleep
        emojis=['😍', '🔥', '❤', '😁', '💯', '🦄', '🎉', '🤩', '👍']
        emoji_para_reagir = choice(emojis)
        sleep(1.5)
        self.BOT.set_message_reaction(checkin_sent.chat.id, checkin_sent.id, [ReactionTypeEmoji(emoji_para_reagir)])


class clear_checkin(msg_handler):
    def __init__(self, nossoBOT, **dependecies):
        super().__init__(nossoBOT, **dependecies)
        self.callbacks()

        self.db_handler= handler_DB(nossoBOT, self.DATABASE)
        
    def __call__(self, msg: Message):
        checkin_atual=self.db_handler.getDB(msg.chat.id)

        if self.db_handler.is_DB_empty(checkin_atual, msg.chat.id):
            return
        
        btn1_clear= InlineKeyboardButton(text="SIM", callback_data= "clear_sim")
        btn2_clear= InlineKeyboardButton(text="NÃO", callback_data= "clear_nao")
        inline_keyboard_clear= InlineKeyboardMarkup(row_width=2)
        inline_keyboard_clear.add(btn1_clear, btn2_clear)

        if msg.chat.type== 'private':
            warning= '<b>WARNING:</b> Tem certeza que você deseja apagar o seu check-in atual?\n<b>Essa ação não pode ser desfeita!</b>'

        else:
            warning= '<b>WARNING:</b> Tem certeza que você deseja apagar o check-in atual de <u>todo</u> o grupo? <b>Essa ação não pode ser desfeita!</b>'

        self.BOT.send_message(msg.chat.id, warning, reply_markup= inline_keyboard_clear, parse_mode='HTML')
    
    def callbacks(self):
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('clear'))
        def temCerteza(call: CallbackQuery):
            if call.data == "clear_sim":
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Pronto! Check-in semanal esvaziado!')

                self.DATABASE.deleta_db(call.message.chat.id)

            elif call.data == 'clear_nao':
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Ok! Seu check-in não foi esvaziado!')

            else:
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Erro ao processar o comando /checkin_clear')
