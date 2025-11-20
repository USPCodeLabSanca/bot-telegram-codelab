from typing import Type
from functools import wraps
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, ReplyParameters, CallbackQuery

from dependencies.internal.bot_errors import *
from handlers.abstract import msg_handler


def catch_message_errors(*errors_to_catch: Type[TelebotError]):

    def actual_decorator(func):

        @wraps(func)
        async def wrapper(self: msg_handler, *args, **kwargs):

            msg = None
            all_args = list(args) + list(kwargs)

            for arg in all_args:

                if isinstance(arg, Message):
                    msg = arg
                    break

            if msg == None:
                try:
                    result = await func(self, *args, **kwargs)
                    return result

                except Exception as E:
                    print("======================================================================================")
                    print(f"Erro crítico, não foi possível definir a mensagem do usuário para enviarmos erro!")
                    print(f"Exception: {E}")
                    print(f"Class: {self.__class__.__name__}")
                    print(f"Function: {func.__name__}")
                    print("======================================================================================")

                    raise E

            else:
                try:
                    result = await func(self, *args, **kwargs)
                    return result

                except errors_to_catch as E:
                    print("======================================================================================")
                    print(f"Houve um erro!")
                    print(f"Exception: {E}")
                    print(f"Class: {self.__class__.__name__}")
                    print(f"Function: {func.__name__}")
                    print("======================================================================================")
                    await send_error(
                        BOT=self.BOT,
                        msg=msg,
                        error_text=(E.error_tag + E.error_text),
                        edit_msg=E.edit,
                        keyboard=E.keyboard,
                        reply=E.reply,
                    )

                except Exception as E:
                    error_msg = f"<b>⚠️ ERRO:</b> Execução interrompida devido a um erro inesperado!"
                    print("======================================================================================")
                    print(f"Houve um erro!")
                    print(f"Exception: {E}")
                    print(f"Class: {self.__class__.__name__}")
                    print(f"Function: {func.__name__}")
                    print("======================================================================================")

                    await send_error(
                        BOT=self.BOT,
                        msg=msg,
                        error_text=(error_msg),
                    )

        return wrapper

    return actual_decorator


def catch_callbackquery_errors(BOT: TeleBot, *errors_to_catch: Type[TelebotError]):

    def actual_decorator(func):

        @wraps(func)
        async def wrapper(self, *args, **kwargs):

            msg = None
            all_args = [self] + list(args) + list(kwargs)

            for arg in all_args:

                if isinstance(arg, CallbackQuery):
                    msg = arg.message
                    break

            if msg == None:
                try:
                    result = await func(self, *args, **kwargs)
                    return result

                except Exception as E:
                    print("======================================================================================")
                    print(f"Erro crítico, não foi possível definir a mensagem do usuário para enviarmos erro!")
                    print(f"Exception: {E}")
                    print(f"Class: {self.__class__.__name__}")
                    print(f"Function: {func.__name__}")
                    print("======================================================================================")
                    raise E

            else:
                try:
                    result = await func(self, *args, **kwargs)
                    return result

                except errors_to_catch as E:
                    print("======================================================================================")
                    print(f"Houve um erro!")
                    print(f"Exception: {E}")
                    print(f"Class: {self.__class__.__name__}")
                    print(f"Function: {func.__name__}")
                    print("======================================================================================")
                    await send_error(
                        BOT=BOT,
                        msg=msg,
                        error_text=(E.error_tag + E.error_text),
                        edit_msg=E.edit,
                        keyboard=E.keyboard,
                        reply=E.reply,
                    )

                except Exception as E:
                    error_msg = f"<b>⚠️ ERRO:</b> Execução interrompida devido a um erro inesperado!"
                    
                    print("======================================================================================")
                    print(f"Houve um erro!")
                    print(f"Exception: {E}")
                    print(f"Class: {self.__class__.__name__}")
                    print(f"Function: {func.__name__}")
                    print("======================================================================================")

                    await send_error(BOT=BOT, msg=msg, error_text=error_msg, edit_msg=msg)

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
        return

