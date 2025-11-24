from telebot.apihelper import ApiTelegramException


# Função auxiliar para verificar se o usuário é admin ou não
async def isAdmin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")

    # Caso o bot não esteja em um grupo
    except ApiTelegramException as err:
        print(f"Erro ao checar admin: {err}")
        return False


# Decorator para a verificação de admin
def admin_only(func):
    async def wrapper(self, message, *args, **kwargs):
        chat_id = message.chat.id
        user_id = message.from_user.id
        topic_id = message.message_thread_id

        if await isAdmin(self.BOT, chat_id, user_id):
            return await func(message, *args, **kwargs)
        else:
            await self.BOT.send_message(
                chat_id,
                "Só admins podem executar este comando",
                message_thread_id=topic_id,
            )

    return wrapper
