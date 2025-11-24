import telebot
from handlers.abstract import msg_handler
from handlers.errors import catch_message_errors

from github import Github

class git_invite(msg_handler):
    def __init__(self,bot,git_token: str):
        super().__init__(bot)

        self.git_token = git_token
        self.github = Github(git_token)
        self.organizacao = self.github.get_organization("USPCodeLabSanca")
        self.register_callback_handler()
        
    @catch_message_errors() 
    async def __call__(self,msg:telebot.types.Message):
        invite = 'Escreva o e-mail da pessoa que deseja adicionar à organização:'

        await self.BOT.send_message(msg.chat.id, invite, message_thread_id = msg.message_thread_id)