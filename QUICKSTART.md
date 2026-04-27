# NCam Weekly Intelligence - Quick Start Guide

## 📋 Passos para Começar


### 1. Instalar Dependências

**Recomendado:** Use o Python do Anaconda/Miniconda para evitar travamentos do pip.

```powershell
# (Opção 1 - Anaconda, mais rápido e confiável)
conda create -n ncam python=3.10 -y
conda activate ncam
pip install -r requirements.txt

# (Opção 2 - venv, pode ser lento)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o `pip install -r requirements.txt` travar, instale só os pacotes essenciais:

```powershell
pip install python-dotenv openai discord.py aiohttp requests pydantic colorlog pytz python-dateutil SQLAlchemy APScheduler
```

> **Nota:** O pacote `anthropic` não é necessário para rodar com Z.ai/GLM, pois o código usa a API OpenAI compatível.

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais:

```powershell
Copy-Item .env.example .env
```

Depois edite o arquivo `.env` com suas chaves e configurações reais.

### 3. Obter Credenciais Necessárias

#### 🟢 WhatsApp (Evolution API)

1. **Instalar Evolution API** (se ainda não tiver):
   - Docker: https://doc.evolution-api.com/install/docker
   - Standalone: https://doc.evolution-api.com/install/standalone

2. **Criar uma instância**:
   ```bash
   POST http://localhost:8080/instance/create
   {
     "instanceName": "ncam_instance"
   }
   ```

3. **Obter API Key** no painel da Evolution API

4. **Conectar WhatsApp**: Escanear QR Code pelo app

#### 💙 Discord Bot

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Vá em "Bot" → "Add Bot"
4. Copie o **Token** (DISCORD_BOT_TOKEN)
5. Ative as **Intents**:
   - ✅ Intenção de conteúdo da mensagem (Message Content Intent)
   - ✅ Intenção dos membros do servidor (Server Members Intent)
6. Vá em "OAuth2" → "URL Generator":
   - Scopes: `bot`
   - Permissions: `Read Message History`, `Read Messages/View Channels`
7. Use a URL gerada para adicionar o bot aos servidores

8. **Obter IDs dos Servidores**:
   - Ative o "Developer Mode" no Discord (Configurações → Avançado)
   - Clique com botão direito no servidor → "Copiar ID"

#### 🤖 Z.ai / Claude / GLM

1. Acesse [Z.ai](https://z.ai/) ou [Anthropic Console](https://console.anthropic.com/)
2. Gere uma chave de API compatível com OpenAI (ANTHROPIC_API_KEY)
3. Configure o modelo desejado (ex: glm-4.5-flash)
4. **Importante**: Adicione créditos à conta se necessário

#### 📧 E-mail (Gmail)

1. Acesse sua conta Google
2. Vá em "Segurança" → "Verificação em duas etapas" (ative se ainda não estiver)
3. Vá em "Senhas de app"
4. Gere uma senha para "E-mail" → "Windows Computer"

---

> **Dica:** Se o pip travar, tente rodar o comando de instalação dos pacotes essenciais individualmente, ou use o Anaconda/Miniconda para evitar problemas de rede e dependências.
5. Use essa senha no SMTP_PASSWORD (não use sua senha normal!)

### 4. Testar Integrações

```powershell
python main.py --mode test
```

Você deve ver:
```
✅ WhatsApp OK
✅ Discord OK
✅ Claude AI OK
✅ SMTP OK
```

### 5. Executar Modo Manual (Teste)

Coletar mensagens dos últimos 7 dias e gerar resumo:

```powershell
python main.py --mode manual
```

Coletar apenas WhatsApp:
```powershell
python main.py --mode manual --collector whatsapp
```

Coletar apenas Discord:
```powershell
python main.py --mode manual --collector discord
```

### 6. Modo Produção (Agendado)

Para rodar continuamente com agendamento automático:

```powershell
python main.py --mode scheduled
```

O sistema ficará rodando e gerará resumos automaticamente toda segunda-feira às 08h.

---

## 🔧 Troubleshooting Comum

### ❌ "ModuleNotFoundError"
```powershell
# Certifique-se que o ambiente virtual está ativo
.\venv\Scripts\Activate.ps1

