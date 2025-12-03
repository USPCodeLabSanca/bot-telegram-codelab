import telebot
from handlers.abstract import msg_handler

from utils.isAdmin import admin_only

import aiohttp

class git_invite(msg_handler):
    def __init__(self,bot,git_token: str, git_api: str, session: aiohttp.ClientSession):
        super().__init__(bot)

        self.git_token = git_token
        self.git_api = git_api
        self.session = session
    
    async def __call__(self,msg:telebot.types.Message):

        email_com_barra = msg.text.split("/gitInvite", 1)[1]
        if not email_com_barra:
            await self.BOT.send_message(msg.chat.id,"Adicione um e-mail! Ex: /gitInvite/exemplo@email.com",message_thread_id = msg.message_thread_id)
            return
        email = email_com_barra.split("/", 1)[1]
        print(email)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.git_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        json_data = {
            "email": email
        }
        response = await self.session.post(self.git_api, headers = headers, json = json_data)
        data = await response.json()
        print(data)
        response.raise_for_status()
        await self.BOT.send_message(msg.chat.id,"Membro Adicionado!",message_thread_id = msg.message_thread_id)

