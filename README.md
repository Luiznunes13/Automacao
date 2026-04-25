# NCam Weekly Intelligence

Sistema automatizado de resumo semanal integrando WhatsApp (Evolution API) e Discord para análise inteligente de comunicações com clientes e equipe.

## 🎯 Objetivo

Coletar mensagens do WhatsApp e Discord durante a semana (segunda a sexta) e gerar automaticamente toda segunda-feira às 08h um resumo estruturado usando Claude AI, entregue por e-mail.

## 🏢 Contexto de Negócio

**NCam** é uma empresa de monitoramento de máquinas CNC com dois canais principais:

- **WhatsApp**: Relacionamento direto com clientes (demandas, dúvidas, reclamações, visitas, instalações)
- **Discord**: Comunicação interna da equipe (decisões técnicas, pendências, contexto operacional)

O diferencial está no **cruzamento das fontes**: correlacionar demandas de clientes com discussões internas.

## 🛠️ Stack Técnica

- **Python 3.11+**
- **WhatsApp**: Evolution API (REST, self-hosted)
- **Discord**: discord.py (bot com permissão de leitura)
- **LLM**: Anthropic Claude (claude-sonnet-4-5)
- **Scheduler**: APScheduler
- **Database**: SQLite com SQLAlchemy
- **Config**: python-dotenv

## 📁 Estrutura do Projeto

```
ncam-weekly-intel/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configurações e variáveis de ambiente
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy models
│   │   └── database.py        # Conexão e sessões
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── base.py            # Interface abstrata
│   │   ├── whatsapp.py        # Evolution API collector
│   │   └── discord_collector.py  # Discord bot collector
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── claude_processor.py   # Integração com Anthropic
│   │   └── prompts.py            # Templates de prompts
│   ├── delivery/
│   │   ├── __init__.py
│   │   └── email_sender.py       # Envio de e-mails
│   └── scheduler/
│       ├── __init__.py
│       └── jobs.py               # APScheduler jobs
├── main.py                       # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Instalação

1. Clone o repositório e navegue até a pasta:
```bash
cd "c:\Users\44057824820\Documents\Automacao"
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
copy .env.example .env
# Edite o arquivo .env com suas credenciais
```

## ⚙️ Configuração

Edite o arquivo `.env` com as seguintes variáveis:

```env
# Evolution API (WhatsApp)
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua_api_key_aqui

# Discord Bot
DISCORD_BOT_TOKEN=seu_token_aqui
DISCORD_GUILD_IDS=id1,id2,id3

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# E-mail (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
EMAIL_RECIPIENT=destinatario@ncam.com

# Database
DATABASE_URL=sqlite:///./ncam_intel.db

# Scheduler
SCHEDULER_ENABLED=true
REPORT_SCHEDULE_CRON="0 8 * * MON"  # Segunda-feira às 08h
```

## 📊 Uso

### Execução Manual (teste)
```bash
python main.py --mode manual
```

### Execução Agendada (produção)
```bash
python main.py --mode scheduled
```

### Coletar apenas WhatsApp
```bash
python main.py --collector whatsapp
```

### Coletar apenas Discord
```bash
python main.py --collector discord
```

## 🔄 Fluxo de Funcionamento

1. **Coleta Contínua** (segunda a sexta):
   - WhatsApp Collector busca mensagens via Evolution API
   - Discord Bot monitora canais relevantes
   - Mensagens armazenadas no SQLite com timestamp e metadados

2. **Processamento Semanal** (segunda-feira 08h):
   - Agrupa mensagens da última semana
   - Envia para Claude AI com prompt estruturado
   - Claude correlaciona WhatsApp + Discord por cliente

3. **Entrega**:
   - Resumo formatado enviado por e-mail
   - Marca janela como processada no banco

## 🧠 Estrutura do Resumo

O resumo gerado conterá:

- **Visão Executiva**: principais destaques da semana
- **Por Cliente**:
  - Demandas recebidas (WhatsApp)
  - Discussões internas (Discord)
  - Ações pendentes
  - Prioridades identificadas
- **Alertas**: questões urgentes ou recorrentes
- **Métricas**: volume de mensagens, clientes ativos, tempo de resposta

## 📝 Exemplo de Saída

```markdown
# Resumo Semanal NCam — 21 a 25 de Abril de 2026

## 📌 Visão Executiva
- 15 clientes ativos com comunicação
- 3 instalações concluídas
- 2 problemas técnicos resolvidos
- 1 reclamação pendente (Cliente ABC)

## 🏢 Por Cliente

### Cliente ABC Indústria
**WhatsApp (5 mensagens)**:
- Reportou falha no sensor CNC linha 2
- Solicitou visita técnica urgente
- Confirmou instalação para dia 30/04

**Discord (equipe interna - 8 mensagens)**:
- Yuri identificou problema: cabo com mau contato
- Luiz agendou visita para 28/04
- Mariana preparou relatório de diagnóstico

**✅ Ações**:
- [ ] Visita técnica agendada (28/04 - Luiz)
- [ ] Enviar relatório pós-visita

---
[... outros clientes ...]
```

## 🛡️ Segurança

- Credenciais em `.env` (nunca comitar)
- `.gitignore` configurado
- Banco SQLite local com backup recomendado
- Tokens de API com permissões mínimas necessárias

## 🐛 Troubleshooting

### Discord bot não conecta
- Verifique se o token está correto
- Confirme permissões de leitura de histórico no servidor

### Evolution API retorna 401
- Valide a API key no arquivo `.env`
- Confirme que a Evolution API está rodando

### E-mail não envia
- Para Gmail, use senha de aplicativo (não a senha normal)
- Verifique firewall/antivírus bloqueando porta 587

## 📄 Licença

Proprietário - NCam Monitoramento

## 👥 Equipe

- **Luiz**: Técnico
- **Yuri**: Técnico
- **Mariana**: Analista
- **Guilherme**: Suporte

---

**Desenvolvido para NCam** 🚀
