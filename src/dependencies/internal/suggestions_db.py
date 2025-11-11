import sqlite3
import aiosqlite
from datetime import datetime, timedelta
import logging
from dependencies.internal.abstract_db import InternalDatabase, DBResult

class SuggestionsDB(InternalDatabase):
    def __init__(self, database_path):
        super().__init__(database_path)
        self.categories = ("fix", "feature", "outro",)

    async def init_db(self):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.cursor()

            try:
                #Cria a tabela de sugestões
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS bot_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    suggestion_title TEXT NOT NULL,
                    suggestion_body TEXT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) """)
                
                #Dá o commit do comando realizado
                await db.commit()

                #Loga o evento realizado
                self.logger.info('Tabela criada com sucesso!')

            except (sqlite3.Error, Exception) as e:
                if db:
                    #Anula a última ação feita pelo código, no caso a criação da tabela
                    await db.rollback() 

                    # Loga o erro ocorrido 
                    self.logger.critical('Erro ao criar a tabela')
                    print(e)


    async def add_db(self, category: str, suggestion_title: str, suggestion_body: str):

        if category not in self.categories:
            return DBResult(success=False, data= None, error=ValueError(f"Invalid category: {category}"))
        
        async with aiosqlite.connect(self.DB) as db:
            try:
                #Cria o cursor para fazer operações na tabela
                cursor = await db.cursor()

                #Inserindo na tabela
                await cursor.execute("""
                                INSERT INTO bot_suggestions (category, suggestion_title, suggestion_body)
                                VALUES (?, ?, ?)""", (category, suggestion_title, suggestion_body,))

                #Dá o commit do comando realizado
                await db.commit()

                #Loga o evento realizado       
                self.logger.info(f'{category}: "{suggestion_title}: {suggestion_body}" adicionado à tabela de sugestões com sucesso!')

                await cursor.execute("SELECT MAX(id) FROM bot_suggestions;")
                id = await cursor.fetchone()
                await cursor.execute("SELECT category, suggestion_title, suggestion_body FROM bot_suggestions WHERE id = ?", (id[0],))
                row = await cursor.fetchone()
                self.logger.debug(f'A mais nova row da tabela é: {row}')

                return DBResult(success=True, data=row, error=None)

            except (sqlite3.Error, Exception) as e:
                if db:
                    #Anula a última ação feita pelo código, no caso a adição de uma sugestão nova
                    await db.rollback() 

                # Loga o erro ocorrido 
                self.logger.error(f'Erro ao adicionar "{category}: {suggestion_title}: {suggestion_body}"')
                print(e)
                return DBResult(success=False, data=None, error=e)
            
    async def get_all_suggestions(self):
        async with aiosqlite.connect(self.DB) as db:
            try:
                #Estabelece a conexão e cria um cursor
                cursor = await db.cursor() 

                #Seleciona tudo da tabela
                await cursor.execute("""SELECT category, suggestion_title, suggestion_body FROM bot_suggestions ORDER BY date""")
                
                #Guarda as extrações da tabela
                rows = await cursor.fetchall()

                #Armazena em um dicionário
                suggestions = {
                    "fix": [],
                    "feature": [],
                    "outro": []
                }
                table_empty = True

                for cat, sug_title, sug_body in rows:
                    if cat in suggestions.keys():
                        table_empty = False
                        suggestions[cat].append((sug_title, sug_body,))        

                # Verifica se há itens para enviar
                if table_empty: 
                
                    self.logger.info(f'Não há sugestões na tabela')
                    return DBResult(success=True, data=None, error=None)
                
                else:

                    self.logger.debug(f'Dados da tabela: {suggestions}')
                    return DBResult(success=True, data= suggestions, error=None)
                
            except (sqlite3.Error, Exception) as e:
                # Loga o erro ocorrido 
                print(e)
                self.logger.error(f'Erro ao procurar as sugestões')
                return DBResult(success=False, data=None, error=e)
        
    async def get_specific_suggestions(self, category:str):
        if category not in self.categories:
            return DBResult(success=False, data= None, error=ValueError(f"Invalid category: {category}"))
        
        async with aiosqlite.connect(self.DB) as db:
            try:
                #Estabelece a conexão e cria um cursor
                cursor = await db.cursor() 

                #Seleciona tudo da tabela
                await cursor.execute("""SELECT suggestion_title, suggestion_body FROM bot_suggestions
                                    WHERE category = ?
                                    ORDER BY date""", (category,))
                
                #Guarda as extrações da tabela
                rows = await cursor.fetchall()

                suggestions = {category: []}
                table_empty = True

                for sug in rows:
                    suggestions[category].append(sug)
                    table_empty = False         

                # Verifica se há itens para enviar
                if table_empty: 
                    self.logger.info(f'Não há sugestões de {category} na tabela')
                    return DBResult(success=True, data=None, error=None)
                
                else:
                    self.logger.debug(f'Dados de {category} da tabela: {suggestions}')
                    return DBResult(success=True, data= suggestions, error=None)
                
            except (sqlite3.Error, Exception) as e:
                # Loga o erro ocorrido 
                print(e)
                self.logger.error(f'Erro ao procurar as sugestões')
                return DBResult(success=False, data=None, error=e)
            
    async def delete_suggestion(self, suggestion_title:str):
        async with aiosqlite.connect(self.DB) as db:
            try:
                #Estabelece a conexão e cria um cursor
                cursor = await db.cursor() 

                #Deleta a sugestão específica
                await cursor.execute("""DELETE FROM bot_suggestions WHERE suggestion_title = ? """, (suggestion_title,))
                
                #Dá o commit do comando realizado
                await db.commit()

                #Loga o evento ocorrido
                self.logger.info(f'Sugestão {suggestion_title} deletada da database')

                return DBResult(success=True, data=suggestion_title, error=None)

            except (sqlite3.Error, Exception) as e:
                if db:
                    #Anula a última ação feita pelo código, no caso a adição de uma sugestão nova
                    await db.rollback() 

                # Loga o erro ocorrido 
                self.logger.error(f'Erro ao deletar "{suggestion_title}"')
                print(e)
                return DBResult(success=False, data=None, error=e)

    async def maintenance_db(self, time: int = 240):
        """O método maintenance_db é feito pra apagar sugestões antigas"""

        async with aiosqlite.connect(self.DB) as db:
            try:
                #Estabelece o cursor
                cursor = await db.cursor()

                #Estabele a data limite para manter um dado na tabela
                limit_date = (datetime.now() - timedelta(days=time)).strftime('%Y-%m-%d %H:%M:%S') 

                #Deleta todos os items que estão na tabela há muito tempo
                await cursor.execute("""DELETE FROM bot_suggestions
                            WHERE date < ? """, (limit_date,))
                
                #Dá o commit do comando realizado
                await db.commit()

                #Loga o evento ocorrido
                self.logger.info('Exclusão de dados antigos realizada')

            except sqlite3.Error as e:
                if db:
                    #Anula a última ação feita pelo código, no caso deletar os itens antigos
                    await db.rollback() 

                # Loga o erro ocorrido 
                self.logger.error(f'Erro ao deletar os items antigos')
                print(e)
           

#DEBUG PLACE
async def tests():
    testingDB= await SuggestionsDB.create(database_path='src/dependencies/internal/test.db')

    logger= logging.basicConfig(
        format= "%(asctime)s [%(levelname)s] line:%(lineno)d - %(message)s",
        level= logging.DEBUG,
        filename='test.log' 
    )

import asyncio

if __name__== '__main__':
    asyncio.run(tests())
    