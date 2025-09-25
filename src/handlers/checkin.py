import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji, Message, CallbackQuery
from handlers.dados_checkin import Check_in_db

class Check_in:
    def __init__(self, nossoBot:telebot.TeleBot):
        """A classe Check_in é utilizada para gerenciar todos os comandos do nosso bot do telegram
        que envolvam a criação ou a manutenção do relatório semanal estipulado pelo dev.boost
        
        :Parâmetro nossoBot: este é o bot em si, que foi criado no app.py com o token de ativação
        providenciado pelo BotFather
        """

        #Nosso mini banco de dados para guardar o que cada usuário/grupo adicionou ao seu relatório semanal
        self.DATABASE= Check_in_db() 

        #Telebot com o token
        self.BOT= nossoBot 

        #Método que contém todos os handlers de comando/ativa as callbacks
        self.main()

    
    def getDB_s(self, user_id: int, chat_id: int):
        #AINDA NÃO ESTÁ EM USO
        """O método getDB_s é pretendido para grupos, em que se deseja apenas coletar os dados 
        inseridos no relatório por um único usuário, ao invés de tudo que o grupo inseriu
        
        :Parâmetro user_id: int do usuário que pediu os dados
        :Parâmetro chat_id: int da conversa em que foi pedido os dados
        :Return: dicionário com os dados dividos entre os campos 'tarefas', 'desafios' e 'comentarios' | None, se não houver dados """

        return self.DATABASE.extrai_db_s(user_id, chat_id)
    
    def getDB_a(self, chat_id: int):
        """O método getDB_a coleta os dados inseridos no relatório por todos os usuários que estão 
        naquele chat, seja uma conversa privada com o bot ou em um grupo com vários participantes
        
        :Parâmetro chat_id: int da conversa em que foi pedido os dados
        :Return: dicionário com os dados dividos entre os campos 'tarefas', 'desafios' e 'comentarios' | None, se não houver dados"""

        return self.DATABASE.extrai_db_a( chat_id)
    
    def is_db_empty(self, check_atual: dict | None, msg: Message):
        """O método is_db_empty verifica se não existem entradas do usuário que requisitou
        
        :Parâmetro check_atual: dicionário com dados | None, se não houver dados
        :Parâmetro msg: Mensagem do telegram que pediu pelos dados
        :Return: bool, True se não houver dados | False se houver"""

        if not check_atual:
            self.BOT.send_message(msg.chat.id,'Não há nada no seu check-in semanal no momento :( ')
            return True
        
        else:
            return False
        
    def preview_checkin(self, msg: Message):
        """O método preview_checkin permite que o usuário veja uma prévia de como está o seu 
        relatório antes de enviar o formatado
        
        :Parâmetro msg: Mensagem do telegram que pediu o preview"""

        #Pega os dados que estão neste relátorio para escrever o preview
        checkin_atual = self.getDB_a(msg.chat.id)

        #Se não há nada no checkin_atual, não há porque mostrar uma prévia
        if self.is_db_empty(checkin_atual, msg):
            return
        
        #O preview é uma string simples com as informações que já estão no check-in
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


    def clear_checkin(self, msg: Message):
        """O método clear_checkin remove tudo o que havia sido adicionado antes pelo usuário
        
        :Parâmetro msg: Mensagem do telegram que pediu para deletar os dados"""

        #Pega os dados na database para ver se tem alguma coisa para apagar
        checkin_atual = self.getDB_a(msg.chat.id)

        #Se não há nada no checkin_atual, não há nada pra deletar
        if self.is_db_empty(checkin_atual, msg):
            return
        
        #Teclado para perguntar/confirmar se o usário queria mesmo apagar todo o checkin
        btn1_clear= InlineKeyboardButton(text="SIM", callback_data= "clear_sim")
        btn2_clear= InlineKeyboardButton(text="NÃO", callback_data= "clear_nao")
        inline_keyboard_clear= InlineKeyboardMarkup(row_width=2)
        inline_keyboard_clear.add(btn1_clear, btn2_clear)

        if msg.chat.type== 'private':
            warning= '<b>WARNING:</b> Tem certeza que você deseja apagar o seu check-in atual?\n<b>Essa ação não pode ser desfeita!</b>'

        else:
            warning= '<b>WARNING:</b> Tem certeza que você deseja apagar o check-in atual de <u>todo</u> o grupo? <b>Essa ação não pode ser desfeita!</b>'

        self.BOT.send_message(msg.chat.id, warning, reply_markup= inline_keyboard_clear, parse_mode='HTML')

    def format_checkin(self, msg: Message):
        """O método format_checkin escreve o check-in formatado com emojis da maneira estabelecida pelo boost
        
        :Parâmetro msg: Mensagem do telegram que pediu para deletar os dados"""

        #Pega os dados que estão neste relátorio para escrever o relatório
        checkin_atual = self.getDB_a(msg.chat.id)

        #Se não há nada no checkin_atual, não há porque formatar
        if self.is_db_empty(checkin_atual, msg):
            return
        
        #Cria a string que vai ser enviada para o usuário/grupo que requisitou
        titulo = (f'<b>Check-in semanal</b>')
        bullet_char = " • "
        formated= f'{titulo}\n\n'
        formated+= '✅ Progresso dessa semana:\n'
        for tar in checkin_atual['tarefas']:
            formated+= f'{bullet_char}{tar.capitalize()}\n'

        formated+= '\n🚧 Bloqueios / dificuldades:\n'
        for des in checkin_atual['desafios']:
            formated+= f'{bullet_char}{des.capitalize()}\n'

        formated+= '\n💬 Comentários adicionais (opcional):\n'
        for com in checkin_atual['comentarios']:
            formated+= f'{bullet_char}{com.capitalize()}\n'

        envio= self.BOT.send_message(msg.chat.id, formated, parse_mode='HTML')

        #Vamos também reagir à mensagem de formatação com um emoji da lista abaixo
        from random import randint
        from time import sleep
        emojis=['😍', '🔥', '❤', '😁', '💯', '🦄', '🎉', '🤩', '👍']
        emoji_para_reagir = emojis[randint(0,8)]
        sleep(0.5)
        self.BOT.set_message_reaction(envio.chat.id, envio.id, [ReactionTypeEmoji(emoji_para_reagir)])

    def add_checkin(self, msg: Message):
        """O método add_checkin adiciona o que o usuário pedir ao seu check-in semanal, de acordo com a categoria

        :Parâmetro msg: Mensagem do telegram que pediu para adicionar os dados"""

        #Botões e keyboard para cada tipo de coisa que vai no check-in
        btn1_add= InlineKeyboardButton(text="✅ Adicionar tarefa realizada ✅", callback_data= "add_tar")
        btn2_add= InlineKeyboardButton(text="🚧 Adicionar dificuldade/bloqueio 🚧", callback_data= "add_des")
        btn3_add= InlineKeyboardButton(text="💬 Adicionar Comentário opicional 💬", callback_data= "add_com")

        inline_keyboard_add= InlineKeyboardMarkup(row_width=1)
        inline_keyboard_add.add(btn1_add, btn2_add, btn3_add)

        self.BOT.send_message(msg.chat.id, 'O que você quer adicionar ao seu check-in semanal?', reply_markup= inline_keyboard_add)

    def callbacks(self):
        """O método callbacks cuida das ações que ocorrem após um usuário usar um botão dos inline keyboards"""

        #Essa é a callback de adicionar novos items ao check-in, do método self.add_checkin
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('add'))
        def oque_vamos_adicionar(call: CallbackQuery):
            self.BOT.answer_callback_query(call.id)

            mensagens_para_cada_opcao = {
            'add_tar': 'Qual foi a tarefa realizada? \nPara anular, responda "none"',
            'add_des': 'Qual foi a dificuldade encontrada? \nPara anular, responda "none"',
            'add_com': 'Qual comentario a ser adicionado? \nPara anular, responda "none"'
            }

            #Se o botão que o usuário criou está entre as opções acima, no dicionário mensagens_para_cada opcao:
            #Nós enviamos para o método le_Resposta qual botão foi escolhido
            if call.data in mensagens_para_cada_opcao.keys():
                self.BOT.send_message(call.message.chat.id, mensagens_para_cada_opcao[call.data])
                self.BOT.register_next_step_handler(call.message, self.le_Resposta, call.data)


        #Essa é a callback que apaga o check-in atual, caso o usuário confirme, do método self.clear_checkin
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('clear'))
        def temCerteza(call: CallbackQuery):
            if call.data == "clear_sim":
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Pronto! Check-in semanal esvaziado!')

                self.DATABASE.deleta_db_a(call.message.chat.id)

            elif call.data == 'clear_nao':
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Ok! Seu check-in não foi esvaziado!')

            else:
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Erro ao processar o comando /checkin_clear')

    def msg_handlers(self):
        """O método msg_handlers aciona os message handlers para os métodos acima. Também cria o seu próprio 
        message handler que contém o menu de quais comandos estão disponíveis no momento para auxiliar na 
        criação do relatório."""

        @self.BOT.message_handler(commands=['checkin']) 
        def checkin(msg: telebot.types.Message):

            #redirect é a string com o menu de opções de check-in
            redirect= f'<b>O que você deseja realizar?</b>\n\n'
            redirect+=f'➕ Adicionar um novo item ao meu check-in:\n/checkin_add\n\n'
            redirect+=f'🔎 Ver uma prévia simples do que já está no seu check-in:\n/checkin_preview\n\n'
            redirect+=f'✨ Formatar o check-in atual:\n/checkin_format\n\n'
            redirect+=f'🚮 Deletar o check-in atual:\n/checkin_clear\n\n'

            self.BOT.send_message(msg.chat.id, redirect, parse_mode='HTML')

        #Cria um message handler para cada funcionalidade (add, preview, format, clear) 
        self.BOT.message_handler(commands=['checkin_add'])(self.add_checkin)
        self.BOT.message_handler(commands=['checkin_preview'])(self.preview_checkin)
        self.BOT.message_handler(commands=['checkin_format'])(self.format_checkin)
        self.BOT.message_handler(commands=['checkin_clear'])(self.clear_checkin)


    def le_Resposta(self, msg:Message, categoria: str):
        """O método le_resposta é auxiliar do add_checkin, ele envia para a database o que o usuário quer adicionar ao seu check-in
        
        :Parâmetro msg: Mensagem do telegram que pediu para adicionar os dados
        :Parâmetro categoria: String que contém qual tipo de dado que será inserido ('tarefa', 'desafio', 'comentario') """

        resposta= msg.text.lower().strip()

        #Caso de anulação da adição
        if (resposta== 'none'):
            return
        
        resposta= resposta.capitalize()
        if (categoria=='add_tar'):
            self.DATABASE.add_db(msg.from_user.id, msg.chat.id, 'tarefas', resposta)
            self.BOT.send_message(msg.chat.id, f'✅ Tarefa adicionada: <i>{resposta}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML')

        elif (categoria=='add_des'):
            self.DATABASE.add_db(msg.from_user.id, msg.chat.id, 'desafios', resposta)
            self.BOT.send_message(msg.chat.id, f'🚧 Dificuldade adicionada: <i>{resposta}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML')

        elif (categoria=='add_com'):
            self.DATABASE.add_db(msg.from_user.id, msg.chat.id, 'comentarios', resposta)
            self.BOT.send_message(msg.chat.id, f'💬 Comentário adicionado: <i>{resposta}</i>\nDeseja adicionar um novo item? /checkin_add', parse_mode='HTML')

        else:
            self.BOT.send_message(msg.chat.id, f'Erro ao acrescentar: <i>{resposta}</i>\nDeseja tentar adicionar um novo item? /checkin_add', parse_mode='HTML')


    def main(self):
        """O método main é o que aciona os dois métodos que contém os message handlers e as callbacks"""

        #Aciona os message handlers
        self.msg_handlers()

        #Aciona as callbacks
        self.callbacks()

        #Limpa o banco de dados de entradas antigas inutilizadas
        self.DATABASE.manutencao_db()
        


