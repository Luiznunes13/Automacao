# Arquitetura Técnica - NCam Weekly Intelligence

## 🏗️ Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINT (main.py)                     │
│  • Argument parsing                                              │
│  • Mode selection (test/manual/scheduled/init)                   │
│  • Database initialization                                       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
┌─────────────────────┐       ┌─────────────────────┐
│   CONFIG (config.py) │       │  DATABASE (SQLite)   │
│  • Environment vars  │       │  • Messages          │
│  • Pydantic Settings │       │  • ProcessedWindows  │
│  • Logging setup     │       │  • SQLAlchemy ORM    │
└─────────────────────┘       └─────────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
┌─────────────────────┐       ┌─────────────────────┐
│  SCHEDULER (APSch.) │       │  COLLECTORS          │
│  • Weekly job       │       │  • WhatsApp (REST)   │
│  • Cron triggers    │       │  • Discord (Bot)     │
│  • Async execution  │       │  • Base Interface    │
└─────────────────────┘       └─────────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  PROCESSOR (Claude AI)        │
            │  • Anthropic SDK              │
            │  • Prompt engineering         │
            │  • Message correlation        │
            └──────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  DELIVERY (Email)             │
            │  • SMTP sender                │
            │  • HTML rendering             │
            │  • Markdown to HTML           │
            └──────────────────────────────┘
```

---

## 📦 Módulos e Responsabilidades

### 1. `main.py` - Entry Point
**Responsabilidade**: Orquestração geral do sistema

- Parse de argumentos CLI
- Seleção de modo de execução
- Inicialização de componentes
- Tratamento de exceções top-level

**Dependências**:
- `src.config`
- `src.database`
- `src.scheduler`
- `src.collectors`
- `src.processors`
- `src.delivery`

---

### 2. `src/config.py` - Configurações
**Responsabilidade**: Gerenciamento centralizado de configurações

**Classes**:
```python
class Settings(BaseSettings):
    # Evolution API
    evolution_api_url: str
    evolution_api_key: str
    
    # Discord
    discord_bot_token: str
    discord_guild_ids: str
    
    # Anthropic
    anthropic_api_key: str
    anthropic_model: str
    
    # SMTP
    smtp_host: str
    smtp_user: str
    smtp_password: str
    
    # Scheduler
    scheduler_enabled: bool
    report_schedule_cron: str
```

**Features**:
- Validação com Pydantic
- Parsing de listas (guild_ids, channel_ids)
- Logging configurável (colorlog)
- Type hints completos

---

### 3. `src/database/` - Persistência

#### `models.py`
**Responsabilidade**: Definição de modelos SQLAlchemy

**Models**:

```python
class Message(Base):
    """Mensagem coletada (WhatsApp ou Discord)"""
    id: int
    source: SourceType (WHATSAPP | DISCORD)
    timestamp: datetime
    sender_name: str
    content: str
    # ... campos específicos

class ProcessedWindow(Base):
    """Período já processado"""
    id: int
    start_date: datetime
    end_date: datetime
    total_messages: int
    summary_sent: bool
```

#### `database.py`
**Responsabilidade**: Conexão e sessões

**Functions**:
```python
def init_db() -> None
    """Cria todas as tabelas"""

@contextmanager
def get_db() -> Session:
    """Context manager para transações"""
```

---

### 4. `src/collectors/` - Coleta de Dados

#### Interface Base (`base.py`)
```python
class BaseCollector(ABC):
    @abstractmethod
    async def collect_messages(start_date, end_date) -> List[dict]
    
    @abstractmethod
    async def test_connection() -> bool
```

#### WhatsApp Collector (`whatsapp.py`)
**Responsabilidade**: Integração com Evolution API

**Fluxo**:
1. `_get_all_chats()` - Busca conversas ativas
2. `_get_chat_messages()` - Para cada chat, busca mensagens no período
3. `_normalize_message()` - Normaliza formato Evolution → padrão

**Endpoints Evolution API**:
- `GET /chat/findChats/{instance}`
- `POST /message/find/{instance}`
- `GET /instance/connectionState/{instance}`

#### Discord Collector (`discord_collector.py`)
**Responsabilidade**: Bot Discord para histórico de mensagens

**Features**:
- discord.py bot com intents
- Async event loop
- Busca por período (`history()`)
- Filtro por guild/channel

**Intents Necessárias**:
- `message_content`
- `messages`
- `guilds`

---

### 5. `src/processors/` - Processamento com IA

#### Prompts (`prompts.py`)
**Responsabilidade**: Templates de prompts para Claude

**Constants**:
```python
SYSTEM_PROMPT: str
    """Contexto sobre NCam e role do assistente"""

SUMMARY_PROMPT_TEMPLATE: str
    """Template do prompt com variáveis {start_date}, {whatsapp_messages}, etc."""
