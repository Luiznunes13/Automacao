# Changelog - NCam Weekly Intelligence

## [1.0.0] - 2026-04-25

### ✨ Features Iniciais

- ✅ Integração com WhatsApp via Evolution API
- ✅ Integração com Discord via discord.py bot
- ✅ Processamento inteligente com Anthropic Claude (Sonnet 4)
- ✅ Agendamento automático com APScheduler
- ✅ Entrega de resumos por e-mail (SMTP)
- ✅ Persistência em SQLite com SQLAlchemy
- ✅ Sistema de logging colorido
- ✅ Suporte a múltiplos modos de execução:
  - `--mode test`: Testar integrações
  - `--mode manual`: Execução manual com período customizado
  - `--mode scheduled`: Modo produção com agendamento
  - `--mode init`: Inicializar banco de dados
- ✅ Coletores modulares (WhatsApp e Discord)
- ✅ Controle de janelas processadas (evita duplicação)
- ✅ Exportação e utilitários de banco de dados

### 📋 Estrutura do Projeto

```
ncam-weekly-intel/
├── src/
│   ├── config.py              # Configurações centralizadas
│   ├── database/              # Models e conexão SQLAlchemy
│   ├── collectors/            # Coletores WhatsApp e Discord
│   ├── processors/            # Claude AI processor
│   ├── delivery/              # Email sender
│   └── scheduler/             # APScheduler jobs
├── main.py                    # Entry point
├── utils.py                   # Utilitários CLI
├── setup.ps1                  # Script de setup automatizado
├── requirements.txt           # Dependências Python
├── README.md                  # Documentação principal
├── QUICKSTART.md             # Guia rápido
└── CHANGELOG.md              # Este arquivo
```

### 🔧 Configurações

- Suporte a `.env` com python-dotenv
- Validação de configurações com Pydantic
- Timezone configurável (padrão: America/Sao_Paulo)
- Cron schedule customizável
- Filtros por guild/channel no Discord

### 📊 Database Schema

**messages**:
- Armazena mensagens de WhatsApp e Discord
- Campos comuns: timestamp, sender, content, chat
- Campos específicos por fonte (phone_number, guild_id, etc.)
- Flag de processamento

**processed_windows**:
- Registro de períodos processados
- Estatísticas (total de mensagens por fonte)
- Status de envio do resumo
- Notas e logs

### 🚀 Deploy

- Suporte a execução como serviço Windows (NSSM)
- Agendador de tarefas do Windows
- Script PowerShell de setup automatizado

### 📝 Prompts Claude

- System prompt contextualizado para NCam
- Template estruturado de resumo
- Formatação automática de mensagens
- Correlação WhatsApp ↔ Discord

### 🎯 Próximas Melhorias (Roadmap)

- [ ] Dashboard web para visualização
- [ ] Notificações Telegram/Slack
- [ ] Múltiplos destinatários de e-mail
- [ ] Filtros avançados por cliente
- [ ] Exportação de relatórios em PDF
- [ ] Análise de sentimento
- [ ] Detecção de urgência com ML
- [ ] Integração com CRM

---

**Versão inicial desenvolvida para NCam Monitoramento**
