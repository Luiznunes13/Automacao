"""
Agendador de tarefas usando APScheduler

Gerencia execução automática de coleta e processamento semanal.
"""

from datetime import datetime, timedelta
import asyncio
import logging
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.database import get_db, Message, ProcessedWindow, SourceType
from src.collectors import WhatsAppCollector, DiscordCollector
from src.processors import ClaudeProcessor
from src.delivery import EmailSender
from src.utils.time_windows import get_last_work_week, format_period

logger = logging.getLogger(__name__)


class WeeklyScheduler:
    """
    Gerencia o agendamento automático de coletas e geração de resumos semanais.
    
    Features:
    - Executa toda segunda-feira às 08h (configurável)
    - Coleta mensagens da semana anterior (seg-sex)
    - Gera resumo com Claude
    - Envia por e-mail
    - Previne duplicatas (idempotência)
    """
    
    def __init__(self):
        self.scheduler = BlockingScheduler(timezone=settings.collection_timezone)
        self.whatsapp_collector = WhatsAppCollector()
        self.discord_collector = DiscordCollector()
        self.processor = ClaudeProcessor()
        self.email_sender = EmailSender()
        self.timezone = pytz.timezone(settings.collection_timezone)
        
        logger.info(f"WeeklyScheduler inicializado - Timezone: {settings.collection_timezone}")
    
    def start(self):
        """
        Inicia o scheduler com as tarefas configuradas.
        
        Bloqueia a thread até receber Ctrl+C.
        """
        if not settings.scheduler_enabled:
            logger.warning("⚠️ Scheduler desabilitado nas configurações")
            return
        
        logger.info("🚀 Iniciando scheduler...")
        
        # Tarefa principal: Gerar resumo semanal (segunda-feira 08h por padrão)
        self.scheduler.add_job(
            self.generate_weekly_summary,
            trigger=CronTrigger.from_crontab(
                settings.report_schedule_cron,
                timezone=self.timezone
            ),
            id="weekly_summary",
            name="Geração de Resumo Semanal",
            replace_existing=True
        )
        
        logger.info(
            f"📅 Resumo semanal agendado: {settings.report_schedule_cron} "
            f"({settings.collection_timezone})"
        )
        
        logger.info("✅ Scheduler iniciado. Pressione Ctrl+C para parar.")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n⏹️ Scheduler interrompido pelo usuário")
            self.stop()
    
    def stop(self):
        """Para o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("⏹️ Scheduler parado")
    
    def generate_weekly_summary(self):
        """
        Tarefa principal: Coleta mensagens da última semana e gera resumo.
        
        Executada automaticamente toda segunda-feira às 08h (ou conforme configurado).
        
        Workflow:
        1. Calcula período (última seg-sex)
        2. Verifica se já foi processado
        3. Coleta WhatsApp
        4. Coleta Discord
        5. Persiste mensagens no DB
        6. Gera resumo com Claude
        7. Envia por e-mail
        8. Marca como processado
        """
        try:
            logger.info("=" * 70)
            logger.info("🔔 INICIANDO GERAÇÃO DE RESUMO SEMANAL")
            logger.info("=" * 70)
            
            # 1. Definir período (última semana de trabalho: seg-sex)
            start_date, end_date = get_last_work_week(timezone=settings.collection_timezone)
            
            logger.info(f"📆 Período: {format_period(start_date, end_date)}")
            
            # 2. Verificar se já foi processado (idempotência)
            with get_db() as db:
                existing = db.query(ProcessedWindow).filter(
                    ProcessedWindow.start_date == start_date,
                    ProcessedWindow.end_date == end_date
                ).first()
                
                if existing and existing.summary_sent:
                    logger.warning(
                        "⚠️ Este período já foi processado anteriormente. Pulando..."
                    )
                    return
            
            # 3. Coletar mensagens
            logger.info("📥 Coletando mensagens...")
            
            # WhatsApp
            logger.info("📱 WhatsApp...")
            whatsapp_messages = self.whatsapp_collector.collect_messages(
                start_date=start_date,
                end_date=end_date
            )
            
            # Discord
            logger.info("💬 Discord...")
            discord_messages = self.discord_collector.collect_messages(
                start_date=start_date,
                end_date=end_date
            )
            
            total_messages = len(whatsapp_messages) + len(discord_messages)
            logger.info(
                f"✅ Total coletado: {total_messages} mensagens "
                f"(WhatsApp: {len(whatsapp_messages)}, Discord: {len(discord_messages)})"
            )
            
            if total_messages == 0:
                logger.warning("⚠️ Nenhuma mensagem coletada. Abortando geração de resumo.")
                return
            
            # 4. Salvar mensagens no banco
            logger.info("💾 Salvando mensagens no banco de dados...")
            self._save_messages_to_db(whatsapp_messages, discord_messages)
            
            # 5. Gerar resumo com Claude
            logger.info("🤖 Gerando resumo com Claude AI...")
            summary_data = self.processor.generate_summary(
                whatsapp_messages=whatsapp_messages,
                discord_messages=discord_messages,
                start_date=start_date,
                end_date=end_date
            )
            
            if not summary_data:
                logger.error("❌ Falha ao gerar resumo. Abortando.")
                return
            
            # 6. Enviar por e-mail
            logger.info("📧 Enviando resumo por e-mail...")
            email_sent = self.email_sender.send_summary(
                summary_data=summary_data,
                start_date=start_date,
                end_date=end_date
            )
            
            # 7. Registrar janela processada
            with get_db() as db:
                window = ProcessedWindow(
                    start_date=start_date,
                    end_date=end_date,
                    total_messages=total_messages,
                    whatsapp_messages=len(whatsapp_messages),
                    discord_messages=len(discord_messages),
                    summary_sent=email_sent,
                    summary_recipient=settings.email_recipient,
                    summary_content=str(summary_data) if summary_data else None,
                    notes="Processamento concluído com sucesso" if email_sent else "Erro no envio do e-mail"
                )
                db.add(window)
                db.commit()
            
            logger.info("=" * 70)
            logger.info("✅ RESUMO SEMANAL GERADO E ENVIADO COM SUCESSO!")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo semanal: {e}", exc_info=True)
            
            # Registrar erro no banco
            try:
                with get_db() as db:
                    window = ProcessedWindow(
                        start_date=start_date,
                        end_date=end_date,
                        total_messages=0,
                        summary_sent=False,
                        notes=f"Erro: {str(e)}"
                    )
                    db.add(window)
                    db.commit()
            except:
                pass  # Se falhar ao registrar erro, apenas logar
    
    def _save_messages_to_db(self, whatsapp_messages: list, discord_messages: list):
        """
        Salva mensagens coletadas no banco de dados.
        
        Args:
            whatsapp_messages: Lista de mensagens do WhatsApp
            discord_messages: Lista de mensagens do Discord
        """
        with get_db() as db:
            saved_count = 0
            
            # WhatsApp
            for msg_data in whatsapp_messages:
                try:
                    msg = Message(
                        source=SourceType.WHATSAPP,
                        message_id=msg_data.get('message_id', ''),
                        timestamp=msg_data['timestamp'],
                        sender_id=msg_data.get('sender_id', ''),
                        sender_name=msg_data.get('sender', 'Desconhecido'),
                        channel_id=msg_data.get('channel_id', ''),
                        channel_name=msg_data.get('channel_name', ''),
                        content=msg_data.get('content', ''),
                        processed=False
                    )
                    db.add(msg)
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao salvar mensagem WhatsApp: {e}")
            
            # Discord
            for msg_data in discord_messages:
                try:
                    msg = Message(
                        source=SourceType.DISCORD,
                        message_id=msg_data.get('message_id', ''),
                        timestamp=msg_data['timestamp'],
                        sender_id=msg_data.get('sender_id', ''),
                        sender_name=msg_data.get('sender', 'Desconhecido'),
                        channel_id=msg_data.get('channel_id', ''),
                        channel_name=msg_data.get('channel_name', ''),
                        content=msg_data.get('content', ''),
                        processed=False
                    )
                    db.add(msg)
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao salvar mensagem Discord: {e}")
            
            db.commit()
            logger.info(f"✅ {saved_count} mensagens salvas no banco")
            logger.info("✅ Mensagens salvas no banco de dados")
    
    async def run_manual_collection(self, days_back: int = 7):
        """
        Executa coleta manual (para testes)
        
        Args:
            days_back: Quantos dias para trás coletar
        """
        logger.info(f"🔧 Executando coleta manual ({days_back} dias)")
        
        now = datetime.now(self.timezone)
        end_date = now
        start_date = now - timedelta(days=days_back)
        
        await self.generate_weekly_summary()
