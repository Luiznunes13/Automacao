# 🔄 Fluxo de Dados - NCam Weekly Intelligence

Este documento descreve visualmente como os dados fluem pelo sistema.

---

## 📊 Diagrama de Fluxo Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                    FONTES DE DADOS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📱 WhatsApp                    💬 Discord                      │
│  (Evolution API)                (discord.py Bot)                │
│  - Grupos de clientes           - Canais internos               │
│  - Conversas diretas            - Discussões técnicas           │
│  - Suporte                      - Decisões de equipe            │
│                                                                 │
└────────────┬──────────────────────────┬─────────────────────────┘
             │                          │
             │  HTTP REST               │  WebSocket
             │  (retry + backoff)       │  (real-time)
             ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE COLETA                             │
│                    (collectors/)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ WhatsAppCollector         ⏳ DiscordCollector               │
│  ├─ test_connection()        ├─ test_connection()              │
│  ├─ collect_messages()       ├─ collect_messages()             │
│  ├─ _get_all_chats()         ├─ _get_guild_channels()          │
│  ├─ _get_chat_messages()     ├─ _get_channel_history()         │
│  └─ _normalize_message()     └─ _normalize_message()           │
│                                                                 │
│  🔄 Retry: 3 tentativas, backoff exponencial (2s, 4s, 8s)      │
│  📅 Filtro: Segunda 00h - Sexta 23h59 (semana anterior)        │
│                                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             │  Lista[Dict] - Mensagens normalizadas
             │  {source, message_id, channel_id, sender, 
             │   content, timestamp, ...}
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE PERSISTÊNCIA                       │
│                    (database/)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  💾 SQLite Database (ncam_intel.db)                             │
│                                                                 │
│  📋 Tabelas:                                                    │
│  ├─ messages                                                    │
│  │  ├─ id (PK)                                                  │
│  │  ├─ source (whatsapp|discord)                               │
│  │  ├─ message_id (unique)     ← Previne duplicatas            │
│  │  ├─ channel_id, channel_name                                │
│  │  ├─ sender_id, sender_name                                  │
│  │  ├─ content, timestamp                                      │
│  │  └─ processed (boolean)                                     │
│  │                                                              │
│  └─ processed_windows                                           │
│     ├─ id (PK)                                                  │
│     ├─ start_date, end_date                                     │
│     ├─ summary_generated_at                                     │
│     ├─ summary_sent (boolean)                                   │
│     └─ summary_content (JSON)                                   │
│                                                                 │
│  🔐 Idempotência: message_id é UNIQUE                           │
│  ⚡ Performance: Índices em timestamp, source, channel_id       │
│                                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             │  Query: SELECT * WHERE 
             │    start_date <= timestamp <= end_date
             │    AND processed = False
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CAMADA DE PROCESSAMENTO                       │
│                   (processors/)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🧠 ClaudeProcessor                                             │
│  ├─ Agrupa mensagens por cliente/canal                         │
│  ├─ Formata contexto para Claude                               │
│  ├─ Envia para Anthropic API                                   │
│  └─ Valida e parseia resposta JSON                             │
│                                                                 │
│  📝 Prompts (prompts.py):                                       │
│  ├─ SYSTEM_PROMPT                                               │
│  │  └─ Define papel, regras, tom, equipe                       │
│  └─ SUMMARY_PROMPT_TEMPLATE                                     │
│     └─ Instruções específicas + schema JSON                     │
│                                                                 │
│  🔑 API: Anthropic Claude (claude-sonnet-4)                     │
│  📊 Input: Mensagens agrupadas + contexto                       │
│  📤 Output: JSON estruturado                                    │
│                                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             │  JSON Response:
             │  {
             │    "periodo": "21/04 a 25/04",
             │    "clientes": [{
             │      "nome": "Cliente X",
             │      "resumo": "...",
             │      "pendencias": [...],
             │      "tom": "positivo"
             │    }],
             │    "pendencias_gerais": [...],
             │    "destaques_internos": [...],
             │    "proximos_passos_sugeridos": [...]
             │  }
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE ENTREGA                            │
│                    (delivery/)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📧 EmailSender                                                 │
│  ├─ Formata JSON em HTML bonito                                │
│  ├─ Adiciona estilo, cores, ícones                             │
│  ├─ Conecta ao servidor SMTP                                   │
│  └─ Envia e-mail                                                │
│                                                                 │
│  📨 Configuração:                                               │
│  ├─ SMTP: smtp.gmail.com:587 (TLS)                             │
│  ├─ De: ncam-intel@empresa.com                                 │
│  ├─ Para: email_recipient (do .env)                            │
│  └─ Assunto: "NCam Weekly Intel - [período]"                   │
│                                                                 │
│  ✨ Template HTML:                                              │
│  ├─ Header com logo e período                                  │
│  ├─ Cards por cliente (com cor por tom)                        │
│  ├─ Seção de pendências prioritárias                           │
│  ├─ Destaques internos                                         │
│  └─ Próximos passos acionáveis                                 │
│                                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DESTINO FINAL                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📬 Inbox do Usuário                                            │
│  └─ E-mail formatado com resumo semanal                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏰ Fluxo de Agendamento (Scheduler)

