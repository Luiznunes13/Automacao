"""
Utilitários para visualização e manutenção do banco de dados
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy import func

from src.database import get_db, Message, ProcessedWindow, SourceType
from src.config import setup_logging

setup_logging()


def show_statistics():
    """Exibe estatísticas do banco de dados"""
    print("\n" + "=" * 60)
    print("   📊 Estatísticas do Banco de Dados")
    print("=" * 60 + "\n")
    
    with get_db() as db:
        # Total de mensagens
        total = db.query(Message).count()
        whatsapp = db.query(Message).filter(Message.source == SourceType.WHATSAPP).count()
        discord = db.query(Message).filter(Message.source == SourceType.DISCORD).count()
        
        print(f"Total de Mensagens: {total}")
        print(f"  • WhatsApp: {whatsapp}")
        print(f"  • Discord: {discord}")
        
        # Mensagens processadas
        processed = db.query(Message).filter(Message.processed == True).count()
        print(f"\nMensagens Processadas: {processed}/{total}")
        
        # Períodos processados
        windows = db.query(ProcessedWindow).count()
        windows_sent = db.query(ProcessedWindow).filter(
            ProcessedWindow.summary_sent == True
        ).count()
        
        print(f"\nPeríodos Processados: {windows}")
        print(f"  • Resumos enviados: {windows_sent}")
        
        # Última mensagem
        last_msg = db.query(Message).order_by(Message.timestamp.desc()).first()
        if last_msg:
            print(f"\nÚltima Mensagem: {last_msg.timestamp.strftime('%d/%m/%Y %H:%M')}")
            print(f"  • Fonte: {last_msg.source.value}")
            print(f"  • De: {last_msg.sender_name}")
        
        # Mensagens por dia (últimos 7 dias)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent = db.query(Message).filter(
            Message.timestamp >= seven_days_ago
        ).count()
        
        print(f"\nMensagens (últimos 7 dias): {recent}")
    
    print("\n" + "=" * 60 + "\n")


def list_recent_messages(limit=10, source=None):
    """Lista mensagens recentes"""
    print("\n" + "=" * 60)
    print(f"   📝 Últimas {limit} Mensagens")
    print("=" * 60 + "\n")
    
    with get_db() as db:
        query = db.query(Message).order_by(Message.timestamp.desc())
        
        if source:
            source_type = SourceType.WHATSAPP if source.lower() == "whatsapp" else SourceType.DISCORD
            query = query.filter(Message.source == source_type)
        
        messages = query.limit(limit).all()
        
        for msg in messages:
            print(f"[{msg.timestamp.strftime('%d/%m/%Y %H:%M')}] {msg.source.value.upper()}")
            print(f"  De: {msg.sender_name}")
            print(f"  Chat: {msg.chat_name}")
            print(f"  Mensagem: {msg.content[:100]}...")
            print()
    
    print("=" * 60 + "\n")


def list_processed_windows():
    """Lista períodos já processados"""
    print("\n" + "=" * 60)
    print("   📅 Períodos Processados")
    print("=" * 60 + "\n")
    
    with get_db() as db:
        windows = db.query(ProcessedWindow).order_by(
            ProcessedWindow.processed_at.desc()
        ).all()
        
        if not windows:
            print("Nenhum período processado ainda.\n")
            return
        
        for w in windows:
            status = "✅ Enviado" if w.summary_sent else "❌ Não enviado"
            print(f"{w.start_date.strftime('%d/%m/%Y')} a {w.end_date.strftime('%d/%m/%Y')} - {status}")
            print(f"  • Mensagens: {w.total_messages} (WA: {w.whatsapp_messages}, DC: {w.discord_messages})")
            print(f"  • Processado em: {w.processed_at.strftime('%d/%m/%Y %H:%M')}")
            if w.notes:
                print(f"  • Notas: {w.notes}")
            print()
    
    print("=" * 60 + "\n")


def clear_old_messages(days=30):
    """Remove mensagens antigas do banco"""
    print(f"\n⚠️  Removendo mensagens com mais de {days} dias...")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with get_db() as db:
        deleted = db.query(Message).filter(
            Message.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        print(f"✅ {deleted} mensagens removidas\n")


def export_to_csv(output_file="export_messages.csv"):
    """Exporta mensagens para CSV"""
    import csv
    
    print(f"\n📤 Exportando mensagens para {output_file}...")
    
    with get_db() as db:
        messages = db.query(Message).order_by(Message.timestamp).all()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Fonte', 'Data/Hora', 'Remetente', 'Chat', 'Conteúdo'
            ])
            
            for msg in messages:
                writer.writerow([
                    msg.id,
                    msg.source.value,
                    msg.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                    msg.sender_name,
                    msg.chat_name,
                    msg.content
                ])
        
        print(f"✅ {len(messages)} mensagens exportadas\n")


def main():
    """Menu principal"""
    if len(sys.argv) < 2:
        print("\nUso: python utils.py [comando]")
        print("\nComandos disponíveis:")
        print("  stats              - Exibir estatísticas")
        print("  recent [N]         - Listar últimas N mensagens (padrão: 10)")
        print("  whatsapp [N]       - Listar últimas N mensagens do WhatsApp")
        print("  discord [N]        - Listar últimas N mensagens do Discord")
        print("  windows            - Listar períodos processados")
        print("  clear [days]       - Remover mensagens antigas (padrão: 30 dias)")
        print("  export [arquivo]   - Exportar mensagens para CSV")
        print()
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_statistics()
    
    elif command == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_recent_messages(limit)
    
    elif command == "whatsapp":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_recent_messages(limit, source="whatsapp")
    
    elif command == "discord":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_recent_messages(limit, source="discord")
    
    elif command == "windows":
        list_processed_windows()
    
    elif command == "clear":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        confirm = input(f"⚠️  Confirma remover mensagens com mais de {days} dias? (s/N): ")
        if confirm.lower() == 's':
            clear_old_messages(days)
        else:
            print("Operação cancelada.\n")
    
    elif command == "export":
        output = sys.argv[2] if len(sys.argv) > 2 else "export_messages.csv"
        export_to_csv(output)
    
    else:
        print(f"Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