```

**Functions**:
```python
def build_summary_prompt(...) -> str:
    """Monta prompt completo com dados reais"""

def format_messages_for_prompt(...) -> str:
    """Formata mensagens para inclusão no prompt"""
```

#### Claude Processor (`claude_processor.py`)
**Responsabilidade**: Integração com Anthropic API

**Methods**:
```python
async def generate_summary(...) -> str:
    """Gera resumo usando Claude"""

async def generate_summary_streaming(...) -> str:
    """Versão com streaming (opcional)"""
```

**API Details**:
- Model: `claude-sonnet-4-20250514`
- Max tokens: 4096 (configurável)
- System prompt + User prompt
- Retorno: Markdown formatado

---

### 6. `src/delivery/` - Entrega de Resumos

#### Email Sender (`email_sender.py`)
**Responsabilidade**: Envio de e-mails formatados

**Methods**:
```python
async def send_summary(...) -> bool:
    """Envia resumo por e-mail"""

def _markdown_to_html(...) -> str:
    """Converte Markdown → HTML estilizado"""
```

**Features**:
- MIME multipart (text + HTML)
- CSS inline para compatibilidade
- Parser básico de Markdown
- Fallback para texto plano

---

### 7. `src/scheduler/` - Agendamento

#### Jobs (`jobs.py`)
**Responsabilidade**: Tarefas agendadas

**Main Job**:
```python
async def generate_weekly_summary():
    """
    1. Calcula período (segunda a sexta anterior)
    2. Coleta mensagens
    3. Salva no banco
    4. Processa com Claude
    5. Envia por e-mail
    6. Registra janela processada
    """
```

**Scheduler**:
- APScheduler AsyncIOScheduler
- CronTrigger para agendamento
- Timezone-aware (configurável)

---

## 🔄 Fluxo de Dados Completo

### Execução Manual (`--mode manual`)

```
User executes
     │
     ▼
main.py (manual_run)
     │
     ▼
WeeklyScheduler.generate_weekly_summary()
     │
     ├─→ Define período (últimos N dias)
     │
     ├─→ WhatsAppCollector.collect_messages()
     │   │
     │   ├─→ Evolution API: GET /chat/findChats
     │   ├─→ For each chat: POST /message/find
     │   └─→ Normalize messages
     │
     ├─→ DiscordCollector.collect_messages()
     │   │
     │   ├─→ Bot.start()
     │   ├─→ For each guild/channel: history()
     │   └─→ Normalize messages
     │
     ├─→ Save to SQLite (Message table)
     │
     ├─→ ClaudeProcessor.generate_summary()
     │   │
     │   ├─→ Build prompt from messages
     │   ├─→ Anthropic API: POST /messages
     │   └─→ Return Markdown summary
     │
     ├─→ EmailSender.send_summary()
     │   │
     │   ├─→ Convert Markdown → HTML
     │   ├─→ SMTP send
     │   └─→ Return success/failure
     │
     └─→ Save ProcessedWindow to SQLite
```

### Execução Agendada (`--mode scheduled`)

```
main.py (scheduled_run)
     │
     ▼
WeeklyScheduler.start()
     │
     ├─→ APScheduler.add_job(
     │       func=generate_weekly_summary,
     │       trigger=CronTrigger("0 8 * * MON")
     │   )
     │
     └─→ Keep running (async loop)

Every Monday 08:00:
     │
     ▼
generate_weekly_summary()
     │
     └─→ [Same flow as manual mode]
