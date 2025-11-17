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
GIT_LINK_ISSUES = os.getenv("GIT_LINK_ISSUES")
GIT_API_ISSUE_ENDPOINT = os.getenv("GIT_API_ISSUE_ENDPOINT")
GIT_TOKEN = os.getenv("GIT_TOKEN")
CODELAB_NAME_LIST = os.getenv("CODELAB_NAME_LIST")
SUGGESTION_EXAMPLES = os.getenv("SUGGESTION_EXAMPLES")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# Função compositora para associar o bot aos handlers desenvolvidos
# Criando esses handlers por injeção de dependências
async def create_bot(TOKEN, session):
    # instanciando o bot
    bot = AsyncTeleBot(TOKEN)

    # Instanciando as dependências dos bots
    suggestionsDB = await suggestions_db.SuggestionsDB.create(database_path = DB)

    # Injetando as dependências nas features
    bugged_command = suggestions.BuggedCommand(bot)
    codelab_comm = codelab.CodelabHandler(bot, CODELAB_NAME_LIST)
    feedback = feedbacks.Feedback(bot, TARGET_CHAT_ID)
    front = fronts.ShowFronts(bot)
    link = links.show_links(bot)
    suggestions_add = suggestions.SuggestionAdd(bot, suggestionsDB, GIT_LINK_ISSUES, GIT_API_ISSUE_ENDPOINT, GIT_TOKEN, session)
    suggestion_guide = suggestions.SuggestionHelper(bot, SUGGESTION_EXAMPLES)
    suggestions_list = suggestions.SuggestionList(bot, suggestionsDB, GIT_LINK_ISSUES)
    suggestion_main = suggestions.SuggestionMain(bot)

    # Composição das features no bot
    bot.register_message_handler(bugged_command, commands=['bugged_command'])
    bot.register_message_handler(codelab_comm, commands=['codelab'])
    bot.register_message_handler(feedback, commands=['feedback'])
    bot.register_message_handler(front, commands=['fronts'])
    bot.register_message_handler(link,commands=['links'])
    bot.register_message_handler(suggestion_main, commands=['suggestion'])
    bot.register_message_handler(suggestions_add, commands=['suggestion_add'])
    bot.register_message_handler(suggestion_guide, commands=['suggestion_guide'])
    bot.register_message_handler(suggestions_list, commands=['suggestion_list'])

    # Configurando a lista de comandos do bot
    await bot.set_my_commands(setCommands.COMANDOS)

    return bot

async def main():
    # Instanciando um cliente HTTP global
    session = aiohttp.ClientSession()

    # Rodando o bot e tratando erros
    print("> Bot Iniciando...")
    try: 
        bot = await create_bot(TOKEN, session)
        print("> Bot iniciado com sucesso!")

        # Rodando em loop assíncrono
        await bot.polling(non_stop=True)
    except Exception as e:
        print(f"!> Um erro ocorreu:\n{e}")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
