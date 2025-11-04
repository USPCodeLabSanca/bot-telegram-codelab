import telebot
from telebot.apihelper import ApiTelegramException

# Verifica se o usuário que executa um comando é um administrador
async def isAdmin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    
    # Caso o bot não esteja em um grupo
    except ApiTelegramException as err:
        print(f"Erro ao checar admin: {err}")
        return False
