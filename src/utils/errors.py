import logging
import traceback
import uuid
from typing import Type
from functools import wraps
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, InlineKeyboardMarkup, ReplyParameters, CallbackQuery

from utils.bot_errors import *
from handlers.abstract import msg_handler

logger = logging.getLogger(__name__)

def catch_message_errors(*errors_to_catch: Type[TelebotError]):

    def actual_decorator(func):

        @wraps(func)
        async def wrapper(self: msg_handler, *args, **kwargs):

            msg = None
            all_objects = [self] + list(args) + list(kwargs.values())

            for obj in all_objects:
                if isinstance(obj, Message):
                    msg = obj
                    break

            error_id = str(uuid.uuid4())[:8]

            try:
                result = await func(self, *args, **kwargs)
                return result
            
            except PoorUseOfCommand as E: 
                if msg:
                    await send_error(
                        BOT=self.BOT,
                        msg=msg,
                        error_text=(E.error_tag + E.error_text),
                        edit_msg=E.edit,
                        keyboard=E.keyboard,
                        reply=E.reply,
                    )

                else:
                    logger.critical(f"[ID: {error_id}] Não foi possível encontrar a mensagem para enviar o erro pro usuário!")

            except errors_to_catch as E:
                logger.error(f"[ID: {error_id}] Erro na função {func.__name__}")  
                logger.error(traceback.format_exc())  

                if msg:
                    await send_error(
                        BOT=self.BOT,
                        msg=msg,
                        error_text=(E.error_tag + E.error_text + f"\nCódigo de erro: <code>{error_id}</code>"),
                        edit_msg=E.edit,
                        keyboard=E.keyboard,
                        reply=E.reply,
                    )

                else:
                    logger.critical(f"[ID: {error_id}] Não foi possível encontrar a mensagem para enviar o erro pro usuário!")

            except Exception as E:
                    
                logger.error(f"[ID: {error_id}] Erro crítico na função: {func.__name__}")
                logger.error(traceback.format_exc())

                if msg:

                    error_msg = f"<b>⚠️ ERRO CRÍTICO:</b> Não é possível prosseguir devido a um erro inesperado! \nCódigo de erro: <code>{error_id}</code>"

                    await send_error(
                        BOT=self.BOT,
                        msg=msg,
                        error_text=error_msg
                    )

                else:
                    logger.critical(f"[ID: {error_id}] Não foi possível encontrar a mensagem para enviar o erro pro usuário!")

        return wrapper

    return actual_decorator


def catch_callbackquery_errors(BOT: AsyncTeleBot, *errors_to_catch: Type[TelebotError]):

    def actual_decorator(func):

        @wraps(func)
        async def wrapper(self, *args, **kwargs):

            msg = None
            all_args = [self] + list(args) + list(kwargs)

            for arg in all_args:

                if isinstance(arg, CallbackQuery):
                    msg = arg.message
                    break

                elif isinstance(arg, Message):
                    msg = arg
                    break

            error_id = str(uuid.uuid4())[:8]

            try:
                result = await func(self, *args, **kwargs)
                return result
            
            except PoorUseOfCommand as E: 
                if msg:
                    await send_error(
                        BOT=BOT,
                        msg=msg,
                        error_text=(E.error_tag + E.error_text),
                        edit_msg=E.edit,
                        keyboard=E.keyboard,
                        reply=E.reply,
                    )

                else:
                    logger.critical(f"[ID: {error_id}] Não foi possível encontrar a mensagem para enviar o erro pro usuário!")

            except errors_to_catch as E:
                logger.error(f"[ID: {error_id}] Erro na função {func.__name__}")  
                logger.error(traceback.format_exc())  

                if msg:
                    await send_error(
                        BOT=BOT,
                        msg=msg,
                        error_text=(E.error_tag + E.error_text + f"\nCódigo de erro: <code>{error_id}</code>"),
                        edit_msg=E.edit,
                        keyboard=E.keyboard,
                        reply=E.reply,
                    )

                else:
                    logger.critical(f"[ID: {error_id}] Não foi possível encontrar a mensagem para enviar o erro pro usuário!")

            except Exception as E:
                    
                logger.error(f"[ID: {error_id}] Erro crítico na função: {func.__name__}")
                logger.error(traceback.format_exc())

                if msg:

                    error_msg = f"<b>⚠️ ERRO CRÍTICO:</b> Não é possível prosseguir devido a um erro inesperado! \nCódigo de erro: <code>{error_id}</code>"

                    await send_error(
                        BOT=BOT,
                        msg=msg,
                        error_text=error_msg
                    )

                else:
                    logger.critical(f"[ID: {error_id}] Não foi possível encontrar a mensagem para enviar o erro pro usuário!")
        return wrapper

    return actual_decorator


async def send_error(
    BOT: TeleBot,
    msg: Message,
    error_text: str,
    edit_msg: Message = None,
    keyboard: InlineKeyboardMarkup = None,
    reply: bool = False,
):
    try:
        if edit_msg:
            await BOT.edit_message_text(
                text=error_text,
                message_id=edit_msg.id,
                chat_id=msg.chat.id,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            return

        if reply:
            await BOT.send_message(
                chat_id=msg.chat.id,
                text=error_text,
                parse_mode="HTML",
                message_thread_id=msg.message_thread_id,
                reply_markup=keyboard,
                reply_parameters=ReplyParameters(
                    msg.id, chat_id=msg.chat.id, allow_sending_without_reply=True
                ),
            )
            return

        else:
            await BOT.send_message(
                chat_id=msg.chat.id,
                text=error_text,
                parse_mode="HTML",
                message_thread_id=msg.message_thread_id,
                reply_markup=keyboard,
            )

    except Exception:
        #Erro dessa função, não de algo que o usuário tenha feito!!!
        error_id = str(uuid.uuid4())[:8]
        logger.critical(f"[ID: {error_id}] Não foi possível enviar o erro pro usuário!")
        logger.error(traceback.format_exc())  
        return

