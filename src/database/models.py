"""
SQLAlchemy Models para persistência de dados
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class SourceType(enum.Enum):
    """Tipos de fonte de mensagens"""
    WHATSAPP = "whatsapp"
    DISCORD = "discord"


class Message(Base):
    """
    Armazena mensagens coletadas do WhatsApp e Discord
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação da fonte
    source = Column(SQLEnum(SourceType), nullable=False, index=True)
    source_id = Column(String(255), nullable=False, index=True)  # ID da mensagem na origem
    
    # Metadados temporais
    timestamp = Column(DateTime, nullable=False, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Identificação do remetente
    sender_id = Column(String(255), nullable=False)  # Phone number ou Discord user ID
    sender_name = Column(String(255))
    
    # Contexto
    chat_id = Column(String(255), nullable=False, index=True)  # WhatsApp chat ou Discord channel
    chat_name = Column(String(255))  # Nome do grupo/canal
    
    # Conteúdo
    content = Column(Text, nullable=False)
    
    # WhatsApp específico
    phone_number = Column(String(50))  # Número de telefone (WhatsApp)
    contact_name = Column(String(255))  # Nome do contato
    
    # Discord específico
    guild_id = Column(String(100))  # ID do servidor Discord
    guild_name = Column(String(255))  # Nome do servidor
    channel_name = Column(String(255))  # Nome do canal Discord
    
    # Controle de processamento
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Message {self.source.value} - {self.sender_name} @ {self.timestamp}>"
    
    def to_dict(self):
        """Serializa para dicionário"""
        return {
            "id": self.id,
            "source": self.source.value,
            "source_id": self.source_id,
            "timestamp": self.timestamp.isoformat(),
            "sender_name": self.sender_name,
            "chat_name": self.chat_name,
            "content": self.content,
            "processed": self.processed,
        }


class ProcessedWindow(Base):
    """
    Registra janelas de tempo já processadas para evitar duplicação
    """
    __tablename__ = "processed_windows"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Janela de tempo
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Metadados de processamento
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Estatísticas
    total_messages = Column(Integer, default=0)
    whatsapp_messages = Column(Integer, default=0)
    discord_messages = Column(Integer, default=0)
    
    # Resultado
    summary_sent = Column(Boolean, default=False)
    summary_recipient = Column(String(255))
    
    # Log
    notes = Column(Text)  # Erros, avisos, etc.
    
    def __repr__(self):
        return f"<ProcessedWindow {self.start_date} to {self.end_date}>"
