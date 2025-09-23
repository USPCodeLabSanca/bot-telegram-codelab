import telebot
from telebot.types import BotCommand

#Coloque aqui o comando que você adicionou e uma breve descrição dele
COMANDOS = [
    BotCommand('/start', 'Inicia o robô'),
    BotCommand('/checkin', 'Auxilia a criação do check-in semanal'),
    BotCommand('/fronts',  'Breve descrição das frentes do Codelab'),
    BotCommand('/codelab', 'Mostra o nome correto do grupo')
]

#AVISO: O PROGRAMA DEMORA UNS MINUTINHOS ANTES DE ATUALIZAR O MENU DE COMANDOS