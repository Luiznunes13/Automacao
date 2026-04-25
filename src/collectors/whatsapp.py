"""
Coletor de mensagens do WhatsApp via Evolution API

Implementação robusta com retry, backoff exponencial e tratamento de erros.
Compatível com Evolution API v2.x
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseCollector
from src.config import settings

logger = logging.getLogger(__name__)


class WhatsAppCollector(BaseCollector):
    """
    Coleta mensagens do WhatsApp usando Evolution API com retry e backoff exponencial.
    
    Features:
    - Lista todos os chats disponíveis
    - Busca mensagens por período (start_date, end_date)
    - Retry automático com backoff exponencial (3 tentativas)
    - Filtragem e normalização de dados
    - Logging detalhado de progresso
    - Tratamento robusto de erros
    
    Documentação Evolution API: https://doc.evolution-api.com/
    """
    
    def __init__(self):
        super().__init__()
        self.api_url = settings.evolution_api_url.rstrip('/')
        self.api_key = settings.evolution_api_key
        self.instance_name = settings.evolution_instance_name
        
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        # Configura sessão HTTP com retry automático
        self.session = self._create_session_with_retry()
        
        self.logger.info(f"WhatsAppCollector inicializado: {self.instance_name}")
    
    def _create_session_with_retry(self) -> requests.Session:
        """
        Cria sessão HTTP com retry automático e backoff exponencial
        """
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,  # 3 tentativas
            backoff_factor=2,  # backoff exponencial: 2s, 4s, 8s
            status_forcelist=[429, 500, 502, 503, 504],  # códigos que acionam retry
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def test_connection(self) -> bool:
        """
        Testa conexão com Evolution API verificando status da instância
        """
        try:
            url = f"{self.api_url}/instance/connectionState/{self.instance_name}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                state = data.get('state', 'unknown')
                self.logger.info(f"✅ Conexão Evolution API OK - Status: {state}")
                return True
            else:
                self.logger.error(f"❌ Erro ao conectar Evolution API: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar conexão Evolution API: {e}")
            return False
    
    def collect_messages(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Coleta mensagens do WhatsApp no período especificado.
        
        Este é o método principal que:
        1. Lista todos os chats disponíveis
        2. Para cada chat, busca mensagens no período
        3. Normaliza e retorna lista estruturada
        
        Args:
            start_date: Data inicial da coleta (incluído)
            end_date: Data final da coleta (incluído)
        
        Returns:
            Lista de dicts com estrutura padronizada:
            {
                'source': 'whatsapp',
                'message_id': str,
                'channel_id': str,
                'channel_name': str,
                'sender': str,
                'content': str,
                'timestamp': datetime
            }
        """
        self.logger.info(f"🔄 Iniciando coleta WhatsApp: {start_date.date()} até {end_date.date()}")
        
        try:
            messages = []
            
            # 1. Buscar todas as conversas (chats)
            self.logger.info("📋 Listando conversas...")
            chats = self._get_all_chats()
            
            if not chats:
                self.logger.warning("⚠️ Nenhuma conversa encontrada no WhatsApp")
                return []
            
            self.logger.info(f"✅ {len(chats)} conversas encontradas")
            
            # 2. Para cada conversa, buscar mensagens no período
            for idx, chat in enumerate(chats, 1):
                chat_id = chat.get('id')
                chat_name = chat.get('name') or chat.get('pushName') or 'Desconhecido'
                
                self.logger.info(f"📨 [{idx}/{len(chats)}] Coletando mensagens de: {chat_name}")
                
                chat_messages = self._get_chat_messages(
                    chat_id=chat_id,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # 3. Normalizar mensagens
                for msg in chat_messages:
                    normalized = self._normalize_message(msg, chat_id, chat_name)
                    if normalized:
                        messages.append(normalized)
                
                self.logger.debug(f"   └─ {len(chat_messages)} mensagens coletadas")
            
            self.logger.info(f"✅ Coleta WhatsApp concluída: {len(messages)} mensagens")
            return messages
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar mensagens do WhatsApp: {e}", exc_info=True)
            return []
    
    def _get_all_chats(self) -> List[Dict[str, Any]]:
        """
        Busca todas as conversas ativas do WhatsApp.
        
        Tenta múltiplos endpoints da Evolution API com retry automático.
        
        Returns:
            Lista de chats com id, name, etc.
        """
        endpoints = [
            f"{self.api_url}/chat/findChats/{self.instance_name}",
            f"{self.api_url}/chat/find/{self.instance_name}",
        ]
        
        for endpoint in endpoints:
            try:
                self.logger.debug(f"Tentando endpoint: {endpoint}")
                response = self.session.get(endpoint, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Evolution API pode retornar estruturas diferentes
                    chats = data if isinstance(data, list) else data.get('chats', [])
                    
                    if chats:
                        self.logger.debug(f"✅ {len(chats)} conversas encontradas via {endpoint}")
                        return chats
                else:
                    self.logger.debug(f"Endpoint retornou HTTP {response.status_code}")
                    
            except Exception as e:
                self.logger.debug(f"Erro no endpoint {endpoint}: {e}")
                continue
        
        # Se nenhum endpoint funcionou
        self.logger.warning("⚠️ Nenhum endpoint de chats funcionou")
        return []
    
    def _get_chat_messages(
        self,
        chat_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Busca mensagens de uma conversa específica no período.
        
        Utiliza retry automático via sessão HTTP configurada.
        
        Args:
            chat_id: ID da conversa (remoteJid)
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de mensagens brutas da API (serão normalizadas depois)
        """
        try:
            # Evolution API - endpoint de busca de mensagens
            url = f"{self.api_url}/message/find/{self.instance_name}"
            
            # Payload com filtros
            payload = {
                "where": {
                    "key": {
                        "remoteJid": chat_id
                    }
                },
                "limit": 1000  # Ajuste conforme necessário
            }
            
            response = self.session.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                messages = data if isinstance(data, list) else data.get('messages', [])
                
                # Filtrar por data
                filtered = []
                for msg in messages:
                    msg_timestamp = msg.get('messageTimestamp', 0)
                    
                    # Converter timestamp para datetime
                    if isinstance(msg_timestamp, str):
                        msg_date = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                    else:
                        # Timestamp Unix (segundos)
                        msg_date = datetime.fromtimestamp(int(msg_timestamp))
                    
                    # Filtrar por intervalo
                    if start_date <= msg_date <= end_date:
                        filtered.append(msg)
                
                return filtered
            else:
                self.logger.warning(f"⚠️ HTTP {response.status_code} ao buscar mensagens de {chat_id}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar mensagens do chat {chat_id}: {e}")
            return []
    
    def _normalize_message(
        self,
        raw_msg: Dict[str, Any],
        chat_id: str,
        chat_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Normaliza mensagem da Evolution API para formato padrão.
        
        Estrutura Evolution API (simplificada):
        {
            "key": {"id": "...", "remoteJid": "...", "fromMe": bool},
            "message": {"conversation": "texto", "extendedTextMessage": {...}},
            "messageTimestamp": 1234567890,
            "pushName": "Nome do Contato"
        }
        
        Args:
            raw_msg: Mensagem bruta da API
            chat_id: ID do chat
            chat_name: Nome do chat
            
        Returns:
            Mensagem normalizada ou None se inválida
        """
        try:
            # Extrair informações da estrutura Evolution API
            key = raw_msg.get('key', {})
            message_data = raw_msg.get('message', {})
            
            # Timestamp
            timestamp = raw_msg.get('messageTimestamp', 0)
            if isinstance(timestamp, str):
                msg_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                msg_datetime = datetime.fromtimestamp(int(timestamp))
            
            # Conteúdo (pode estar em diferentes campos)
            content = (
                message_data.get('conversation') or
                message_data.get('extendedTextMessage', {}).get('text') or
                message_data.get('imageMessage', {}).get('caption') or
                message_data.get('videoMessage', {}).get('caption') or
                "[Mídia não textual]"
            )
            
            # Se não tem conteúdo textual, ignorar
            if not content or content == "[Mídia não textual]":
                return None
            
            # Remetente
            sender_id = key.get('remoteJid', '')
            from_me = key.get('fromMe', False)
            push_name = raw_msg.get('pushName', 'Desconhecido')
            
            return {
                "source": "whatsapp",
                "message_id": key.get('id', ''),
                "channel_id": chat_id,
                "channel_name": chat_name,
                "sender": "Você (NCam)" if from_me else push_name,
                "sender_id": sender_id,
                "content": content.strip(),
                "timestamp": msg_datetime,
                "from_me": from_me,
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao normalizar mensagem: {e}")
            return None
