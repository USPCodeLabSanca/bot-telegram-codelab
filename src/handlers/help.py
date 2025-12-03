from handlers.abstract import msg_handler
from utils.errors import catch_message_errors
from telebot.types import ReactionTypeEmoji, Message
from random import choice

class Help(msg_handler):
    def __init__(self, BOT):
        super().__init__(BOT)

    @catch_message_errors()
    async def __call__(self, msg: Message):

        help_message = f"Aqui está uma lista dos comandos que você pode utilizar: \n\n"
        help_message += f"  ● /codelab - Descubra de uma vez por todas qual é o nome correto do Codxlabes!\n"
        help_message += f"  ● /feedback - Envie um feedback anônimo (seja críticas, elogios, ideias) diretamente para os coordenadores!\n"
        help_message += f"  ● /fronts - Veja uma descrição do escopo de cada uma das frentes do Codelab!\n"
        help_message += f"  ● /help - Conheça as minhas funcionalidades!\n"
        help_message += f"  ● /links - Confira uma lista de links úteis do Codelab!\n"
        help_message += f"  ● /start - Comece a interagir comigo!\n"
        help_message += f"  ● /suggestion_add - Envie uma sugestão de melhoria para mim!\n"
        help_message += f"  ● /suggestion_guide - Confira o guia instrucional de como elaborar uma sugestão de melhoria para mim!\n"
        help_message += f"  ● /suggestion_list - Veja quais são as sugestões pendentes de melhoria para mim!\n"
        help_message += f"  ● /gitInvite - Caso for administrador, adicione um membro à organização CodeLab no GitHub! (Adicione o email após o comando. Ex: /gitInvite/exemplo@email.com)"

        await self.BOT.send_message(
            chat_id=msg.chat.id,
            text=help_message,
            message_thread_id=msg.message_thread_id
        )