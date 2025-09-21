import sqlite3
from datetime import datetime, timedelta
import threading

class Check_in_db():
    def __init__(self, database_path='users.db'):
        self.db = database_path
        self.local = threading.local()

        self.inicia_db()

    def get_conexao(self):
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db)
        return self.local.connection
        

    def inicia_db(self):
        """O método inicia_db cria a tabela em que os dados que os usuários querem adicionar 
            ao seu check-in semanal serão inseridos de acordo com o user_id de cada um"""
        
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

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e

    def add_db(self, userID, chatID, cat, it):
        """O método add_db adiciona à nossa tabela o que o usuário escreveu"""

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

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e

    def extrai_db_s(self, userID, chatID):
        """O método extrai_db_s pega os dados que estão na tabela para aquele usuário que requisitou um preview ou um format"""

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

            #Coloca num dicionario, mais acessível
            a=0
            checkin={'tarefas':[], 
                    'desafios':[],
                    'comentarios':[]}
            
            for categoria, item in colunas:
                if categoria in checkin.keys():
                    checkin[categoria].append(item)
                    a=1

            if a==0:
                return None
            
            else:
                return checkin
        
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e
        
    def extrai_db_a(self, chatID):
        """O método extrai_db_a pega os dados que estão na tabela para aquele usuário que requisitou um preview ou um format"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Pega na tabela o que foi providenciado pelo usuário
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

            if a==0:
                return None
            
            else:
                return checkin
        
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e
         
    def deleta_db_s(self, userID, chatID):
        """O método deleta_db_s apaga todas as entradas feitas pelo usuário"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Deleta todos os items ligados a um usuário da tabela
            cursor.execute("""DELETE FROM user_checkins
                        WHERE user_id = ? AND chat_id = ?""", (userID, chatID,))
            
            #Dá o commit do comando realizado
            conexao.commit()

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e
        
    def deleta_db_a(self,chatID):
        """O método deleta_db_a apaga todas as entradas feitas pelo usuário"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Deleta todos os items ligados a um usuário da tabela
            cursor.execute("""DELETE FROM user_checkins
                        WHERE chat_id = ?""", (chatID,))
            
            #Dá o commit do comando realizado
            conexao.commit()

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e
        
    def manutencao_db(self, tempo=60):
        """O método manutenção_db é feito pra apagar dados antigos inutilizados"""

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

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e