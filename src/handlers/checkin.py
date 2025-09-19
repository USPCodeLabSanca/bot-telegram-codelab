import telebot
from telebot import formatting
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

class Check_in:
    def __init__(self, nossoBot):
        self.current_checkin= {
            #Em cada uma dessas listas fica o que o usuário quis adicionar em seu check-in semanal
            'tarefas':[],
            'desafios': [],
            'comentarios': []
        }
        self.BOT= nossoBot #Telebot com o token
        self.current_checkin_empty=True #Inicialmente, você não tem nada no seu check-in

        #método que contém todos os handlers de comando/ativa as callbacks
        self.main() 

    def preview_checkin(self, msg):
        """O método preview_checkin permite que o usuário veja uma prévia de como está o seu check in antes de enviar o formatado """

        #se não há nada no check-in, não há porque mostrar uma prévia
        if self.current_checkin_empty:
            self.BOT.send_message(msg.chat.id,'Não há nada no seu check-in semanal no momento :( ')
            return

        else:
            #o preview é uma string simples com as informações que já estão no check-in
            preview= f'Tarefas realizadas:\n'
            for t in self.current_checkin['tarefas']:
                preview+= f'    -{t}\n'

            preview+= f'\nDesafios encontrados:\n'
            for d in self.current_checkin['desafios']:
                preview+= f'    -{d}\n'
        
            preview+= f'\nComentários adicionais:\n'
            for c in self.current_checkin['comentarios']:
                preview+= f'    -{c}\n'

            self.BOT.send_message(msg.chat.id, preview)

    def clear_checkin(self, msg):
        """O método clear_checkin remove tudo o que havia sido adicionado antes pelo usuário"""

        #se não há nada no check-in, não há porque limpar a lista
        if self.current_checkin_empty:
            self.BOT.send_message(msg.chat.id,'Não há nada no seu check-in semanal no momento :( ')
            return
        
        else:
            #Teclado para perguntar/confirmar se o usário queria mesmo apagar todo o checkin
            btn1_clear= InlineKeyboardButton(text="SIM", callback_data= "clear_sim")
            btn2_clear= InlineKeyboardButton(text="NÃO", callback_data= "clear_nao")
            inline_keyboard_clear= InlineKeyboardMarkup(row_width=2)
            inline_keyboard_clear.add(btn1_clear, btn2_clear)

            self.BOT.send_message(msg.chat.id,'WARNING: Tem certeza que você deseja apagar o seu check-in atual?\nEssa ação não pode ser desfeita!', reply_markup= inline_keyboard_clear)

    def format_checkin(self, msg):
        """O método format_checkin escreve o check-in formatado com emojis da maneira estabelecida pelo boost"""

        if self.current_checkin_empty:
            self.BOT.send_message(msg.chat.id,'Não há nada no seu check-in semanal no momento :( ')
            return
        
        titulo = formatting.hbold("Check-in semanal")
        bullet_char = " • "
        formated= f'{titulo}\n\n'
        formated+= '✅ Progresso dessa semana:\n'
        for tar in self.current_checkin['tarefas']:
            formated+= f'{bullet_char}{tar.capitalize()}\n'

        formated+= '\n🚧 Bloqueios / dificuldades:\n'
        for des in self.current_checkin['desafios']:
            formated+= f'{bullet_char}{des.capitalize()}\n'

        formated+= '\n💬 Comentários adicionais (opcional):\n'
        for com in self.current_checkin['comentarios']:
            formated+= f'{bullet_char}{com.capitalize()}\n'

        self.BOT.send_message(msg.chat.id, formated, parse_mode='HTML')

    def add_checkin(self, msg):
        """O método add_checkin adiciona o que o usuário quiser ao seu check-in semanal"""

        #botões e key board para cada tipo de coisa que vai no check-in
        btn1_add= InlineKeyboardButton(text="✅ Adicionar tarefa realizada ✅", callback_data= "add_tar")
        btn2_add= InlineKeyboardButton(text="🚧 Adicionar dificuldade/bloqueio 🚧", callback_data= "add_des")
        btn3_add= InlineKeyboardButton(text="💬 Adicionar Comentário opicional 💬", callback_data= "add_com")

        inline_keyboard_add= InlineKeyboardMarkup(row_width=1)
        inline_keyboard_add.add(btn1_add, btn2_add, btn3_add)

        inicial= f'O que você quer adicionar ao seu check-in semanal?'
        self.BOT.send_message(msg.chat.id, inicial, reply_markup= inline_keyboard_add)

    def le_Resposta(self, msg, categoria):
        """O método le_resposta é auxiliar do add_checkin, ele guarda o que o usuário quer adicionar ao seu check-in"""

        resposta= msg.text.lower().strip()
        if (resposta== 'none'):
            return
        
        resposta= resposta.capitalize()
        if (categoria=='add_tar'):
            self.current_checkin['tarefas'].append(resposta)
            self.BOT.send_message(msg.chat.id, f'✅ Tarefa adicionada: {resposta}\nDeseja adicionar um novo item? /checkin_add')

        elif (categoria=='add_des'):
            self.current_checkin['desafios'].append(resposta)
            self.BOT.send_message(msg.chat.id, f'🚧 Dificuldade adicionada: {resposta}\nDeseja adicionar um novo item? /checkin_add')

        elif (categoria=='add_com'):
            self.current_checkin['comentarios'].append(resposta)
            self.BOT.send_message(msg.chat.id, f'💬 Comentário adicionado: {resposta}\nDeseja adicionar um novo item? /checkin_add')

        self.current_checkin_empty=False

    def callbacks(self):
        """O método callbacks cuida das ações que ocorrem após um usuário usar um botão dos inline keyboards"""

        #Essa é a callback de adicionar novos items ao check-in, do método self.add_checkin
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('add'))
        def oque_vamos_adicionar(call):
            self.BOT.answer_callback_query(call.id)

            mensagens_para_cada_opção = {
            'add_tar': 'Qual foi a tarefa realizada? \nPara anular, responda "none"',
            'add_des': 'Qual foi a dificuldade encontrada? \nPara anular, responda "none"',
            'add_com': 'Qual comentario a ser adicionado? \nPara anular, responda "none"'
            }

            #Se o botão que o usuário criou está entre as opções acima, no dicionário mensagens_para_cada opção:
            #Nós enviamos para o método le_Resposta qual foi o botão escolhido
            if call.data in mensagens_para_cada_opção.keys():
                self.BOT.send_message(call.message.chat.id, mensagens_para_cada_opção[call.data])
                self.BOT.register_next_step_handler(call.message, self.le_Resposta, call.data)


        #Essa é a callback que apaga o check-in atual, caso o usuário confirme, do método self.clear_checkin
        @self.BOT.callback_query_handler(func= lambda call: call.data.startswith('clear'))
        def temCerteza(call):
            if call.data == "clear_sim":
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Pronto! Check-in semanal esvaziado!')

                for categoria in self.current_checkin.values():
                    categoria.clear()

                self.current_checkin_empty=True

            elif call.data == 'clear_nao':
                self.BOT.answer_callback_query(call.id)
                self.BOT.send_message(call.message.chat.id,'Ok! Seu check-in não foi esvaziado!')

    def main(self):
        """O método main é o que aciona os message handlers para os métodos acima e as callbacks. 
        Também mostra um menu de opções para o usuário de quais comandos estão disponíveis."""

        @self.BOT.message_handler(commands=['checkin']) 
        def checkin(msg: telebot.types.Message):

            #redirect é a string com o menu de opções de check-in
            redirect= f'<b>O que você deseja realizar?</b>\n\n'
            redirect+=f'➕ Adicionar um novo item ao meu check-in:\n /checkin_add\n\n'
            redirect+=f'🔎 Ver uma prévia simples do que já está no seu check-in:\n /checkin_preview\n\n'
            redirect+=f'✨ Formatar o check-in atual:\n /checkin_format\n\n'
            redirect+=f'🚮 Deletar o check-in atual:\n /checkin_clear\n\n'

            self.BOT.send_message(msg.chat.id, redirect, parse_mode='HTML')

        self.BOT.message_handler(commands=['checkin_add'])(self.add_checkin)
        self.BOT.message_handler(commands=['checkin_preview'])(self.preview_checkin)
        self.BOT.message_handler(commands=['checkin_format'])(self.format_checkin)
        self.BOT.message_handler(commands=['checkin_clear'])(self.clear_checkin)

        self.callbacks()