```
┌──────────────────────────────────────────────────────────┐
│  ⏰ APScheduler                                          │
│  (scheduler/jobs.py)                                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Cron: "0 8 * * MON"                                     │
│  └─ Toda segunda-feira às 08h00                         │
│                                                          │
│  1. Trigger acionado                                     │
│  2. Calcula janela: última seg-sex                       │
│     (utils.time_windows.get_last_work_week())           │
│  3. Verifica se já foi processado (DB)                  │
│  4. Se não: executa workflow completo                   │
│  5. Marca window como processada                        │
│  6. Aguarda próximo trigger                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow Completo (Execução Manual ou Agendada)

```
INÍCIO
  │
  ├─ 1. Calcular janela de tempo
  │    └─ get_last_work_week()
  │    └─ start: Segunda 00h00, end: Sexta 23h59
  │
  ├─ 2. Verificar se já processado
  │    └─ Query: processed_windows WHERE start_date = ?
  │    └─ Se SIM: PARAR
  │
  ├─ 3. Coletar WhatsApp
  │    ├─ WhatsAppCollector.test_connection()
  │    ├─ WhatsAppCollector.collect_messages(start, end)
  │    └─ Resultado: Lista[Mensagem]
  │
  ├─ 4. Coletar Discord
  │    ├─ DiscordCollector.test_connection()
  │    ├─ DiscordCollector.collect_messages(start, end)
  │    └─ Resultado: Lista[Mensagem]
  │
  ├─ 5. Persistir no banco
  │    ├─ INSERT INTO messages (com IGNORE duplicatas)
  │    └─ Commit transaction
  │
  ├─ 6. Processar com Claude
  │    ├─ Agrupar mensagens por fonte
  │    ├─ Formatar prompt com contexto
  │    ├─ Chamar Anthropic API
  │    ├─ Validar JSON de resposta
  │    └─ Resultado: JSON estruturado
  │
  ├─ 7. Entregar via E-mail
  │    ├─ Formatar JSON em HTML
  │    ├─ Conectar SMTP
  │    ├─ Enviar e-mail
  │    └─ Confirmar entrega
  │
  ├─ 8. Registrar conclusão
  │    ├─ INSERT INTO processed_windows
  │    ├─ UPDATE messages SET processed = True
  │    └─ Log de sucesso
  │
