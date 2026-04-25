"""
Processador de mensagens usando Anthropic Claude API

Gera resumos estruturados em JSON a partir de mensagens coletadas.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import json
from anthropic import Anthropic
from anthropic.types import Message

from src.config import settings
from .prompts import SYSTEM_PROMPT, SUMMARY_PROMPT_TEMPLATE
from src.utils.time_windows import format_period

logger = logging.getLogger(__name__)


class ClaudeProcessor:
    """
    Processa mensagens coletadas e gera resumo JSON estruturado usando Claude AI.
    
    Features:
    - Validação de API key
    - Formatação inteligente de mensagens
    - Agrupamento por fonte (WhatsApp/Discord)
    - Geração de JSON estruturado
    - Validação de schema
    - Retry automático em erros
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens
        
        logger.info(f"ClaudeProcessor inicializado: {self.model}")
    
    def test_connection(self) -> bool:
        """
        Testa conexão com API da Anthropic com uma chamada simples.
        
        Returns:
            True se a conexão está OK
        """
        try:
            logger.info("🔍 Testando conexão com Claude API...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {"role": "user", "content": "Responda apenas: OK"}
                ]
            )
            
            if response.content:
                logger.info(f"✅ Claude API OK - Modelo: {self.model}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar Claude API: {e}")
            return False
    
    def generate_summary(
        self,
        whatsapp_messages: List[Dict[str, Any]],
        discord_messages: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Gera resumo estruturado em JSON das mensagens usando Claude.
        
        Args:
            whatsapp_messages: Lista de mensagens do WhatsApp
            discord_messages: Lista de mensagens do Discord
            start_date: Data inicial do período
            end_date: Data final do período
        
        Returns:
            Dict com resumo estruturado ou None em caso de erro
        """
        try:
            logger.info(
                f"🤖 Gerando resumo com Claude: "
                f"{len(whatsapp_messages)} WhatsApp + {len(discord_messages)} Discord"
            )
            
            # Construir prompt
            user_prompt = self._build_prompt(
                whatsapp_messages=whatsapp_messages,
                discord_messages=discord_messages,
                start_date=start_date,
                end_date=end_date
            )
            
            # Chamar Claude API
            logger.debug(f"Enviando {len(user_prompt)} caracteres para Claude...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            # Extrair texto da resposta
            summary_text = self._extract_text_from_response(response)
            
            if not summary_text:
                logger.error("❌ Resposta vazia do Claude")
                return None
            
            # Parse JSON
            summary_json = self._parse_json_response(summary_text)
            
            if summary_json:
                logger.info("✅ Resumo gerado com sucesso")
                
                # Log de uso de tokens
                if hasattr(response, 'usage'):
                    logger.info(
                        f"📊 Tokens: "
                        f"input={response.usage.input_tokens}, "
                        f"output={response.usage.output_tokens}"
                    )
                
                return summary_json
            else:
                logger.error("❌ Falha ao parsear JSON da resposta")
                return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo com Claude: {e}", exc_info=True)
            return None
    
    def _build_prompt(
        self,
        whatsapp_messages: List[Dict[str, Any]],
        discord_messages: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """
        Constrói o prompt para enviar ao Claude.
        
        Args:
            whatsapp_messages: Mensagens do WhatsApp
            discord_messages: Mensagens do Discord
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Prompt formatado
        """
        # Formatar período
        period_label = format_period(start_date, end_date)
        
        # Formatar mensagens do WhatsApp
        whatsapp_formatted = self._format_messages(whatsapp_messages, "WhatsApp")
        
        # Formatar mensagens do Discord
        discord_formatted = self._format_messages(discord_messages, "Discord")
        
        # Construir prompt usando template
        prompt = SUMMARY_PROMPT_TEMPLATE.format(
            start_date=start_date.strftime("%d/%m/%Y"),
            end_date=end_date.strftime("%d/%m/%Y"),
            period_label=period_label,
            whatsapp_count=len(whatsapp_messages),
            discord_count=len(discord_messages),
            whatsapp_messages=whatsapp_formatted,
            discord_messages=discord_formatted
        )
        
        return prompt
    
    def _format_messages(
        self,
        messages: List[Dict[str, Any]],
        source_name: str
    ) -> str:
        """
        Formata lista de mensagens para inclusão no prompt.
        
        Args:
            messages: Lista de mensagens
            source_name: Nome da fonte (WhatsApp/Discord)
            
        Returns:
            String formatada com todas as mensagens
        """
        if not messages:
            return f"(Nenhuma mensagem de {source_name} neste período)"
        
        formatted = []
        
        # Agrupar por canal/conversa
        by_channel = {}
        for msg in messages:
            channel = msg.get('channel_name', 'Desconhecido')
            if channel not in by_channel:
                by_channel[channel] = []
            by_channel[channel].append(msg)
        
        # Formatar cada grupo
        for channel, msgs in sorted(by_channel.items()):
            formatted.append(f"\n### {channel}\n")
            
            for msg in sorted(msgs, key=lambda x: x.get('timestamp', datetime.min)):
                timestamp = msg.get('timestamp', datetime.min)
                sender = msg.get('sender', 'Desconhecido')
                content = msg.get('content', '')
                
                formatted.append(
                    f"[{timestamp.strftime('%d/%m %H:%M')}] {sender}: {content}\n"
                )
        
        return "".join(formatted)
    
    def _extract_text_from_response(self, response: Message) -> str:
        """
        Extrai texto da resposta do Claude.
        
        Args:
            response: Resposta da API
            
        Returns:
            Texto extraído
        """
        text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text += block.text
        return text.strip()
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parseia resposta JSON do Claude.
        
        Remove markdown se presente e valida estrutura.
        
        Args:
            text: Texto da resposta
            
        Returns:
            Dict parseado ou None se inválido
        """
        try:
            # Remover markdown code blocks se houver
            clean_text = text.strip()
            
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:]
            
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            clean_text = clean_text.strip()
            
            # Parse JSON
            data = json.loads(clean_text)
            
            # Validação básica do schema
            if not isinstance(data, dict):
                logger.error("Resposta não é um objeto JSON")
                return None
            
            required_keys = ["periodo", "clientes"]
            for key in required_keys:
                if key not in data:
                    logger.warning(f"Chave '{key}' não encontrada no JSON")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON: {e}")
            logger.debug(f"Texto recebido: {text[:500]}...")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao parsear resposta: {e}")
            return None
