import telebot
import asyncio
import aiohttp
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import os

from handlers import fronts, setCommands, codelab ,links, feedbacks, suggestions
from handlers.codelab import CodelabHandler
from dependencies.internal import suggestions_db


# Constantes para instanciar o bot
load_dotenv()

TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")
DB = os.getenv("DB")
CODELAB_NAME_LIST = os.getenv("CODELAB_NAME_LIST")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# Função compositora para associar o bot aos handlers desenvolvidos
# Criando esses handlers por injeção de dependências
async def create_bot(TOKEN):
    # instanciando o bot
    bot = AsyncTeleBot(TOKEN)

    # Instanciando as dependências dos bots

    # Injetando as dependências nas features
    codelab_comm = codelab.CodelabHandler(bot, CODELAB_NAME_LIST)
    link = links.show_links(bot)

    front = fronts.ShowFronts(bot)
    feedback = feedbacks.Feedback(bot, TARGET_CHAT_ID)


    # Composição das featrues no bot
    bot.register_message_handler(codelab_comm, commands=['codelab'])

    bot.register_message_handler(link,commands=['links'])
    bot.register_message_handler(front, commands=['fronts'])

    bot.register_message_handler(feedback, commands=['feedback'])

    # Configurando a lista de comandos do bot
    await bot.set_my_commands(setCommands.COMANDOS)

    return bot

async def main():
    # Instanciando um cliente HTTP global
    session = aiohttp.ClientSession()

    # Rodando o bot e tratando erros
    print("> Bot Iniciando...")
    try: 
        bot = await create_bot(TOKEN)
        print("> Bot iniciado com sucesso!")

        # Rodando em loop assíncrono
        await bot.polling(non_stop=True)
    except Exception as e:
        print(f"!> Um erro ocorreu:\n{e}")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