FIM (✅ Resumo semanal entregue!)
```

---

## 📁 Mapa de Arquivos por Etapa

### Etapa 1-2: Inicialização
- `main.py` - Entry point
- `src/config.py` - Configurações
- `src/utils/time_windows.py` - Cálculo de janelas

### Etapa 3-4: Coleta
- `src/collectors/whatsapp.py` ✅ **COMPLETO**
- `src/collectors/discord_collector.py` ⏳ *Pendente*
- `src/collectors/base.py` - Interface comum

### Etapa 5: Persistência
- `src/database/models.py` - Modelos SQLAlchemy
- `src/database/database.py` - Conexão e helpers

### Etapa 6: Processamento
- `src/processors/claude_processor.py` - Cliente Anthropic
- `src/processors/prompts.py` ✅ **ATUALIZADO**

### Etapa 7: Entrega
- `src/delivery/email_sender.py` - Envio SMTP

### Etapa 8: Agendamento
- `src/scheduler/jobs.py` - APScheduler jobs

---

## 🎯 Pontos de Entrada

### 1. Teste de Integração
```powershell
python main.py test
```
- Testa todas as conexões
- Não persiste dados
- Rápido feedback

### 2. Coleta Manual
```powershell
python main.py collect
```
- Coleta última semana
- Persiste no banco
- Não gera resumo

### 3. Execução Completa
```powershell
python main.py run
```
- Workflow completo
- Coleta + Processamento + Entrega

### 4. Scheduler Daemon
```powershell
python main.py schedule
```
- Fica em loop
- Executa automaticamente toda segunda às 08h
- Ctrl+C para parar

### 5. Exemplo Standalone
```powershell
python example_whatsapp_collector.py
```
- Demonstração do WhatsApp Collector
- Vários exemplos de uso
- Exportação para .txt

---

## 🔐 Garantias de Segurança

### Idempotência
- ✅ `message_id` único previne duplicatas
- ✅ `processed_windows` previne reprocessamento
- ✅ Safe para executar múltiplas vezes

### Tratamento de Erros
- ✅ Try/except em todos os níveis
- ✅ Logging detalhado
- ✅ Rollback de transações em falha
- ✅ Retry automático com backoff

### Privacidade
- ✅ Credenciais em `.env` (não commitado)
- ✅ Logs sem dados sensíveis
- ✅ Database local (SQLite)

---

## 📊 Métricas e Observabilidade

### Logging Levels
- **INFO**: Progresso normal (coleta iniciada, X mensagens coletadas)
- **WARNING**: Situações inesperadas mas recuperáveis
- **ERROR**: Falhas que impedem uma etapa específica
- **DEBUG**: Detalhes técnicos (endpoints, payloads)

### Exemplos de Logs
```
2025-04-28 08:00:00 [INFO] 🔄 Iniciando coleta WhatsApp: 2025-04-21 até 2025-04-25
2025-04-28 08:00:02 [INFO] ✅ 15 conversas encontradas
2025-04-28 08:00:05 [INFO] 📨 [1/15] Coletando mensagens de: Cliente Metaltim
2025-04-28 08:00:06 [INFO] 📨 [2/15] Coletando mensagens de: Cliente Hi-Tech
...
2025-04-28 08:00:45 [INFO] ✅ Coleta WhatsApp concluída: 247 mensagens
```

---

## 🚀 Status da Implementação

| Componente | Status | Progresso |
|------------|--------|-----------|
| WhatsApp Collector | ✅ Completo | 100% |
| Discord Collector | ⏳ Pendente | 0% |
| Time Windows Utils | ✅ Completo | 100% |
| Claude Processor | ⏳ Pendente | 50% (prompts prontos) |
| Email Sender | ⏳ Pendente | 0% |
| Database Models | ✅ Completo | 100% |
| Scheduler | ⏳ Pendente | 0% |
| Main Orchestrator | ⏳ Pendente | 30% (estrutura pronta) |

**Progresso Geral**: ~40% ✨

---

**Próximo Passo Recomendado**: Implementar **Discord Collector** seguindo o mesmo padrão do WhatsApp Collector.
