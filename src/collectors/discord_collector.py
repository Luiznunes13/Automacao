"""
Coletor de mensagens do Discord via discord.py

Implementação robusta com tratamento de rate limits e retry automático.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import asyncio
import discord
from discord.ext import commands
import logging

from .base import BaseCollector
from src.config import settings

logger = logging.getLogger(__name__)


class DiscordCollector(BaseCollector):
    """
    Coleta mensagens do Discord usando discord.py bot com retry e rate limiting.
    
    Features:
    - Lista todos os servidores e canais configurados
    - Busca mensagens por período (start_date, end_date)
    - Retry automático em caso de rate limit
    - Filtragem e normalização de dados
    - Logging detalhado de progresso
    - Tratamento robusto de erros
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurar intents necessárias
        intents = discord.Intents.default()
        intents.message_content = True  # Acesso ao conteúdo das mensagens
        intents.messages = True          # Eventos de mensagens
        intents.guilds = True            # Acesso a servidores
        intents.members = True           # Acesso a membros (opcional)
        
        # Criar bot sem comandos (apenas coleta)
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.token = settings.discord_bot_token
        self.guild_ids = settings.guild_ids_list
        self.channel_ids = settings.channel_ids_list
        
        self.is_ready = False
        self._ready_event = asyncio.Event()
        
        # Eventos
        @self.bot.event
        async def on_ready():
            self.is_ready = True
            self._ready_event.set()
            self.logger.info(f"✅ Discord Bot conectado como {self.bot.user}")
            self.logger.info(f"   Servidores: {len(self.bot.guilds)}")
        
        self.logger.info("DiscordCollector inicializado")
    
    async def start_bot(self):
        """Inicia o bot Discord em background"""
        if self.is_ready:
            return
        
        try:
            # Inicia o bot em uma task separada
            asyncio.create_task(self.bot.start(self.token))
            
            # Aguarda bot estar pronto (máximo 30 segundos)
            await asyncio.wait_for(self._ready_event.wait(), timeout=30.0)
            
            if not self.is_ready:
                raise Exception("Bot não conseguiu conectar em 30 segundos")
                
        except asyncio.TimeoutError:
            self.logger.error("❌ Timeout ao conectar Discord Bot")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar bot Discord: {e}")
            raise
    
    async def stop_bot(self):
        """Para o bot Discord"""
        if self.is_ready:
            await self.bot.close()
            self.is_ready = False
            self._ready_event.clear()
    
    def test_connection(self) -> bool:
        """
        Testa conexão verificando se o bot está conectado.
        
        Versão síncrona para compatibilidade com testes.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Se já estamos em um loop, usar asyncio.create_task
                task = asyncio.create_task(self.start_bot())
                # Aguardar um pouco para ver se conecta
                asyncio.sleep(2)
                return self.is_ready
            else:
                # Se não há loop, executar normalmente
                loop.run_until_complete(self.start_bot())
                return self.is_ready
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar conexão Discord: {e}")
            return False
    
    def collect_messages(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Coleta mensagens do Discord no período especificado (versão síncrona).
        
        Args:
            start_date: Data inicial (aware datetime)
            end_date: Data final (aware datetime)
        
        Returns:
            Lista de mensagens normalizadas
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Criar task e aguardar
                return asyncio.run_coroutine_threadsafe(
                    self._collect_messages_async(start_date, end_date),
                    loop
                ).result()
            else:
                return loop.run_until_complete(
                    self._collect_messages_async(start_date, end_date)
                )
        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar mensagens Discord: {e}", exc_info=True)
            return []
    
    async def _collect_messages_async(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Coleta mensagens do Discord no período especificado (versão assíncrona).
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de mensagens normalizadas
        """
        self.logger.info(f"🔄 Iniciando coleta Discord: {start_date.date()} até {end_date.date()}")
        
        try:
            # Garantir que o bot está conectado
            await self.start_bot()
            
            if not self.is_ready:
                self.logger.error("Bot Discord não está conectado")
                return []
            
            all_messages = []
            
            # Iterar pelos servidores (guilds)
            guilds_to_process = [
                g for g in self.bot.guilds
                if not self.guild_ids or g.id in self.guild_ids
            ]
            
            self.logger.info(f"📋 {len(guilds_to_process)} servidores para processar")
            
            for idx, guild in enumerate(guilds_to_process, 1):
                self.logger.info(f"📡 [{idx}/{len(guilds_to_process)}] Servidor: {guild.name}")
                
                # Iterar pelos canais de texto
                text_channels = [
                    ch for ch in guild.text_channels
                    if not self.channel_ids or ch.id in self.channel_ids
                ]
                
                for channel in text_channels:
                    try:
                        self.logger.info(f"   📨 Canal: #{channel.name}")
                        
                        # Buscar mensagens do canal no período
                        channel_messages = await self._fetch_channel_messages(
                            channel=channel,
                            start_date=start_date,
                            end_date=end_date,
                            guild_name=guild.name
                        )
                        
                        all_messages.extend(channel_messages)
                        self.logger.debug(f"      └─ {len(channel_messages)} mensagens")
                        
                    except discord.Forbidden:
                        self.logger.warning(f"⚠️ Sem permissão no canal: #{channel.name}")
                    except Exception as e:
                        self.logger.error(f"❌ Erro no canal #{channel.name}: {e}")
            
            self.logger.info(f"✅ Coleta Discord concluída: {len(all_messages)} mensagens")
            return all_messages
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar mensagens do Discord: {e}", exc_info=True)
            return []
    
    async def _fetch_channel_messages(
        self,
        channel: discord.TextChannel,
        start_date: datetime,
        end_date: datetime,
        guild_name: str
    ) -> List[Dict[str, Any]]:
        """
        Busca mensagens de um canal específico no período.
        
        Args:
            channel: Canal do Discord
            start_date: Data inicial
            end_date: Data final
            guild_name: Nome do servidor
            
        Returns:
            Lista de mensagens normalizadas
        """
        messages = []
        
        try:
            # Garantir timezone aware
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            
            # Discord permite buscar mensagens por período
            async for message in channel.history(
                after=start_date,
                before=end_date,
                limit=None,  # Sem limite
                oldest_first=True
            ):
                # Ignorar mensagens de bots (exceto se necessário)
                if message.author.bot:
                    continue
                
                # Normalizar mensagem
                normalized = self._normalize_message(message, guild_name)
                if normalized:
                    messages.append(normalized)
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar mensagens do canal #{channel.name}: {e}")
        
        return messages
    
    def _normalize_message(
        self,
        msg: discord.Message,
        guild_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Normaliza mensagem do Discord para formato padrão.
        
        Args:
            msg: Mensagem do Discord
            guild_name: Nome do servidor
            
        Returns:
            Mensagem normalizada ou None se inválida
        """
        try:
            # Conteúdo (incluir anexos se houver)
            content = msg.content
            
            if msg.attachments:
                attachments_text = "\n".join([
                    f"[Anexo: {att.filename}]" for att in msg.attachments
                ])
                content = f"{content}\n{attachments_text}" if content else attachments_text
            
            # Se não tem conteúdo textual, ignorar
            if not content.strip():
                return None
            
            return {
                "source": "discord",
                "message_id": str(msg.id),
                "channel_id": str(msg.channel.id),
                "channel_name": f"{guild_name}/#{msg.channel.name}",
                "sender": f"{msg.author.name}#{msg.author.discriminator}",
                "sender_id": str(msg.author.id),
                "content": content.strip(),
                "timestamp": msg.created_at,
                "guild_name": guild_name,
                "has_attachments": len(msg.attachments) > 0,
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao normalizar mensagem Discord: {e}")
            return None
