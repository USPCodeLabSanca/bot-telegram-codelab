from abc import abstractmethod, ABC
import sqlite3
import threading
import logging

class internal_database(ABC):
    def __init__(self, database_path):
        """A classe database é utilizada como base para criar outras databases. 
        
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
    
    @abstractmethod
    def inicia_db(self):
        pass

    @abstractmethod
    def add_db(self, chatID: int):
        pass
    
    @abstractmethod
    def extrai_db(self, chatID: int):
        pass

    @abstractmethod     
    def deleta_db(self, chatID: int):
        pass

    @abstractmethod
    def manutencao_db(self):
        pass

    