"""
Interface base para coletores de mensagens
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
import logging

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    Classe abstrata para coletores de mensagens
    Define a interface que todos os coletores devem implementar
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def collect_messages(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[dict]:
        """
        Coleta mensagens dentro do período especificado
        
        Args:
            start_date: Data/hora inicial
            end_date: Data/hora final
        
        Returns:
            Lista de dicionários com as mensagens coletadas
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Testa a conexão com a fonte de dados
        
        Returns:
            True se conectado com sucesso, False caso contrário
        """
        pass
    
    def _log_collection(self, count: int, start: datetime, end: datetime):
        """Helper para logging de coletas"""
        self.logger.info(
            f"✅ Coletadas {count} mensagens de {start.strftime('%d/%m/%Y %H:%M')} "
            f"até {end.strftime('%d/%m/%Y %H:%M')}"
        )
