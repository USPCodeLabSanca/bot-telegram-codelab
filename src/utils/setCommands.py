import telebot
from telebot.types import BotCommand

#Coloque aqui o comando que você adicionou e uma breve descrição dele
COMANDOS = [
    BotCommand('/start', 'Inicia o robô'),
<<<<<<< HEAD:src/utils/setCommands.py
    BotCommand('/checkin', 'Auxilia a criação do check-in semanal'),
    BotCommand('/fronts',  'Breve descrição das frentes do Codelab'),
=======
>>>>>>> e6388c8d6793f84f9b4c55402507d5e4124a40df:src/handlers/setCommands.py
    BotCommand('/codelab', 'Mostra o nome correto do grupo'),
    BotCommand('/feedback', 'Coleta o feedback anônimo do usuário'),
    BotCommand('/fronts',  'Breve descrição das frentes do Codelab'),
    BotCommand('/links', 'Mostra links úteis do Codelab'),
    BotCommand('/suggestion', 'Auxilia a construção de sugestões para o bot')
]

#AVISO: O PROGRAMA DEMORA UNS MINUTINHOS ANTES DE ATUALIZAR O MENU DE COMANDOS