```

---

## 🗄️ Estrutura do Banco de Dados

### Tabela: `messages`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER PK | Auto-increment |
| `source` | ENUM | 'whatsapp' ou 'discord' |
| `source_id` | VARCHAR(255) | ID da mensagem na origem |
| `timestamp` | DATETIME | Data/hora da mensagem |
| `sender_id` | VARCHAR(255) | Phone ou Discord user ID |
| `sender_name` | VARCHAR(255) | Nome do remetente |
| `chat_id` | VARCHAR(255) | Chat/channel ID |
| `chat_name` | VARCHAR(255) | Nome do chat/canal |
| `content` | TEXT | Conteúdo da mensagem |
| `phone_number` | VARCHAR(50) | WhatsApp only |
| `guild_id` | VARCHAR(100) | Discord only |
| `processed` | BOOLEAN | Flag de processamento |
| `processed_at` | DATETIME | Quando foi processada |

**Índices**:
- `source` (filtros)
- `source_id` (unicidade)
- `timestamp` (queries por período)
- `chat_id` (agrupamento)
- `processed` (queries de pendentes)

### Tabela: `processed_windows`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER PK | Auto-increment |
| `start_date` | DATETIME | Início do período |
| `end_date` | DATETIME | Fim do período |
| `total_messages` | INTEGER | Total processado |
| `whatsapp_messages` | INTEGER | Apenas WhatsApp |
| `discord_messages` | INTEGER | Apenas Discord |
| `summary_sent` | BOOLEAN | Se foi enviado |
| `summary_recipient` | VARCHAR(255) | Para quem |
| `notes` | TEXT | Logs/erros |
| `processed_at` | DATETIME | Timestamp |

---

## 🔐 Segurança

### Secrets Management
- ✅ `.env` nunca versionado (`.gitignore`)
- ✅ `.env.example` versionado (sem valores reais)
- ✅ Pydantic valida tipos e obrigatoriedade
- ⚠️ Para produção: considerar vault (HashiCorp, AWS Secrets)

### API Keys
- WhatsApp: API key custom (Evolution API)
- Discord: Bot token OAuth2
- Claude: API key Anthropic
- SMTP: App password (não senha normal)

### Permissões Discord Bot
- ✅ Read Message History (mínimo necessário)
- ✅ Read Messages/View Channels
- ❌ Não precisa de Write/Manage

---

## ⚡ Performance

### Otimizações Implementadas

1. **Async/Await**: 
   - Collectors assíncronos
   - Não bloqueante

2. **Batch Processing**:
   - Salva todas mensagens em uma transação
   - Bulk insert no SQLite

3. **Connection Pooling**:
   - SQLAlchemy sessionmaker
   - Context managers para cleanup

4. **Lazy Loading**:
   - Discord bot inicia apenas quando necessário
   - Fecha após coleta

### Limitações Conhecidas

- **Evolution API**: Rate limit depende da instância
- **Discord API**: 50 msg/sec (não atingível normalmente)
- **Claude API**: Tier-based (verificar console)
- **SQLite**: Lock em writes (não problema para este uso)

---

## 🧪 Testabilidade

### Testes Implementados

- `--mode test`: Testa todas as integrações
- Collectors têm `test_connection()`
- SMTP testável sem envio real

### Testes Futuros (Recomendados)

```python
# tests/test_collectors.py
async def test_whatsapp_normalize_message():
    """Testa normalização de mensagens"""

# tests/test_processor.py
async def test_claude_prompt_building():
    """Testa construção de prompts"""

# tests/test_scheduler.py
def test_period_calculation():
    """Testa cálculo de períodos"""
```

Framework recomendado: **pytest** + **pytest-asyncio**

---

## 📈 Escalabilidade

### Cenário Atual
- ✅ Até ~1000 mensagens/semana
- ✅ 1-10 servidores Discord
- ✅ SQLite suficiente

### Scale Up (se necessário)

1. **Mais mensagens** (10k+/semana):
   - Migrar SQLite → PostgreSQL
   - Adicionar indices otimizados
   - Considerar particionamento por data

2. **Mais servidores Discord** (50+):
   - Sharding de bots (múltiplos tokens)
   - Queue system (Celery/RQ)

3. **Múltiplos usuários**:
   - Multi-tenancy no banco
   - API REST + frontend
   - Authentication/Authorization

---

## 🔧 Manutenibilidade

### Code Quality
- ✅ Type hints em todo código
- ✅ Docstrings em funções públicas
- ✅ Logging estruturado
- ✅ Separação de concerns (módulos)

### Documentação
- ✅ README.md principal
- ✅ QUICKSTART.md para setup
- ✅ EXAMPLES.md para casos de uso
- ✅ ARCHITECTURE.md (este arquivo)
- ✅ Inline comments em código complexo

### Versionamento
- ✅ Git-friendly (.gitignore configurado)
- ✅ CHANGELOG.md para rastrear mudanças
- ⚠️ Adicionar tags de versão no Git

---

## 🚀 Deploy

### Ambiente de Desenvolvimento
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### Ambiente de Produção (Windows Service)

**Opção 1: NSSM**
```powershell
nssm install NcamWeeklyIntel "C:\path\to\venv\Scripts\python.exe" "C:\path\to\main.py --mode scheduled"
```

**Opção 2: Task Scheduler**
- Gatilho: Ao iniciar sistema
- Ação: `python main.py --mode scheduled`

### Monitoramento
- Logs: `ncam_intel.log`
- Banco: `ncam_intel.db` (query com SQL)
- Utils: `python utils.py stats`

---

## 📊 Métricas e Observabilidade

### Métricas Disponíveis

```python
# utils.py stats
- Total de mensagens
- Breakdown por fonte
- Taxa de processamento
- Períodos processados
- Taxa de envio de e-mails
```

### Logs Estruturados

```
[timestamp] - [logger_name] - [level] - [message]
2026-04-25 08:00:15 - WeeklyScheduler - INFO - Iniciando coleta semanal
```

### Futura Integração (Recomendada)
- Prometheus + Grafana (métricas)
- ELK Stack (logs centralizados)
- Sentry (error tracking)

---

**Documentação Técnica v1.0 - NCam Weekly Intelligence**
