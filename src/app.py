import telebot
import asyncio
import aiohttp
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import os

from handlers import fronts, checkin, setCommands, codelab ,links
from handlers.codelab import CodelabHandler
from dependencies.internal import dados_checkin


# Constantes para instanciar o bot
load_dotenv()

TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")
DB = os.getenv("DB")
CODELAB_NAME_LIST = os.getenv("CODELAB_NAME_LIST")

# Função compositora para associar o bot aos handlers desenvolvidos
# Criando esses handlers por injeção de dependências
async def create_bot(TOKEN):
    # instanciando o bot
    bot = AsyncTeleBot(TOKEN)

    # Instanciando as dependências dos bots
    checkin_DB = dados_checkin.Check_in_db(database_path=DB)

    # Injetando as dependências nas features
    codelab_comm = codelab.CodelabHandler(bot, CODELAB_NAME_LIST)
    link = links.show_links(bot)

    checkin_main = checkin.main_checkin(bot, DATABASE=checkin_DB)
    checkin_add = checkin.add_checkin(bot, DATABASE=checkin_DB)
    checkin_clear= checkin.clear_checkin(bot, DATABASE=checkin_DB)
    checkin_format= checkin.format_checkin(bot, DATABASE=checkin_DB)
    checkin_preview = checkin.preview_checkin(bot, DATABASE=checkin_DB)

    fronts_handler = fronts.ShowFronts(bot)


    # Composição das featrues no bot
    bot.register_message_handler(codelab_comm, commands=['codelab'])

    bot.register_message_handler(link,commands=['links'])
    bot.register_message_handler(fronts_handler, commands=['fronts'])
    bot.register_message_handler(checkin_main, commands=['checkin'])
    bot.register_message_handler(checkin_add, commands=['checkin_add'])
    bot.register_message_handler(checkin_clear, commands=['checkin_clear'])
    bot.register_message_handler(checkin_preview, commands=['checkin_preview'])
    bot.register_message_handler(checkin_format, commands=['checkin_format'])

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
