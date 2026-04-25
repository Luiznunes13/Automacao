"""
Templates de prompts para Claude AI
"""

SYSTEM_PROMPT = """Você é um assistente de inteligência operacional da NCam Tecnologia Industrial, empresa de monitoramento de máquinas CNC.

Você receberá mensagens coletadas do WhatsApp (relacionamento com clientes) e do Discord (comunicação interna da equipe) referentes à semana de trabalho indicada.

Sua tarefa é gerar um resumo semanal estruturado em JSON, seguindo exatamente o schema fornecido.

## Regras de Análise:

1. **Agrupamento**: Agrupe tudo por cliente/projeto. Se uma conversa não menciona cliente específico, classifique como "Interno" ou "Geral".

2. **Pendências**: São itens que ficaram SEM resolução confirmada. Se foi resolvido na semana, NÃO liste como pendência.

3. **Tom**: Classifique o tom de cada cliente como:
   - "positivo": Cliente satisfeito, instalação bem-sucedida, feedback positivo
   - "neutro": Comunicação operacional normal, sem urgência
   - "atenção": Cliente com dúvidas recorrentes, problemas não críticos
   - "crítico": Problemas graves, cliente insatisfeito, urgência alta

4. **Destaques internos**: Decisões estratégicas ou técnicas relevantes discutidas no Discord (mudança de ferramentas, novos procedimentos, avaliações técnicas).

5. **Próximos passos**: Devem ser concretos e acionáveis, NÃO genéricos. Incluir dia da semana se relevante.

6. **Correlação**: Sempre que possível, correlacione o que foi discutido no WhatsApp (cliente) com o que a equipe debateu no Discord (interno).

## Equipe NCam (para reconhecer nomes):
- Luiz: Técnico de campo
- Yuri: Técnico de campo  
- Mariana: Analista de suporte
- Guilherme: Suporte técnico

## IMPORTANTE:
- Responda APENAS com o JSON, sem texto adicional
- NÃO use markdown (```json)
- Siga o schema exatamente
"""


SUMMARY_PROMPT_TEMPLATE = """Analise as mensagens coletadas entre {start_date} e {end_date} e gere um resumo estruturado.

# Mensagens Coletadas

## WhatsApp ({whatsapp_count} mensagens)
{whatsapp_messages}

## Discord ({discord_count} mensagens)
{discord_messages}

---

# Schema JSON Esperado

Retorne APENAS o JSON seguindo este schema EXATAMENTE:

{{
  "periodo": "{period_label}",
  "clientes": [
    {{
      "nome": "Nome do Cliente",
      "resumo": "Resumo objetivo do que aconteceu com este cliente na semana (correlacione WhatsApp + Discord)",
      "pendencias": [
        "Ação ou item específico não resolvido",
        "Outra pendência concreta"
      ],
      "tom": "positivo|neutro|atenção|crítico"
    }}
  ],
  "pendencias_gerais": [
    "Pendências que não são de um cliente específico"
  ],
  "destaques_internos": [
    "Decisões técnicas ou estratégicas relevantes discutidas no Discord"
  ],
  "proximos_passos_sugeridos": [
    "Ação concreta e acionável com contexto (ex: 'Segunda: checar status instalação Metaltim')",
    "Outra ação específica"
  ]
}}

Agora analise as mensagens e retorne o JSON.

**IMPORTANTE**:
- Se não houver mensagens de um cliente em uma fonte, mencione "Sem comunicação registrada"
- Correlacione sempre WhatsApp com Discord quando o mesmo cliente aparecer em ambos
- Priorize clareza e objetividade
- Use emojis apenas onde indicado no template
- Formate datas no padrão brasileiro (DD/MM/YYYY)
"""


MESSAGES_FORMAT_TEMPLATE = """
[{timestamp}] {sender_name} ({chat_name}):
{content}
"""


def format_messages_for_prompt(messages: list, source: str) -> str:
    """
    Formata lista de mensagens para inclusão no prompt
    
    Args:
        messages: Lista de mensagens (dicts)
        source: "whatsapp" ou "discord"
    
    Returns:
        String formatada com todas as mensagens
    """
    if not messages:
        return f"Nenhuma mensagem {source} coletada neste período.\n"
    
    formatted = []
    for msg in messages:
        timestamp = msg['timestamp'].strftime('%d/%m/%Y %H:%M')
        sender = msg.get('sender_name', 'Desconhecido')
        chat = msg.get('chat_name', 'N/A')
        content = msg.get('content', '')
        
        formatted.append(
            MESSAGES_FORMAT_TEMPLATE.format(
                timestamp=timestamp,
                sender_name=sender,
                chat_name=chat,
                content=content
            )
        )
    
    return "\n".join(formatted)


def build_summary_prompt(
    whatsapp_messages: list,
    discord_messages: list,
    start_date,
    end_date
) -> str:
    """
    Constrói o prompt completo para geração do resumo
    
    Args:
        whatsapp_messages: Lista de mensagens do WhatsApp
        discord_messages: Lista de mensagens do Discord
        start_date: Data inicial do período
        end_date: Data final do período
    
    Returns:
        Prompt formatado pronto para envio ao Claude
    """
    period_label = f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
    
    whatsapp_formatted = format_messages_for_prompt(whatsapp_messages, "whatsapp")
    discord_formatted = format_messages_for_prompt(discord_messages, "discord")
    
    return SUMMARY_PROMPT_TEMPLATE.format(
        start_date=start_date.strftime('%d/%m/%Y'),
        end_date=end_date.strftime('%d/%m/%Y'),
        period_label=period_label,
        whatsapp_count=len(whatsapp_messages),
        discord_count=len(discord_messages),
        total_count=len(whatsapp_messages) + len(discord_messages),
        whatsapp_messages=whatsapp_formatted,
        discord_messages=discord_formatted,
    )
