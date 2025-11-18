import asyncio
import aiohttp
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import os

<<<<<<< HEAD
from handlers import fronts, checkin, codelab ,links
from handlers.codelab import CodelabHandler
from dependencies.internal import dados_checkin
from utils import setCommands
=======
from handlers import fronts, setCommands, codelab ,links, feedbacks, suggestions
from handlers.codelab import CodelabHandler
from dependencies.internal import suggestions_db
>>>>>>> e6388c8d6793f84f9b4c55402507d5e4124a40df


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

<<<<<<< HEAD
    # Instanciando as dependências do bot
    checkin_DB = dados_checkin.Check_in_db(database_path=DB)
=======
    # Instanciando as dependências dos bots
    suggestionsDB = await suggestions_db.SuggestionsDB.create(database_path = DB)
>>>>>>> e6388c8d6793f84f9b4c55402507d5e4124a40df

    # Injetando as dependências nas features
    bugged_command = suggestions.BuggedCommand(bot)
    codelab_comm = codelab.CodelabHandler(bot, CODELAB_NAME_LIST)
    feedback = feedbacks.Feedback(bot, TARGET_CHAT_ID)
    front = fronts.ShowFronts(bot)
    link = links.show_links(bot)
<<<<<<< HEAD
    fronts_handler = fronts.ShowFronts(bot)

    checkin_main = checkin.main_checkin(bot, DATABASE=checkin_DB)
    checkin_add = checkin.add_checkin(bot, DATABASE=checkin_DB)
    checkin_clear= checkin.clear_checkin(bot, DATABASE=checkin_DB)
    checkin_format= checkin.format_checkin(bot, DATABASE=checkin_DB)
    checkin_preview = checkin.preview_checkin(bot, DATABASE=checkin_DB)


    # Composição das featrues no bot
=======
    suggestions_add = suggestions.SuggestionAdd(bot, suggestionsDB, GIT_LINK_ISSUES, GIT_API_ISSUE_ENDPOINT, GIT_TOKEN, session)
    suggestion_guide = suggestions.SuggestionHelper(bot, SUGGESTION_EXAMPLES)
    suggestions_list = suggestions.SuggestionList(bot, suggestionsDB, GIT_LINK_ISSUES)
    suggestion_main = suggestions.SuggestionMain(bot)

    # Composição das features no bot
    bot.register_message_handler(bugged_command, commands=['bugged_command'])
>>>>>>> e6388c8d6793f84f9b4c55402507d5e4124a40df
    bot.register_message_handler(codelab_comm, commands=['codelab'])
    bot.register_message_handler(feedback, commands=['feedback'])
    bot.register_message_handler(front, commands=['fronts'])
    bot.register_message_handler(link,commands=['links'])
<<<<<<< HEAD
    bot.register_message_handler(fronts_handler, commands=['fronts'])
    bot.register_message_handler(checkin_main, commands=['checkin'])
    bot.register_message_handler(checkin_add, commands=['checkin_add'])
    bot.register_message_handler(checkin_clear, commands=['checkin_clear'])
    bot.register_message_handler(checkin_preview, commands=['checkin_preview'])
    bot.register_message_handler(checkin_format, commands=['checkin_format'])
=======
    bot.register_message_handler(suggestion_main, commands=['suggestion'])
    bot.register_message_handler(suggestions_add, commands=['suggestion_add'])
    bot.register_message_handler(suggestion_guide, commands=['suggestion_guide'])
    bot.register_message_handler(suggestions_list, commands=['suggestion_list'])
>>>>>>> e6388c8d6793f84f9b4c55402507d5e4124a40df

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
