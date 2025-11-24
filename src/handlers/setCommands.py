import telebot
from telebot.types import BotCommand

#Coloque aqui o comando que você adicionou e uma breve descrição dele
COMANDOS = [
    BotCommand('/start', 'Inicia o robô'),
    BotCommand('/codelab', 'Mostra o nome correto do grupo'),
    BotCommand('/feedback', 'Coleta o feedback anônimo do usuário'),
    BotCommand('/fronts',  'Breve descrição das frentes do Codelab'),
    BotCommand('/links', 'Mostra links úteis do Codelab'),
    BotCommand('/suggestion', 'Auxilia a construção de sugestões para o bot'),
    BotCommand('/gitInvite', 'Administradores conseguem adicionar pessoas à organização do GitHub')
]

#AVISO: O PROGRAMA DEMORA UNS MINUTINHOS ANTES DE ATUALIZAR O MENU DE COMANDOS