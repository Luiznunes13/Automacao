# 📚 Índice de Documentação - NCam Weekly Intelligence

## 🎯 Visão Geral do Projeto

**NCam Weekly Intelligence** é um sistema automatizado que integra comunicações do WhatsApp (via Evolution API) e Discord (via bot) para gerar resumos semanais inteligentes usando Claude AI da Anthropic, entregues por e-mail.

---

## 📖 Guias de Documentação

### Para Começar ⚡

1. **[README.md](README.md)** - Visão geral e introdução
   - Contexto de negócio
   - Stack tecnológica
   - Estrutura do projeto
   - Instruções básicas

2. **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido de instalação
   - Passo a passo de setup
   - Obtenção de credenciais
   - Testes iniciais
   - Como rodar em produção

3. **[setup.ps1](setup.ps1)** - Script automatizado de instalação
   - Execução: `.\setup.ps1`

### Para Desenvolvedores 🛠️

4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura técnica completa
   - Diagrama de componentes
   - Fluxo de dados
   - Estrutura do banco de dados
   - Performance e escalabilidade
   - Segurança

5. **[EXAMPLES.md](EXAMPLES.md)** - Exemplos práticos de uso
   - Casos de uso comuns
   - Customizações
   - Debug e logs
   - Configurações avançadas

6. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solução de problemas
   - Diagnóstico rápido
   - Problemas comuns por componente
   - Ferramentas de debug
   - Reset completo

### Referência 📋

7. **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões
   - Features da v1.0.0
   - Roadmap futuro

8. **[LICENSE](LICENSE)** - Licença MIT
   - Termos de uso
   - Nota sobre privacidade e LGPD

---

## 🗂️ Estrutura de Arquivos do Projeto

```
ncam-weekly-intel/
│
├── 📄 Documentação Principal
│   ├── README.md                    # Visão geral
│   ├── INDEX.md                     # Este arquivo
│   ├── QUICKSTART.md               # Guia rápido
│   ├── ARCHITECTURE.md             # Arquitetura técnica
│   ├── EXAMPLES.md                 # Exemplos práticos
│   ├── TROUBLESHOOTING.md          # Solução de problemas
│   ├── CHANGELOG.md                # Histórico de versões
│   └── LICENSE                     # Licença MIT
│
├── ⚙️ Configuração
│   ├── .env.example                # Template de variáveis de ambiente
│   ├── .gitignore                  # Arquivos ignorados pelo Git
│   ├── requirements.txt            # Dependências Python
│   └── setup.ps1                   # Script de instalação automatizada
│
├── 🚀 Executáveis
│   ├── main.py                     # Entry point principal
│   └── utils.py                    # Utilitários CLI
│
└── 📦 Código Fonte (src/)
    ├── __init__.py
    ├── config.py                   # Configurações centralizadas
    │
    ├── database/                   # Persistência (SQLite)
    │   ├── __init__.py
    │   ├── models.py              # SQLAlchemy models
    │   └── database.py            # Conexão e sessões
    │
    ├── collectors/                 # Coleta de mensagens
    │   ├── __init__.py
    │   ├── base.py                # Interface abstrata
    │   ├── whatsapp.py            # Evolution API
    │   └── discord_collector.py    # Discord bot
    │
    ├── processors/                 # Processamento com IA
    │   ├── __init__.py
    │   ├── prompts.py             # Templates de prompts
    │   └── claude_processor.py     # Anthropic Claude
    │
    ├── delivery/                   # Entrega de resumos
    │   ├── __init__.py
    │   └── email_sender.py        # SMTP
    │
    └── scheduler/                  # Agendamento automático
        ├── __init__.py
        └── jobs.py                # APScheduler
```

---

## 🔧 Principais Comandos

### Setup Inicial
```powershell
# Instalação automatizada
.\setup.ps1

# Ou manual:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edite o .env com suas credenciais
python main.py --mode init
```

### Testes e Validação
```powershell
# Testar todas as integrações
python main.py --mode test

# Ver estatísticas do banco
python utils.py stats

# Listar mensagens recentes
python utils.py recent 20
```

### Execução
```powershell
# Manual (teste com últimos 7 dias)
python main.py --mode manual

# Manual com período customizado
python main.py --mode manual --days 3

# Agendado (produção)
python main.py --mode scheduled

# Coletar apenas uma fonte
python main.py --collector whatsapp
python main.py --collector discord
```

