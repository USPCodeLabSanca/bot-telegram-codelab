import telebot

from handlers.abstract import msg_handler
from utils.isAdmin import admin_only


class show_links(msg_handler):
    def __init__(self, bot):
        super().__init__(bot)

    @admin_only
    async def __call__(self, msg: telebot.types.Message):
        links = """
        🧪Aqui estão alguns links úteis do CodeLab🧪:
         - 😺 Github: https://github.com/USPCodeLabSanca

         - 💻 Notion Dev-Boost (apenas membros do notion Codelab):
         https://www.notion.so/Dev-Boost-a93325cc05ca43059773d0e6850d6037

         - 📚 Notion Dev-Learn (apenas membros do notion Codelab):
         https://www.notion.so/Dev-Learn-b9a3cb1804f748c1bfc91ce2c9519dea

         - 🎉 Notion Dev-Hack (apenas membros do notion Codelab): https://www.notion.so/Dev-Hack-1c63571b691a4c55955d872e2245e5f4

         - 🍽 Notion Dev-Clara(apenas membros do notion Codelab): https://www.notion.so/Dev-Clara-1df8def36c1680c1bc6ce1145c5a3026

         - 📷 Instagram: https://www.instagram.com/uspcodelabsanca/

         - 🌐 Site: https://codelab.icmc.usp.br/
        """

        await self.BOT.send_message(
            msg.chat.id, links, message_thread_id=msg.message_thread_id
        )
