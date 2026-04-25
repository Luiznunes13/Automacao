"""
Configurações centralizadas do projeto
Carrega variáveis de ambiente e valida configurações
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, validator

# Carrega .env do diretório raiz
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic"""
    
    # Evolution API (WhatsApp)
    evolution_api_url: str = Field(..., env="EVOLUTION_API_URL")
    evolution_api_key: str = Field(..., env="EVOLUTION_API_KEY")
    evolution_instance_name: str = Field(default="ncam_instance", env="EVOLUTION_INSTANCE_NAME")
    
    # Discord
    discord_bot_token: str = Field(..., env="DISCORD_BOT_TOKEN")
    discord_guild_ids: str = Field(..., env="DISCORD_GUILD_IDS")
    discord_channel_ids: str = Field(default="", env="DISCORD_CHANNEL_IDS")
    
    # Anthropic Claude
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=4096, env="ANTHROPIC_MAX_TOKENS")
    
    # Email (SMTP)
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(..., env="SMTP_USER")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    email_recipient: str = Field(..., env="EMAIL_RECIPIENT")
    email_from_name: str = Field(default="NCam Weekly Intel", env="EMAIL_FROM_NAME")
    
    # Database
    database_url: str = Field(default="sqlite:///./ncam_intel.db", env="DATABASE_URL")
    
    # Scheduler
    scheduler_enabled: bool = Field(default=True, env="SCHEDULER_ENABLED")
    report_schedule_cron: str = Field(default="0 8 * * MON", env="REPORT_SCHEDULE_CRON")
    collection_timezone: str = Field(default="America/Sao_Paulo", env="COLLECTION_TIMEZONE")
    
    # Coleta
    collection_days: str = Field(
        default="Monday,Tuesday,Wednesday,Thursday,Friday",
        env="COLLECTION_DAYS"
    )
    lookback_days: int = Field(default=7, env="LOOKBACK_DAYS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="ncam_intel.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("discord_guild_ids", "discord_channel_ids")
    def parse_ids(cls, v):
        """Converte string de IDs separados por vírgula em lista"""
        if not v:
            return []
        return [id.strip() for id in v.split(",") if id.strip()]
    
    @validator("collection_days")
    def parse_days(cls, v):
        """Converte dias da semana em lista"""
        if not v:
            return []
        return [day.strip() for day in v.split(",") if day.strip()]
    
    @property
    def guild_ids_list(self) -> List[int]:
        """Retorna lista de Guild IDs como inteiros"""
        if isinstance(self.discord_guild_ids, list):
            return [int(id) for id in self.discord_guild_ids]
        return []
    
    @property
    def channel_ids_list(self) -> List[int]:
        """Retorna lista de Channel IDs como inteiros"""
        if isinstance(self.discord_channel_ids, list):
            return [int(id) for id in self.discord_channel_ids if id]
        return []


# Instância global de configurações
settings = Settings()


# Configuração de logging
import logging
import colorlog

def setup_logging():
    """Configura logging com cores e arquivo"""
    
    # Handler para console com cores
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Silenciar loggers muito verbosos
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


# Inicializar logging ao importar config
setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"Configurações carregadas - Ambiente: {settings.collection_timezone}")
