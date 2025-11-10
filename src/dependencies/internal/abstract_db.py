from abc import abstractmethod, ABC
from dataclasses import dataclass
import sqlite3
import aiosqlite
import logging

class InternalDatabase(ABC):
    def __init__(self, session):
        """A classe database é utilizada como base para criar outras databases. 
        
        :Parametro database_path: string contendo o nome do arquivo em que serão armazenados os processos"""

        # O arquivo onde será salvo os processos
        self.DB = session

        #Cria o logger
        self.logger = logging.getLogger(__name__)
            
    @classmethod
    async def create(cls, database_path):
        instance = cls(database_path)

        # Cria a tabela de dados caso ela não existir
        await instance.init_db()

        return instance

    @abstractmethod
    async def init_db(self):
        """Cria a tabela de dados a ser utilizada"""
        pass


@dataclass(frozen=True)
class DBResult:
    success: bool
    data: any
    error: Exception | None