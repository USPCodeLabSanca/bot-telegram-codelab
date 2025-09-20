import sqlite3
from datetime import datetime, timedelta
import threading

class Check_in_db():
    def __init__(self, database_path='users.db'):
        self.db = database_path
        self.local = threading.local()

        self.inicia_db()

    def get_conexao(self):
        """O método get_conexão cria a conexão entre o código e a database"""
        
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
            categoria TEXT NOT NULL,
            item TEXT NOT NULL,
            data TEXT NOT NULL DEFAULT (datetime('now')),
            data_mod TEXT NOT NULL DEFAULT (datetime('now'))
            ) """)

            #Cria um index para buscas mais rápidas pelo id
            cursor.execute("""CREATE INDEX IF NOT EXISTS idx_user_id 
                        ON user_checkins(user_id)""")

            #Dá o commit do comando realizado
            conexao.commit()

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e

    def add_db(self, userID, cat, it):
        """O método add_db adiciona à nossa tabela o que o usuário escreveu"""

        try:
            #Estabelece a conexão e cria o cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Inserindo na tabela
            cursor.execute("""
                            INSERT INTO user_checkins (user_id, categoria, item)
                            VALUES (?, ?, ?)""", (userID, cat, it,))

            #Dá o commit do comando realizado
            conexao.commit()

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            raise e

    def extrai_db(self, userID):
        """O método extrai_db pega os dados que estão na tabela para aquele usuário que requisitou um preview ou um format"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Pega na tabela o que foi providenciado pelo usuário
            cursor.execute("""
                        SELECT categoria, item FROM user_checkins
                        WHERE user_id = ? 
                        ORDER BY data""", (userID,))
            
            #Guarda as extrações da tabela
            colunas = cursor.fetchall()

            #Atualiza a data de última modificação
            cursor.execute("""UPDATE user_checkins SET data_mod = datetime('now') WHERE user_id = ?""", (userID,))

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
         
    def deleta_db(self, userID):
        """O método deleta_db apaga todas as entradas feitas pelo usuário"""

        try:
            #Estabelece a conexão e cria um cursor
            conexao = self.get_conexao()
            cursor = conexao.cursor() 

            #Deleta todos os items ligados a um usuário da tabela
            cursor.execute("""DELETE FROM user_checkins
                        WHERE user_id = ?""", (userID,))
            
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