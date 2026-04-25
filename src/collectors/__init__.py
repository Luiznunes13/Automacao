"""
Collectors module - Coleta de mensagens do WhatsApp e Discord
"""

from .base import BaseCollector
from .whatsapp import WhatsAppCollector
from .discord_collector import DiscordCollector

__all__ = [
    "BaseCollector",
    "WhatsAppCollector",
    "DiscordCollector",
]
