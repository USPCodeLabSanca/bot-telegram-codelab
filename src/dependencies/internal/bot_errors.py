from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup


class TelebotError(Exception):
    def __init__(
        self,
        error_text: str = None,
        error_tag: str = "<b>⚠️ ERRO:</b> ",
        edit_msg: Message = None,
        keyboard: InlineKeyboardMarkup = None,
        reply: bool = False,
    ):
        self.error_text = error_text
        self.edit = edit_msg
        self.keyboard = keyboard
        self.reply = reply
        self.error_tag = error_tag


class PoorUseOfCommand(TelebotError):
    def __init__(
        self,
        error_text:str,
        error_tag:str = "<b>⚠️ ERRO:</b> ",
        edit_msg: Message = None,
        keyboard: InlineKeyboardMarkup = None,
        reply: bool = False,
    ):
        super().__init__(error_text, error_tag, edit_msg, keyboard, reply)


class ServerError(TelebotError):
    def __init__(
        self,
        error_text: str = "Não foi possível estabelecer conexão com o servidor!",
        error_tag:str = "<b>⚠️ ERRO:</b> ",
        edit_msg: Message = None,
        keyboard: InlineKeyboardMarkup = None,
        reply: bool = False,
    ):
        super().__init__(error_text, error_tag, edit_msg, keyboard, reply)


class DBError(TelebotError):
    def __init__(
        self,
        error_text="Não foi possível estabelecer conexão com a database!",
        error_tag:str = "<b>⚠️ ERRO:</b> ",
        edit_msg: Message = None,
        keyboard: InlineKeyboardMarkup = None,
        reply: bool = False,
    ):
        super().__init__(error_text, error_tag, edit_msg, keyboard, reply)


class ExecutionError(TelebotError):
    def __init__(
        self,
        error_text="Execução interrompida devido a um erro inesperado!",
        error_tag:str = "<b>⚠️ ERRO:</b> ",
        edit_msg: Message = None,
        keyboard: InlineKeyboardMarkup = None,
        reply: bool = False,
    ):
        super().__init__(error_text, error_tag, edit_msg, keyboard, reply)