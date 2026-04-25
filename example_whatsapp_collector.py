"""
Exemplo de uso do WhatsAppCollector

Este script demonstra como usar o coletor de mensagens do WhatsApp.
"""

import asyncio
from datetime import datetime, timedelta
from src.collectors.whatsapp import WhatsAppCollector
from src.utils.time_windows import get_last_work_week, format_period
from src.config import setup_logging

# Configurar logging
setup_logging()


def example_basic_usage():
    """Exemplo básico de coleta de mensagens"""
    print("\n" + "="*60)
    print("📱 EXEMPLO 1: Coleta Básica - Última Semana")
    print("="*60 + "\n")
    
    # Criar coletor
    collector = WhatsAppCollector()
    
    # Testar conexão
    print("🔍 Testando conexão...")
    if not collector.test_connection():
        print("❌ Falha na conexão com Evolution API")
        return
    
    # Obter janela de tempo
    start_date, end_date = get_last_work_week()
    print(f"📅 Período: {format_period(start_date, end_date)}")
    
    # Coletar mensagens
    print("\n🔄 Iniciando coleta...\n")
    messages = collector.collect_messages(start_date, end_date)
    
    # Exibir resultados
    print(f"\n✅ Coletadas {len(messages)} mensagens")
    
    if messages:
        print("\n📊 Primeiras 3 mensagens:")
        for i, msg in enumerate(messages[:3], 1):
            print(f"\n  {i}. {msg['channel_name']}")
            print(f"     De: {msg['sender']}")
            print(f"     Em: {msg['timestamp'].strftime('%d/%m/%Y %H:%M')}")
            print(f"     Mensagem: {msg['content'][:100]}...")


def example_custom_period():
    """Exemplo com período customizado"""
    print("\n" + "="*60)
    print("📱 EXEMPLO 2: Período Customizado")
    print("="*60 + "\n")
    
    collector = WhatsAppCollector()
    
    # Definir período manualmente (últimos 7 dias)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Coletando: {start_date.date()} até {end_date.date()}")
    
    messages = collector.collect_messages(start_date, end_date)
    
    print(f"\n✅ Total: {len(messages)} mensagens")
    
    # Agrupar por canal
    channels = {}
    for msg in messages:
        channel = msg['channel_name']
        channels[channel] = channels.get(channel, 0) + 1
    
    print("\n📊 Mensagens por canal:")
    for channel, count in sorted(channels.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {channel}: {count} mensagens")


def example_filter_analysis():
    """Exemplo com análise e filtros"""
    print("\n" + "="*60)
    print("📱 EXEMPLO 3: Análise Filtrada")
    print("="*60 + "\n")
    
    collector = WhatsAppCollector()
    
    start_date, end_date = get_last_work_week()
    messages = collector.collect_messages(start_date, end_date)
    
    if not messages:
        print("⚠️ Nenhuma mensagem encontrada")
        return
    
    # Filtrar apenas mensagens recebidas (não enviadas)
    received = [m for m in messages if not m.get('from_me', False)]
    sent = [m for m in messages if m.get('from_me', False)]
    
    print(f"📨 Mensagens recebidas: {len(received)}")
    print(f"📤 Mensagens enviadas: {len(sent)}")
    
    # Top 5 contatos mais ativos
    contact_count = {}
    for msg in received:
        sender = msg['sender']
        contact_count[sender] = contact_count.get(sender, 0) + 1
    
    print("\n👥 Top 5 Contatos Mais Ativos:")
    for i, (contact, count) in enumerate(
        sorted(contact_count.items(), key=lambda x: x[1], reverse=True)[:5], 
        1
    ):
        print(f"  {i}. {contact}: {count} mensagens")
    
    # Palavras-chave
    keywords = ['instalação', 'problema', 'urgente', 'máquina', 'fanuc', 'cnc']
    
    print("\n🔍 Mensagens com palavras-chave:")
    for keyword in keywords:
        count = sum(1 for m in messages if keyword.lower() in m['content'].lower())
        if count > 0:
            print(f"  • '{keyword}': {count} menções")


def example_export_to_text():
    """Exemplo exportando para arquivo texto"""
    print("\n" + "="*60)
    print("📱 EXEMPLO 4: Exportar para Arquivo")
    print("="*60 + "\n")
    
    collector = WhatsAppCollector()
    
    start_date, end_date = get_last_work_week()
    messages = collector.collect_messages(start_date, end_date)
    
    if not messages:
        print("⚠️ Nenhuma mensagem para exportar")
        return
    
    # Exportar para arquivo
    filename = f"whatsapp_export_{start_date.date()}_to_{end_date.date()}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"EXPORTAÇÃO WHATSAPP - {format_period(start_date, end_date)}\n")
        f.write("="*80 + "\n\n")
        
        # Agrupar por canal
        by_channel = {}
        for msg in messages:
            channel = msg['channel_name']
            if channel not in by_channel:
                by_channel[channel] = []
            by_channel[channel].append(msg)
        
        # Escrever por canal
        for channel, msgs in sorted(by_channel.items()):
            f.write(f"\n{'='*80}\n")
            f.write(f"Canal: {channel} ({len(msgs)} mensagens)\n")
            f.write(f"{'='*80}\n\n")
            
            for msg in sorted(msgs, key=lambda x: x['timestamp']):
                f.write(f"[{msg['timestamp'].strftime('%d/%m/%Y %H:%M')}] {msg['sender']}\n")
                f.write(f"{msg['content']}\n")
                f.write("-"*80 + "\n\n")
    
    print(f"✅ Arquivo criado: {filename}")
    print(f"📊 {len(messages)} mensagens exportadas")


if __name__ == "__main__":
    print("\n" + "🚀 EXEMPLOS DE USO - WhatsApp Collector")
    print("="*60)
    
    try:
        # Executar exemplos
        example_basic_usage()
        
        input("\n⏸️  Pressione ENTER para continuar...")
        example_custom_period()
        
        input("\n⏸️  Pressione ENTER para continuar...")
        example_filter_analysis()
        
        input("\n⏸️  Pressione ENTER para continuar...")
        example_export_to_text()
        
        print("\n" + "="*60)
        print("✅ Todos os exemplos executados com sucesso!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