# Reinstale as dependências
pip install -r requirements.txt
```

### ❌ Evolution API não conecta

- Verifique se a API está rodando: `http://localhost:8080/manager`
- Teste no navegador ou Postman antes
- Confirme que a instância está conectada (QR Code escaneado)

### ❌ Discord bot não vê mensagens

- Verifique as **Intents** no Developer Portal
- Confirme que o bot foi adicionado aos servidores corretos
- Verifique as permissões do bot nos canais

### ❌ Claude API retorna erro 401

- Valide a API Key no console da Anthropic
- Verifique se há créditos disponíveis na conta
- Teste a chave diretamente: https://console.anthropic.com/

### ❌ E-mail não envia (Gmail)

- Use **senha de aplicativo**, não a senha normal
- Verifique se a verificação em duas etapas está ativa
- Teste com outro cliente SMTP se necessário

---

## 📊 Estrutura do Banco de Dados

O sistema cria automaticamente um arquivo `ncam_intel.db` (SQLite) com:

- **messages**: Todas as mensagens coletadas
- **processed_windows**: Registro de períodos já processados

Você pode visualizar com ferramentas como:
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLite Viewer](https://inloop.github.io/sqlite-viewer/)

---

## 🔄 Fluxo de Execução

```
┌─────────────────────────────────────────────────────────┐
│  SEGUNDA-FEIRA 08:00                                    │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   1. Definir Período          │
         │   (Segunda a Sexta anterior)  │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   2. Coletar Mensagens        │
         │   • WhatsApp (Evolution API)  │
         │   • Discord (discord.py)      │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   3. Salvar no Banco (SQLite) │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   4. Processar com Claude AI  │
         │   • Correlacionar fontes      │
         │   • Identificar clientes      │
         │   • Gerar resumo estruturado  │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   5. Enviar por E-mail        │
         │   (Formato HTML + Markdown)   │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   6. Registrar Processamento  │
         │   (Evitar duplicação)         │
         └───────────────────────────────┘
```

---

## 🎯 Próximos Passos

1. ✅ Instalar e configurar todas as integrações
2. ✅ Executar `--mode test` para validar
3. ✅ Fazer um teste manual com `--mode manual`
4. ✅ Verificar o resumo recebido por e-mail
5. ✅ Ajustar prompts em `src/processors/prompts.py` se necessário
6. ✅ Colocar em produção com `--mode scheduled`
7. ✅ (Opcional) Configurar como serviço do Windows

---

## 🚀 Rodar como Serviço (Produção)

### Opção 1: NSSM (Non-Sucking Service Manager)

```powershell
# Baixar NSSM: https://nssm.cc/download

# Instalar como serviço
nssm install NcamWeeklyIntel "C:\Users\44057824820\Documents\Automacao\venv\Scripts\python.exe" "C:\Users\44057824820\Documents\Automacao\main.py --mode scheduled"

# Iniciar serviço
nssm start NcamWeeklyIntel
```

### Opção 2: Task Scheduler

1. Abra o "Agendador de Tarefas"
2. Criar Tarefa Básica
3. Gatilho: Ao iniciar o sistema
4. Ação: Iniciar programa
   - Programa: `C:\Users\44057824820\Documents\Automacao\venv\Scripts\python.exe`
   - Argumentos: `main.py --mode scheduled`
   - Iniciar em: `C:\Users\44057824820\Documents\Automacao`

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs em `ncam_intel.log`
2. Execute em modo teste: `python main.py --mode test`
3. Consulte a documentação das APIs:
   - [Evolution API](https://doc.evolution-api.com/)
   - [Discord.py](https://discordpy.readthedocs.io/)
   - [Anthropic Claude](https://docs.anthropic.com/)

---

**Desenvolvido para NCam Monitoramento** 🏭
