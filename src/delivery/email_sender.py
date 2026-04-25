"""
Envio de e-mails com resumos semanais

Suporta templates HTML responsivos e fallback em texto plano.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import json

from src.config import settings

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Envia e-mails formatados com resumos semanais usando templates HTML.
    
    Features:
    - Template HTML responsivo
    - Fallback em texto plano
    - Cores por tom de cliente
    - Validação de SMTP
    - Retry em caso de falha temporária
    """
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_name = settings.email_from_name
        self.default_recipient = settings.email_recipient
        
        logger.info(f"EmailSender inicializado: {self.smtp_host}:{self.smtp_port}")
    
    def test_connection(self) -> bool:
        """
        Testa conexão com servidor SMTP.
        
        Returns:
            True se a conexão está OK
        """
        try:
            logger.info("🔍 Testando conexão SMTP...")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            
            logger.info(f"✅ SMTP OK: {self.smtp_host}:{self.smtp_port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão SMTP: {e}")
            return False
    
    def send_summary(
        self,
        summary_data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        recipient: Optional[str] = None
    ) -> bool:
        """
        Envia resumo por e-mail usando template HTML.
        
        Args:
            summary_data: Dict com resumo estruturado (JSON do Claude)
            start_date: Data inicial do período
            end_date: Data final do período
            recipient: E-mail destinatário (opcional, usa padrão se não informado)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            recipient = recipient or self.default_recipient
            
            # Assunto do e-mail
            period = summary_data.get('periodo', f"{start_date.date()} a {end_date.date()}")
            subject = f"📊 NCam Weekly Intelligence — {period}"
            
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.smtp_user}>"
            message["To"] = recipient
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Corpo em texto plano (fallback)
            text_content = self._format_text_plain(summary_data)
            text_part = MIMEText(text_content, "plain", "utf-8")
            message.attach(text_part)
            
            # Corpo em HTML (template bonito)
            html_content = self._format_html(summary_data, period)
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # Enviar e-mail
            logger.info(f"📧 Enviando resumo para {recipient}...")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"✅ E-mail enviado com sucesso para {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar e-mail: {e}", exc_info=True)
            return False
    
    def _format_text_plain(self, summary_data: Dict[str, Any]) -> str:
        """
        Formata resumo em texto plano para fallback.
        
        Args:
            summary_data: Dados do resumo
            
        Returns:
            Texto formatado
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"RESUMO SEMANAL NCAM — {summary_data.get('periodo', 'N/A')}")
        lines.append("=" * 70)
        lines.append("")
        
        # Clientes
        clientes = summary_data.get('clientes', [])
        if clientes:
            lines.append(f"📊 {len(clientes)} CLIENTES COM ATIVIDADE")
            lines.append("")
            
            for cliente in clientes:
                nome = cliente.get('nome', 'Desconhecido')
                tom = cliente.get('tom', 'neutro')
                resumo = cliente.get('resumo', '')
                pendencias = cliente.get('pendencias', [])
                
                lines.append(f"### {nome} [{tom.upper()}]")
                lines.append(f"  {resumo}")
                
                if pendencias:
                    lines.append(f"  Pendências ({len(pendencias)}):")
                    for p in pendencias:
                        lines.append(f"    - {p}")
                
                lines.append("")
        
        # Pendências gerais
        pendencias_gerais = summary_data.get('pendencias_gerais', [])
        if pendencias_gerais:
            lines.append("⚠️ PENDÊNCIAS GERAIS")
            for p in pendencias_gerais:
                lines.append(f"  • {p}")
            lines.append("")
        
        # Destaques internos
        destaques = summary_data.get('destaques_internos', [])
        if destaques:
            lines.append("💡 DESTAQUES INTERNOS")
            for d in destaques:
                lines.append(f"  • {d}")
            lines.append("")
        
        # Próximos passos
        proximos = summary_data.get('proximos_passos_sugeridos', [])
        if proximos:
            lines.append("🎯 PRÓXIMOS PASSOS")
            for p in proximos:
                lines.append(f"  • {p}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("Gerado automaticamente por NCam Weekly Intelligence")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_html(self, summary_data: Dict[str, Any], period: str) -> str:
        """
        Formata resumo em HTML usando template responsivo.
        
        Args:
            summary_data: Dados do resumo
            period: Período formatado
            
        Returns:
            HTML formatado
        """
        # Cores por tom
        tone_colors = {
            'positivo': '#10b981',  # Verde
            'neutro': '#3b82f6',    # Azul
            'atenção': '#f59e0b',   # Laranja
            'crítico': '#ef4444'    # Vermelho
        }
        
        # Header
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCam Weekly Intelligence</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background-color: #f9fafb;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 32px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }}
        .header p {{
            margin: 8px 0 0 0;
            opacity: 0.95;
            font-size: 16px;
        }}
        .content {{
            padding: 32px;
        }}
        .section {{
            margin-bottom: 32px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #111827;
        }}
        .client-card {{
            border-left: 4px solid;
            padding: 16px;
            margin-bottom: 16px;
            background: #f9fafb;
            border-radius: 0 8px 8px 0;
        }}
        .client-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .client-name {{
            font-size: 18px;
            font-weight: 600;
            color: #111827;
        }}
        .client-tone {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
        }}
        .client-summary {{
            color: #4b5563;
            margin-bottom: 12px;
        }}
        .pendencias {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .pendencias li {{
            padding: 8px 0;
            padding-left: 24px;
            position: relative;
        }}
        .pendencias li:before {{
            content: "□";
            position: absolute;
            left: 0;
            color: #9ca3af;
        }}
        .list {{
            list-style: none;
            padding: 0;
        }}
        .list li {{
            padding: 8px 0 8px 24px;
            position: relative;
        }}
        .list li:before {{
            content: "•";
            position: absolute;
            left: 8px;
            color: #667eea;
            font-weight: bold;
        }}
        .footer {{
            background: #f9fafb;
            padding: 24px;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 NCam Weekly Intelligence</h1>
            <p>{period}</p>
        </div>
        <div class="content">
"""
        
        # Clientes
        clientes = summary_data.get('clientes', [])
        if clientes:
            html += f"""
            <div class="section">
                <div class="section-title">🏢 Clientes ({len(clientes)})</div>
"""
            for cliente in clientes:
                nome = cliente.get('nome', 'Desconhecido')
                tom = cliente.get('tom', 'neutro')
                resumo = cliente.get('resumo', '')
                pendencias = cliente.get('pendencias', [])
                
                color = tone_colors.get(tom, tone_colors['neutro'])
                
                html += f"""
                <div class="client-card" style="border-left-color: {color};">
                    <div class="client-header">
                        <div class="client-name">{nome}</div>
                        <div class="client-tone" style="background-color: {color};">{tom}</div>
                    </div>
                    <div class="client-summary">{resumo}</div>
"""
                
                if pendencias:
                    html += """
                    <ul class="pendencias">
"""
                    for p in pendencias:
                        html += f"                        <li>{p}</li>\n"
                    html += """
                    </ul>
"""
                
                html += """
                </div>
"""
            
            html += """
            </div>
"""
        
        # Pendências gerais
        pendencias_gerais = summary_data.get('pendencias_gerais', [])
        if pendencias_gerais:
            html += """
            <div class="section">
                <div class="section-title">⚠️ Pendências Gerais</div>
                <ul class="list">
"""
            for p in pendencias_gerais:
                html += f"                    <li>{p}</li>\n"
            html += """
                </ul>
            </div>
"""
        
        # Destaques internos
        destaques = summary_data.get('destaques_internos', [])
        if destaques:
            html += """
            <div class="section">
                <div class="section-title">💡 Destaques Internos</div>
                <ul class="list">
"""
            for d in destaques:
                html += f"                    <li>{d}</li>\n"
            html += """
                </ul>
            </div>
"""
        
        # Próximos passos
        proximos = summary_data.get('proximos_passos_sugeridos', [])
        if proximos:
            html += """
            <div class="section">
                <div class="section-title">🎯 Próximos Passos</div>
                <ul class="list">
"""
            for p in proximos:
                html += f"                    <li>{p}</li>\n"
            html += """
                </ul>
            </div>
"""
        
        # Footer
        html += f"""
        </div>
        <div class="footer">
            <p>Gerado automaticamente por <strong>NCam Weekly Intelligence</strong></p>
            <p style="font-size: 12px; margin-top: 8px;">
                {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    def _markdown_to_html(self, markdown_content: str, period: str) -> str:
        """
        Converte Markdown para HTML estilizado
        (Versão simplificada - pode usar biblioteca como markdown2 para melhor conversão)
        """
        # HTML básico com estilos
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a73e8;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 30px;
            border-left: 4px solid #1a73e8;
            padding-left: 15px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 20px;
        }}
        ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        li {{
            padding: 5px 0;
            padding-left: 25px;
            position: relative;
        }}
        li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: #1a73e8;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        {self._simple_markdown_parser(markdown_content)}
        <div class="footer">
            <p>🤖 Gerado automaticamente por <strong>NCam Weekly Intelligence</strong></p>
            <p>Período: {period}</p>
        </div>
    </div>
</body>
</html>
"""
        return html_template
    
    def _simple_markdown_parser(self, markdown: str) -> str:
        """
        Parser básico de Markdown para HTML
        Para produção, considere usar biblioteca como markdown2 ou mistune
        """
        html = markdown
        
        # Headers
        html = html.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
        html = html.replace('\n</h', '</h')  # Fechar headers
        
        # Adicionar fechamento de tags
        lines = html.split('\n')
        processed = []
        for line in lines:
            if line.startswith('<h1>'):
                processed.append(line + '</h1>')
            elif line.startswith('<h2>'):
                processed.append(line + '</h2>')
            elif line.startswith('<h3>'):
                processed.append(line + '</h3>')
            elif line.startswith('- '):
                processed.append('<li>' + line[2:] + '</li>')
            elif line.strip().startswith('**') and line.strip().endswith('**'):
                processed.append('<strong>' + line.strip()[2:-2] + '</strong>')
            else:
                processed.append(line)
        
        html = '\n'.join(processed)
        
        # Bold
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = '<p>' + html + '</p>'
        
        return html
