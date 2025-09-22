import sqlite3
from datetime import datetime, timedelta
import threading
import logging

class Check_in_db():
    def __init__(self, database_path='users.db'):
        """A classe Check_in_db é utilizada para armazenar os dados coletados pelos processos 
        de criação de relatórios semanais. 
        
        :Parametro database_path: string contendo o nome do arquivo em que serão armazenados os processos"""

        # O arquivo onde será salvo os processos
        self.DB = database_path 

        # Manutenção de thread para segurança
        self.local = threading.local()

        #Cria o logger
        self.logger = logging.getLogger(__name__)
        
        # Cria a tabela de dados caso ela não existir
        self.inicia_db()

    def get_conexao(self):
        """O método get_conexao estabelece o contato entre o nosso código e a database
        
        :Return: A conexão estabelecida"""

        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.DB)

        return self.local.connection
    
    def inicia_db(self):
        """O método inicia_db cria a tabela em que os dados serão inseridos"""
        
        #Estabelece a conexão e cria o cursor
        conexao = self.get_conexao() 
        cursor = conexao.cursor() 

        try:
            #Cria a nossa tabela de check-ins
            cursor.execute("""CREATE TABLE IF NOT EXISTS user_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            item TEXT NOT NULL,
            data TEXT NOT NULL DEFAULT (datetime('now')),
            data_mod TEXT NOT NULL DEFAULT (datetime('now'))
            ) """)

            #Cria dois indexes para buscas mais rápidas pelo id
            cursor.execute("""CREATE INDEX IF NOT EXISTS idx_userid_chatid 
                        ON user_checkins(user_id, chat_id)""")
            
            cursor.execute("""CREATE INDEX IF NOT EXISTS idx_chatid 
                        ON user_checkins(chat_id)""")

            #Dá o commit do comando realizado
            conexao.commit()

            #Loga o evento realizado
            self.logger.info('Tabela criada com sucesso!')

            cursor.execute("PRAGMA table_info(user_checkins)")
            colunas= cursor.fetchall()
            self.logger.debug(f'As colunas presentes na tabela são {colunas}')

        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso a criação da tabela
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.critical('Erro ao criar a tabela')
            raise e
        
    def add_db(self, userID: int, chatID: int, cat: str, it: str):
        """O método add_db adiciona à nossa tabela o que o usuário escreveu
        
        :Param userID: int que representa o usuário que adicionou o dado
        :Param chatID: int que representa a conversa que adicionou o dado
        :Param cat: str que representa qual a categoria que será adicionada (tarefa, desafio ou comentario)
        :Param it: str que representa o item a ser adicionado (estudei tal coisa, dificuldade com a biblioteca, ...)

        """

        try:
            #Estabelece a conexão e cria o cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Inserindo na tabela
            cursor.execute("""
                            INSERT INTO user_checkins (user_id, chat_id, categoria, item)
                            VALUES (?, ?, ?, ?)""", (userID, chatID, cat, it,))

            #Dá o commit do comando realizado
            conexao.commit()

            #Loga o evento realizado       
            self.logger.info(f'Item "{it}" adicionado na categoria "{cat}" pelo usuário "{userID}" na conversa "{chatID}"')

            cursor.execute("SELECT MAX(id) FROM user_checkins;")
            ID= cursor.fetchone()[0]
            cursor.execute("SELECT * FROM user_checkins WHERE id = ?", (ID,))
            row= cursor.fetchone()
            self.logger.debug(f'A mais recente adicionada coluna na tabela foi: {row}')     

        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso a adição de um item novo
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.error(f'Erro ao adicionar item "{it}" na categoria "{cat}" pelo usuário "{userID}" na conversa "{chatID}"')
            raise e
  
    def extrai_db_s(self, userID: int, chatID: int):
        #AINDA NÃO ESTÁ EM USO
        """O método extrai_db_s pega os dados que estão na tabela APENAS para aquele usuário que requisitou um preview ou um format, 
        ao invés de pegar todos os dados da conversa
        
        :Param userID: int que representa o usuário que adicionou o dado
        :Param chatID: int que representa a conversa que adicionou o dado
        :Return: dicionário com as informações separadas por categoria | None, caso não houver dados salvos pelo id do usuário
        """

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Pega na tabela o que foi providenciado pelo usuário
            cursor.execute("""
                        SELECT categoria, item FROM user_checkins
                        WHERE user_id = ? AND chat_id = ?
                        ORDER BY data""", (userID, chatID,))
            
            #Guarda as extrações da tabela
            colunas = cursor.fetchall()

            #Atualiza a data de última modificação
            cursor.execute("""UPDATE user_checkins SET data_mod = datetime('now') WHERE user_id = ? AND chat_id = ?""", (userID, chatID,))

            #Dá o commit do comando realizado
            conexao.commit()

            #Coloca os dados num dicionario
            a=0
            checkin={'tarefas':[], 
                    'desafios':[],
                    'comentarios':[]}
            
            for categoria, item in colunas:
                if categoria in checkin.keys():
                    checkin[categoria].append(item)
                    a=1

            # Verifica se há itens para enviar
            if a==0: 
                #Loga o evento ocorrido
                self.logger.info(f'Não há dados salvos pelo usuário "{userID}" na conversa "{chatID}" para enviar')

                return None
            
            else:
                #Loga o evento ocorrido
                self.logger.info(f'Enviando os dados salvos pelo usuário "{userID}" na conversa "{chatID}"')
                self.logger.debug(f'Para o usuário {userID} na conversa {chatID}:\nAs tarefas presentes eram {checkin["tarefas"]}\nOs desafios presentes eram {checkin["desafios"]}\nOs comentarios presentes eram {checkin["comentarios"]}')

                return checkin
            
        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso a busca pelos itens
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.error(f'Erro ao procurar os items adiconados pelo usuário "{userID}" na conversa "{chatID}"')
            raise e
            
    def extrai_db_a(self, chatID: int):
        """O método extrai_db_a pega os dados que estão na tabela para aquela conversa que requisitou um preview ou um format"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Pega na tabela o que foi providenciado pela conversa
            cursor.execute("""
                        SELECT categoria, item FROM user_checkins
                        WHERE chat_id = ?
                        ORDER BY data""", (chatID,))
            
            #Guarda as extrações da tabela
            colunas = cursor.fetchall()

            #Atualiza a data de última modificação
            cursor.execute("""UPDATE user_checkins SET data_mod = datetime('now') WHERE chat_id = ?""", (chatID,))

            #Dá o commit do comando realizado
            conexao.commit()

            #Coloca num dicionario, mais acessível
            a=0
            checkin={'tarefas':[], 
                    'desafios':[],
                    'comentarios':[]}
            
            for categoria, item in colunas:
                if categoria in checkin.keys():
                    checkin[categoria].append(item)
                    a=1

            # Verifica se há itens para enviar
            if a==0: 
                #Loga o evento ocorrido
                self.logger.info(f'Não há dados salvos na conversa "{chatID}" para enviar')

                return None
            
            else:
                #Loga o evento ocorrido
                self.logger.info(f'Enviando os dados salvos na conversa "{chatID}"')
                self.logger.debug(f'Para a conversa {chatID}:\nAs tarefas presentes eram {checkin["tarefas"]}\nOs desafios presentes eram {checkin["desafios"]}\nOs comentarios presentes eram {checkin["comentarios"]}')

                return checkin
            
        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso a busca pelos itens
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.error(f'Erro ao procurar os items adiconados na conversa "{chatID}"')
            raise e
        
    def deleta_db_s(self, userID: int, chatID: int):
        #AINDA NÃO ESTÁ EM USO
        """O método deleta_db_s apaga todas as entradas feitas APENAS pelo usuário naquela conversa
        
        :Param userID: int que representa o usuário que pediu para deletar os dados
        :Param chatID: int que representa a conversa que pediu para deletar os dados
        """

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Deleta todos os items ligados a um usuário da tabela
            cursor.execute("""DELETE FROM user_checkins
                        WHERE user_id = ? AND chat_id = ?""", (userID, chatID,))
            
            #Dá o commit do comando realizado
            conexao.commit()

            #Loga o evento ocorrido
            self.logger.info(f'Itens do usuário "{userID}" na conversa "{chatID}" deletados da database')

        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso deletar os itens
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.error(f'Erro ao deletar os items do usuário {userID} na conversa "{chatID}"')
            raise e
        
    def deleta_db_a(self, chatID: int):
        """O método deleta_db_a apaga todas as entradas feitas naquela conversa
        
        :Param chatID: int que representa a conversa que pediu para deletar os dados"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Deleta todos os items ligados a um usuário da tabela
            cursor.execute("""DELETE FROM user_checkins
                        WHERE chat_id = ?""", (chatID,))
            
            #Dá o commit do comando realizado
            conexao.commit()

            #Loga o evento ocorrido
            self.logger.info(f'Itens da conversa "{chatID}" deletados da database')

        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso deletar os itens
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.error(f'Erro ao deletar os items da conversa "{chatID}"')
            raise e
        
    def manutencao_db(self, tempo: int = 60):
        """O método manutenção_db é feito pra apagar dados antigos inutilizados
        
        :Param tempo: int que representa o numero de dias de tolerância para guardar os dados inutilizados"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor()

            #Estabele a data limite para manter um dado na tabela
            data_lim = (datetime.now() - timedelta(days=tempo)).strftime('%Y-%m-%d %H:%M:%S') 

            #Deleta todos os items que estão na lista há muito tempo sem serem "modificados"
            cursor.execute("""DELETE FROM user_checkins
                        WHERE data_mod < ? """, (data_lim,))
            
            #Dá o commit do comando realizado
            conexao.commit()

            #Loga o evento ocorrido
            self.logger.info('Exclusão de dados antigos realizada')

        except sqlite3.Error as e:
            if conexao:
                #Anula a última ação feita pelo código, no caso deletar os itens antigos
                conexao.rollback() 

            # Loga o erro ocorrido 
            self.logger.error(f'Erro ao deletar os items antigos"')
            raise e
        

#DEBUG PLACE
if __name__== '__main__':
    testingDB= Check_in_db('test.db')

    logger= logging.basicConfig(
        format= "%(asctime)s [%(levelname)s] line:%(lineno)d - %(message)s",
        level= logging.DEBUG,
        filename='test.log' 
    )

    testingDB.add_db(11, 12, 'tarefas', 'Fiz tal coisa')
    testingDB.add_db(11, 12, 'tarefas', 'Fiz outra coisa')


    testingDB.add_db(11, 13, 'desafios', 'Tal biblioteca')
    testingDB.add_db(11, 13, 'desafios', 'Tal função')
    testingDB.add_db(11, 13, 'comentarios', 'Fiz mais uma coisa')

    a= testingDB.extrai_db_a(12)
    b= testingDB.extrai_db_a(13)
    c= testingDB.extrai_db_a(14)


    testingDB.deleta_db_a(12)
    testingDB.deleta_db_a(13)

    a= testingDB.extrai_db_a(12)
    b= testingDB.extrai_db_a(13)