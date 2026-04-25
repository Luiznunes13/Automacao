"""
NCam Weekly Intelligence - Entry Point
Sistema de resumo semanal automatizado WhatsApp + Discord
"""

import asyncio
import argparse
import sys
import logging
from datetime import datetime, timedelta

from src.config import settings, setup_logging
from src.database import init_db
from src.scheduler import WeeklyScheduler
from src.collectors import WhatsAppCollector, DiscordCollector
from src.processors import ClaudeProcessor
from src.delivery import EmailSender

logger = logging.getLogger(__name__)


async def test_integrations():
    """Testa todas as integrações"""
    logger.info("=" * 60)
    logger.info("🔍 TESTANDO INTEGRAÇÕES")
    logger.info("=" * 60)
    
    all_ok = True
    
    # 1. WhatsApp (Evolution API)
    logger.info("\n1️⃣ Testando WhatsApp (Evolution API)...")
    whatsapp = WhatsAppCollector()
    if await whatsapp.test_connection():
        logger.info("   ✅ WhatsApp OK")
    else:
        logger.error("   ❌ WhatsApp FALHOU")
        all_ok = False
    
    # 2. Discord
    logger.info("\n2️⃣ Testando Discord Bot...")
    discord_bot = DiscordCollector()
    if await discord_bot.test_connection():
        logger.info("   ✅ Discord OK")
        await discord_bot.stop_bot()
    else:
        logger.error("   ❌ Discord FALHOU")
        all_ok = False
    
    # 3. Claude AI
    logger.info("\n3️⃣ Testando Claude AI (Anthropic)...")
    claude = ClaudeProcessor()
    if claude.test_connection():
        logger.info("   ✅ Claude AI OK")
    else:
        logger.error("   ❌ Claude AI FALHOU")
        all_ok = False
    
    # 4. SMTP (E-mail)
    logger.info("\n4️⃣ Testando SMTP (E-mail)...")
    email = EmailSender()
    if email.test_connection():
        logger.info("   ✅ SMTP OK")
    else:
        logger.error("   ❌ SMTP FALHOU")
        all_ok = False
    
    logger.info("\n" + "=" * 60)
    if all_ok:
        logger.info("✅ TODAS AS INTEGRAÇÕES OK!")
    else:
        logger.error("❌ ALGUMAS INTEGRAÇÕES FALHARAM - VERIFIQUE AS CONFIGURAÇÕES")
    logger.info("=" * 60)
    
    return all_ok


async def manual_run(days_back: int = 7):
    """
    Executa manualmente a coleta e geração de resumo
    
    Args:
        days_back: Quantos dias para trás coletar
    """
    logger.info("=" * 60)
    logger.info("🔧 EXECUÇÃO MANUAL")
    logger.info("=" * 60)
    
    scheduler = WeeklyScheduler()
    
    # Executar geração de resumo
    await scheduler.generate_weekly_summary()
    
    # Fechar Discord bot se aberto
    await scheduler.discord_collector.stop_bot()


async def scheduled_run():
    """Executa em modo agendado (produção)"""
    logger.info("=" * 60)
    logger.info("📅 MODO AGENDADO - PRODUÇÃO")
    logger.info("=" * 60)
    
    scheduler = WeeklyScheduler()
    scheduler.start()
    
    logger.info("\n✅ Sistema em execução. Aguardando horários agendados...")
    logger.info("   Pressione Ctrl+C para encerrar\n")
    
    try:
        # Manter rodando indefinidamente
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n🛑 Encerrando scheduler...")
        scheduler.stop()
        await scheduler.discord_collector.stop_bot()
        logger.info("👋 Sistema encerrado")


async def collect_only(collector_name: str):
    """
    Apenas coleta mensagens sem processar
    
    Args:
        collector_name: "whatsapp" ou "discord"
    """
    logger.info(f"📥 Coletando apenas de: {collector_name}")
    
    import pytz
    tz = pytz.timezone(settings.collection_timezone)
    now = datetime.now(tz)
    start_date = now - timedelta(days=7)
    
    if collector_name == "whatsapp":
        collector = WhatsAppCollector()
        messages = await collector.collect_messages(start_date, now)
    elif collector_name == "discord":
        collector = DiscordCollector()
        messages = await collector.collect_messages(start_date, now)
        await collector.stop_bot()
    else:
        logger.error(f"Collector inválido: {collector_name}")
        return
    
    logger.info(f"\n✅ Coletadas {len(messages)} mensagens")
    
    # Exibir preview
    if messages:
        logger.info("\n📝 Preview das últimas 5 mensagens:")
        for msg in messages[-5:]:
            logger.info(
                f"  [{msg['timestamp'].strftime('%d/%m %H:%M')}] "
                f"{msg['sender_name']}: {msg['content'][:50]}..."
            )


def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(
        description="NCam Weekly Intelligence - Resumo Semanal Automatizado"
    )
    
    parser.add_argument(
        "--mode",
        choices=["test", "manual", "scheduled", "init"],
        default="test",
        help="Modo de execução (padrão: test)"
    )
    
    parser.add_argument(
        "--collector",
        choices=["whatsapp", "discord"],
        help="Coletar apenas de uma fonte específica"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Dias para trás na coleta manual (padrão: 7)"
    )
    
    args = parser.parse_args()
    
    # Banner
    print("\n" + "=" * 60)
    print("   📊 NCam Weekly Intelligence v1.0")
    print("   Resumo Semanal Automatizado WhatsApp + Discord")
    print("=" * 60 + "\n")
    
    # Inicializar banco de dados
    init_db()
    
    # Executar modo selecionado
    try:
        if args.mode == "test":
            asyncio.run(test_integrations())
        
        elif args.mode == "init":
            logger.info("✅ Banco de dados inicializado")
            logger.info("📝 Configure o arquivo .env e execute --mode test")
        
        elif args.mode == "manual":
            if args.collector:
                asyncio.run(collect_only(args.collector))
            else:
                asyncio.run(manual_run(args.days))
        
        elif args.mode == "scheduled":
            if not settings.scheduler_enabled:
                logger.warning(
                    "⚠️ Scheduler desabilitado no .env (SCHEDULER_ENABLED=false)"
                )
                sys.exit(1)
            asyncio.run(scheduled_run())
    
    except KeyboardInterrupt:
        logger.info("\n👋 Operação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