### Manutenção
```powershell
# Ver períodos processados
python utils.py windows

# Exportar dados para CSV
python utils.py export mensagens.csv

# Limpar mensagens antigas (30 dias)
python utils.py clear 30

# Ver logs
Get-Content ncam_intel.log -Tail 50 -Wait
```

---

## 🌐 Recursos Externos

### APIs e Serviços Integrados

- **Evolution API (WhatsApp)**
  - 📚 [Documentação](https://doc.evolution-api.com/)
  - 🔧 [GitHub](https://github.com/EvolutionAPI/evolution-api)
  - 💡 [Instalação](https://doc.evolution-api.com/install/docker)

- **Discord Bot (discord.py)**
  - 📚 [Documentação](https://discordpy.readthedocs.io/)
  - 🔧 [Developer Portal](https://discord.com/developers/applications)
  - 💡 [Guia de Bots](https://discordpy.readthedocs.io/en/stable/discord.html)

- **Anthropic Claude AI**
  - 📚 [Documentação](https://docs.anthropic.com/)
  - 🔧 [Console](https://console.anthropic.com/)
  - 💡 [API Reference](https://docs.anthropic.com/claude/reference/)

### Ferramentas Auxiliares

- **Python 3.11+**: https://www.python.org/downloads/
- **VS Code**: https://code.visualstudio.com/
- **Git**: https://git-scm.com/
- **SQLite Browser**: https://sqlitebrowser.org/
- **Postman** (testar APIs): https://www.postman.com/

---

## 📞 Fluxo de Suporte

### Encontrou um problema?

1. **Consulte documentação relevante**:
   - Problema de instalação → [QUICKSTART.md](QUICKSTART.md)
   - Erro em execução → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Dúvida sobre funcionamento → [ARCHITECTURE.md](ARCHITECTURE.md)
   - Exemplos de uso → [EXAMPLES.md](EXAMPLES.md)

2. **Diagnóstico inicial**:
   ```powershell
   python main.py --mode test
   python utils.py stats
   Get-Content ncam_intel.log -Tail 100
   ```

3. **Checklist**:
   - [ ] Ambiente virtual ativado?
   - [ ] Dependências instaladas?
   - [ ] `.env` configurado?
   - [ ] APIs funcionando?
   - [ ] Logs verificados?

4. **Soluções comuns**:
   - Ver seção específica em [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Executar reset: `.\setup.ps1`

---

## 🎓 Tutoriais por Persona

### Sou Gestor/Usuário Final
**Objetivo**: Receber resumos semanais

1. Leia: [README.md](README.md) → [QUICKSTART.md](QUICKSTART.md)
2. Execute: `.\setup.ps1`
3. Configure: `.env` (peça ajuda da TI para APIs)
4. Teste: `python main.py --mode test`
5. Rode: `python main.py --mode scheduled`

### Sou Desenvolvedor
**Objetivo**: Entender, modificar, estender o código

1. Leia: [ARCHITECTURE.md](ARCHITECTURE.md) → [EXAMPLES.md](EXAMPLES.md)
2. Explore: Código em `src/`
3. Customize: Prompts em `src/processors/prompts.py`
4. Teste: `python main.py --mode manual`
5. Debug: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Sou DevOps/SysAdmin
**Objetivo**: Deployar em produção

1. Leia: [QUICKSTART.md](QUICKSTART.md) (seção "Rodar como Serviço")
2. Setup: Windows Service (NSSM) ou Task Scheduler
3. Monitore: Logs em `ncam_intel.log`
4. Backup: `ncam_intel.db` (SQLite)
5. Troubleshoot: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🗺️ Roadmap e Evolução

### Versão Atual: 1.0.0
- ✅ Integração WhatsApp + Discord
- ✅ Processamento com Claude AI
- ✅ Agendamento automático
- ✅ Entrega por e-mail

### Próximas Versões
- 📋 Ver detalhes em [CHANGELOG.md](CHANGELOG.md)
- 💡 Sugestões? Abra issue no repositório

---

## 📄 Licença e Conformidade

- **Licença**: MIT (ver [LICENSE](LICENSE))
- **LGPD**: Responsabilidade do usuário garantir conformidade
- **APIs**: Respeitar termos de serviço de cada plataforma

---

## 🙏 Créditos

**Desenvolvido para**: NCam Monitoramento  
**Stack**: Python, SQLAlchemy, discord.py, Anthropic Claude, APScheduler  
**Versão**: 1.0.0  
**Data**: Abril 2026  

---

**Navegue pela documentação usando os links acima** 👆

**Início rápido**: [QUICKSTART.md](QUICKSTART.md)
