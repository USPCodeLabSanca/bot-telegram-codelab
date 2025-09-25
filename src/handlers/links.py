import telebot

def show_links(bot):
    @bot.message_handler(commands=["links"])
    def start(msg: telebot.types.Message):
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

        bot.send_message(msg.chat.id, links)