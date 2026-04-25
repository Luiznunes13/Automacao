# 📁 Estrutura do Projeto ncam-weekly-intel

```
ncam-weekly-intel/
├── .env.example                    # Template de variáveis de ambiente
├── .env                            # Suas credenciais (não commitar!)
├── .gitignore
├── requirements.txt                # Dependências Python
├── README.md                       # Documentação principal
├── QUICKSTART.md                   # Guia de início rápido
├── ARCHITECTURE.md                 # Arquitetura detalhada
├── EXAMPLES.md                     # Exemplos de uso
├── TROUBLESHOOTING.md              # Solução de problemas
├── CHANGELOG.md                    # Histórico de mudanças
├── INDEX.md                        # Índice da documentação
├── LICENSE
│
├── main.py                         # 🚀 Entry point + scheduler
├── utils.py                        # Utilitários de visualização DB
│
├── src/
│   ├── __init__.py
│   ├── config.py                   # ⚙️ Configurações centralizadas
│   │
│   ├── collectors/                 # 📥 Coletores de mensagens
│   │   ├── __init__.py
│   │   ├── base.py                 # Classe base abstrata
│   │   ├── whatsapp.py             # ✅ WhatsApp via Evolution API (COMPLETO)
│   │   └── discord_collector.py   # Discord via discord.py
│   │
│   ├── database/                   # 💾 Persistência
│   │   ├── __init__.py
│   │   ├── models.py               # Modelos SQLAlchemy
│   │   └── database.py             # Conexão e helpers
│   │
│   ├── processors/                 # 🧠 Processamento LLM
│   │   ├── __init__.py
│   │   ├── claude_processor.py     # Cliente Anthropic Claude
│   │   └── prompts.py              # ✅ Templates de prompt (ATUALIZADO)
│   │
│   ├── delivery/                   # 📧 Entrega de resumos
│   │   ├── __init__.py
│   │   └── email_sender.py         # Envio via SMTP
│   │
│   ├── scheduler/                  # ⏰ Agendamento
│   │   ├── __init__.py
│   │   └── jobs.py                 # APScheduler jobs
│   │
│   └── utils/                      # 🛠️ Utilitários
│       ├── __init__.py
│       └── time_windows.py         # ✅ Helpers de janelas de tempo (NOVO)
│
├── tests/                          # 🧪 Testes (opcional)
│   ├── __init__.py
│   ├── test_collectors.py
│   ├── test_processor.py
│   └── test_integration.py
│
├── logs/                           # 📝 Logs do sistema (gerado em runtime)
├── data/                           # Dados persistentes
│   └── ncam_intel.db               # Banco SQLite
│
└── setup.ps1                       # Script de setup automático Windows
```

---

## 📦 Componentes Principais

### 1. **WhatsApp Collector** (`src/collectors/whatsapp.py`) ✅
- **Status**: ✅ **COMPLETO E FUNCIONAL**
- **Features**:
  - ✅ Retry automático com backoff exponencial (3 tentativas)
  - ✅ Lista todos os chats disponíveis
  - ✅ Filtra mensagens por período (start_date, end_date)
  - ✅ Normaliza dados para formato padrão
  - ✅ Logging detalhado de progresso
  - ✅ Tratamento robusto de erros
  - ✅ Sessão HTTP persistente com urllib3.Retry

### 2. **Time Windows Helper** (`src/utils/time_windows.py`) ✅
- **Status**: ✅ **COMPLETO**
- **Funções**:
  - `get_last_work_week()` - Retorna última semana seg-sex
  - `get_week_range()` - Semana com offset
  - `format_period()` - Formata datas
  - `is_work_day()` - Verifica dia útil
  - `get_current_week_progress()` - Info da semana atual

### 3. **Claude Processor** (`src/processors/`)
- **Prompts atualizados** ✅
- **Output**: JSON estruturado com schema definido
- **Features**:
  - Análise por cliente
  - Correlação WhatsApp + Discord
  - Classificação de tom (positivo/neutro/atenção/crítico)
  - Pendências e próximos passos

---

## 🎯 Formato de Saída do LLM

```json
{
  "periodo": "21/04/2025 a 25/04/2025",
  "clientes": [
    {
      "nome": "Metaltim",
      "resumo": "Instalação do fanuc-driver na OKT20D. FOCAS2 respondendo via TCP.",
      "pendencias": [
        "Validar output MQTT em produção",
        "Agendar visita para verificar cabeamento"
      ],
      "tom": "positivo"
    }
  ],
  "pendencias_gerais": [
    "Definir estratégia para máquinas Mitsubishi da Hi-Tech"
  ],
  "destaques_internos": [
    "Yuri sugeriu avaliar DIME Connector como alternativa ao GRV"
  ],
  "proximos_passos_sugeridos": [
    "Segunda: checar status instalação Metaltim",
    "Agendar call Hi-Tech sobre Mitsubishi"
  ]
}
```

---

## 🚀 Como Usar

### Teste de Conexões
```powershell
python main.py test
```

### Coleta Manual (Última Semana)
```powershell
python main.py collect
```

### Executar Ciclo Completo
```powershell
python main.py run
```

### Iniciar Scheduler (Modo Daemon)
```powershell
python main.py schedule
```

### Ver Estatísticas do Banco
```powershell
python utils.py stats
```

---

## 🔧 Próximas Implementações

- [ ] Discord Collector (similar ao WhatsApp)
- [ ] Delivery via Email com template HTML
- [ ] Scheduler com APScheduler
- [ ] Testes unitários
- [ ] Docker Compose para deploy
- [ ] Dashboard web simples

---

## 📚 Documentação

- **README.md** - Visão geral e introdução
- **QUICKSTART.md** - Tutorial passo a passo
- **ARCHITECTURE.md** - Arquitetura técnica detalhada
- **EXAMPLES.md** - Exemplos de uso e outputs
- **TROUBLESHOOTING.md** - Problemas comuns e soluções
- **INDEX.md** - Índice completo da documentação

---

## 📝 Changelog

### v1.0.0 (Abril 2025) - Implementação Inicial
- ✅ WhatsApp Collector completo com retry
- ✅ Time Windows utilities
- ✅ Prompts Claude atualizados para JSON
- ✅ Estrutura modular do projeto
- ✅ Documentação completa

---

**Desenvolvido para NCam Tecnologia Industrial**
