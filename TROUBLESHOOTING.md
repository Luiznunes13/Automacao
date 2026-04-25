# Troubleshooting Guide - NCam Weekly Intelligence

## 🔍 Diagnóstico Rápido

### Comando Inicial de Diagnóstico

```powershell
# 1. Verificar ambiente Python
python --version
Get-Command python

# 2. Verificar ambiente virtual ativo
Get-Command python | Select-Object -ExpandProperty Source
# Deve apontar para: ...\Automacao\venv\Scripts\python.exe

# 3. Testar todas as integrações
python main.py --mode test

# 4. Ver estatísticas do banco
python utils.py stats

# 5. Verificar logs recentes
Get-Content ncam_intel.log -Tail 50
```

---

## 🔴 Problemas Comuns e Soluções

### 1. Erro ao Instalar Dependências

#### ❌ Problema
```
ERROR: Could not find a version that satisfies the requirement...
```

#### ✅ Solução
```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Limpar cache
pip cache purge

# Reinstalar
pip install -r requirements.txt --no-cache-dir
```

#### ❌ Problema (Windows)
```
error: Microsoft Visual C++ 14.0 or greater is required
```

#### ✅ Solução
1. Instale [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. Ou use wheels pré-compilados:
```powershell
pip install wheel
pip install -r requirements.txt
```

---

### 2. Evolution API (WhatsApp)

#### ❌ Problema: "Connection refused" ou timeout

**Possíveis Causas**:
- Evolution API não está rodando
- URL incorreta no `.env`
- Firewall bloqueando

#### ✅ Solução
```powershell
# 1. Verificar se API está respondendo
Invoke-WebRequest -Uri "http://localhost:8080/manager"

# 2. Se não responder, iniciar Evolution API
# Docker:
docker start evolution-api

# Standalone:
cd caminho/para/evolution-api
npm start
```

#### ❌ Problema: "401 Unauthorized"

**Causa**: API key inválida

#### ✅ Solução
```powershell
# 1. Verificar API key no painel Evolution
# 2. Atualizar no .env
notepad .env

# 3. Testar manualmente
$headers = @{"apikey"="SUA_CHAVE_AQUI"}
Invoke-WebRequest -Uri "http://localhost:8080/instance/connectionState/ncam_instance" -Headers $headers
```

#### ❌ Problema: "Instance not found"

**Causa**: Instância não foi criada ou nome incorreto

#### ✅ Solução
```powershell
# Criar instância via API
$body = @{
    instanceName = "ncam_instance"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/instance/create" `
    -Method POST `
    -Headers @{"apikey"="SUA_CHAVE"; "Content-Type"="application/json"} `
    -Body $body
```

#### ❌ Problema: "Instance not connected"

**Causa**: WhatsApp não foi conectado (QR Code)

#### ✅ Solução
1. Acesse: `http://localhost:8080/manager`
2. Localize sua instância
3. Clique em "Connect" / "QR Code"
4. Escaneie com WhatsApp (Dispositivos Conectados)

---

### 3. Discord Bot

#### ❌ Problema: Bot não conecta

**Erro típico**:
```
discord.errors.LoginFailure: Improper token has been passed
```

#### ✅ Solução
```powershell
# 1. Verificar token no .env (sem espaços, aspas, etc)
$env:DISCORD_BOT_TOKEN
# Deve ser: MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.AbCdEf.GhIjKlMnOpQrStUvWxYz...

# 2. Regenerar token se necessário:
# Discord Developer Portal → Bot → Reset Token

# 3. Atualizar .env
notepad .env
```

#### ❌ Problema: Bot conecta mas não vê mensagens

**Causa**: Intents desativadas

#### ✅ Solução
1. [Discord Developer Portal](https://discord.com/developers/applications)
2. Selecione sua aplicação
3. "Bot" → "Privileged Gateway Intents"
4. ✅ Ative:
   - **MESSAGE CONTENT INTENT** ⚠️ (essencial!)
   - Server Members Intent
   - Presence Intent
5. Salve
6. Reinicie o bot

#### ❌ Problema: "Forbidden" ao acessar canais

**Causa**: Bot sem permissões no servidor

#### ✅ Solução
```powershell
# 1. Verificar permissões do bot no servidor Discord:
# Configurações do Servidor → Funções → [Nome do Bot]

# 2. Permissões necessárias:
# ✅ Ver canais
# ✅ Ler histórico de mensagens
# ✅ Ler mensagens

# 3. Se necessário, re-adicione o bot com URL correta:
# Developer Portal → OAuth2 → URL Generator
# Scopes: bot
# Permissions: Read Message History, View Channels
```

#### ❌ Problema: Guild IDs não funcionam

**Causa**: IDs incorretos ou formato errado

#### ✅ Solução
```powershell
# 1. Ativar Developer Mode no Discord
# Configurações → Avançado → Modo de Desenvolvedor

# 2. Clicar com botão direito no servidor → Copiar ID

# 3. No .env (SEM ESPAÇOS, separado por vírgula):
DISCORD_GUILD_IDS=123456789012345678,987654321098765432
```

---

### 4. Claude AI (Anthropic)

#### ❌ Problema: "authentication_error"

**Erro**:
```json
{"error": {"type": "authentication_error", "message": "invalid x-api-key"}}
```

#### ✅ Solução
```powershell
# 1. Verificar API key
$env:ANTHROPIC_API_KEY
# Deve começar com: sk-ant-api03-...

# 2. Obter nova chave:
# https://console.anthropic.com/ → API Keys → Create Key

# 3. Atualizar .env
notepad .env

# 4. Testar manualmente
python
>>> from anthropic import Anthropic
>>> client = Anthropic(api_key="sk-ant-...")
>>> client.messages.create(model="claude-sonnet-4-20250514", max_tokens=100, messages=[{"role":"user","content":"Hi"}])
```

#### ❌ Problema: "rate_limit_error"

**Erro**:
```json
{"error": {"type": "rate_limit_error"}}
```

#### ✅ Solução
```powershell
# 1. Aguardar reset (geralmente 1 minuto)

# 2. Se recorrente, reduzir tokens:
# .env:
ANTHROPIC_MAX_TOKENS=2048

# 3. Verificar tier da conta:
# https://console.anthropic.com/ → Settings → Limits
```

#### ❌ Problema: "overloaded_error" ou "timeout"

**Causa**: API temporariamente sobrecarregada

#### ✅ Solução
```powershell
# Implementar retry (futuro):
# Por enquanto, executar novamente após alguns minutos
python main.py --mode manual
```

#### ❌ Problema: "insufficient_quota"

**Erro**:
```json
{"error": {"type": "insufficient_quota"}}
```

#### ✅ Solução
1. Acesse [Console Anthropic](https://console.anthropic.com/)
2. Settings → Billing
3. Adicione créditos / Configure método de pagamento
4. Verifique saldo disponível

---

### 5. E-mail (SMTP)

#### ❌ Problema: "Authentication failed" (Gmail)

**Causa**: Senha normal em vez de senha de app

#### ✅ Solução
```powershell
# 1. Acesse Google Account → Segurança
# 2. Ative Verificação em 2 etapas (se não estiver)
# 3. Vá em "Senhas de app"
# 4. Selecione "E-mail" e "Windows Computer"
# 5. Copie a senha gerada (16 caracteres sem espaços)
# 6. Cole no .env:
SMTP_PASSWORD=abcdefghijklmnop
```

#### ❌ Problema: "Connection refused" ou timeout

**Causa**: Porta bloqueada ou servidor incorreto

#### ✅ Solução
```powershell
# 1. Testar conectividade
Test-NetConnection -ComputerName smtp.gmail.com -Port 587

# 2. Se bloqueado, verificar firewall/antivírus

# 3. Alternativas de porta (Gmail):
SMTP_PORT=587  # TLS (recomendado)
SMTP_PORT=465  # SSL
```

#### ❌ Problema: "Recipient refused"

**Causa**: E-mail destinatário inválido

#### ✅ Solução
```powershell
# Verificar formato no .env:
EMAIL_RECIPIENT=email@dominio.com

# Para múltiplos (alguns provedores):
EMAIL_RECIPIENT=email1@dominio.com,email2@dominio.com
```

#### ❌ Problema: E-mail vai para spam

**Causa**: Falta de autenticação/reputação

#### ✅ Solução
1. **SPF/DKIM** (se usando domínio próprio)
2. **Testar com Gmail pessoal primeiro**
3. Marcar como "Não spam" nas primeiras vezes
4. Considerar serviço dedicado (SendGrid, Mailgun) para produção

---

### 6. Banco de Dados (SQLite)

#### ❌ Problema: "database is locked"

**Causa**: Múltiplas instâncias acessando simultaneamente

#### ✅ Solução
```powershell
# 1. Parar todas as instâncias
Get-Process python | Stop-Process

# 2. Se persistir, remover arquivo lock:
Remove-Item ncam_intel.db-journal -ErrorAction SilentlyContinue

# 3. Executar novamente
python main.py --mode manual
```

#### ❌ Problema: Banco corrompido

**Sintomas**: Erros ao query, dados inconsistentes

#### ✅ Solução
```powershell
# 1. Backup (se possível)
Copy-Item ncam_intel.db ncam_intel.db.backup

# 2. Verificar integridade
sqlite3 ncam_intel.db "PRAGMA integrity_check;"

# 3. Se corrompido, exportar dados:
sqlite3 ncam_intel.db ".dump" > dump.sql

# 4. Recriar banco
Remove-Item ncam_intel.db
python main.py --mode init
sqlite3 ncam_intel.db < dump.sql
```

---

### 7. Scheduler / APScheduler

#### ❌ Problema: Job não executa no horário

**Causa**: Timezone incorreta ou cron mal formatado

#### ✅ Solução
```powershell
# 1. Verificar timezone
$env:TZ
# Deve ser: America/Sao_Paulo

# 2. Verificar cron no .env
REPORT_SCHEDULE_CRON=0 8 * * MON
# Formato: minuto hora dia mês dia_semana

# 3. Testar cron online:
# https://crontab.guru/

# 4. Logs do scheduler
Get-Content ncam_intel.log | Select-String "scheduler"
```

#### ❌ Problema: Job executa múltiplas vezes

**Causa**: Múltiplas instâncias rodando

#### ✅ Solução
```powershell
# 1. Ver processos Python
Get-Process python

# 2. Matar duplicatas
Get-Process python | Select-Object -Skip 1 | Stop-Process

# 3. Executar apenas uma vez em modo scheduled
python main.py --mode scheduled
```

---

## 🛠️ Ferramentas de Diagnóstico

### Verificar Configurações Carregadas

```python
# test_config.py
from src.config import settings

print(f"Evolution API URL: {settings.evolution_api_url}")
print(f"Discord Guild IDs: {settings.guild_ids_list}")
print(f"Claude Model: {settings.anthropic_model}")
print(f"SMTP Host: {settings.smtp_host}")
print(f"Cron Schedule: {settings.report_schedule_cron}")
```

### Testar Conexões Individualmente

```python
# test_connections.py
import asyncio
from src.collectors import WhatsAppCollector, DiscordCollector
from src.processors import ClaudeProcessor
from src.delivery import EmailSender

async def test_all():
    # WhatsApp
    wa = WhatsAppCollector()
    print(f"WhatsApp: {await wa.test_connection()}")
    
    # Discord
    dc = DiscordCollector()
    print(f"Discord: {await dc.test_connection()}")
    await dc.stop_bot()
    
    # Claude
    claude = ClaudeProcessor()
    print(f"Claude: {claude.test_connection()}")
    
    # Email
    email = EmailSender()
    print(f"Email: {email.test_connection()}")

asyncio.run(test_all())
```

### Inspecionar Banco de Dados

```powershell
# Instalar SQLite CLI (se não tiver)
# https://www.sqlite.org/download.html

# Conectar
sqlite3 ncam_intel.db

# Comandos úteis:
.tables                          # Listar tabelas
.schema messages                 # Ver estrutura
SELECT COUNT(*) FROM messages;   # Total de mensagens
SELECT source, COUNT(*) FROM messages GROUP BY source;  # Por fonte
SELECT * FROM processed_windows; # Períodos processados
.quit                            # Sair
```

---

## 📋 Checklist de Problemas

Antes de abrir issue/pedir suporte, verifique:

- [ ] Ambiente virtual ativado (`.\venv\Scripts\Activate.ps1`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado (copiar de `.env.example`)
- [ ] Todas as API keys válidas e sem espaços extras
- [ ] Evolution API rodando e conectada (QR Code)
- [ ] Discord bot com intents corretas (MESSAGE CONTENT)
- [ ] Claude API com créditos disponíveis
- [ ] E-mail usando senha de app (não senha normal)
- [ ] Banco de dados inicializado (`python main.py --mode init`)
- [ ] Logs verificados (`Get-Content ncam_intel.log -Tail 100`)

---

## 🆘 Obter Ajuda

### 1. Logs Detalhados

```powershell
# Alterar nível de log para DEBUG
# .env:
LOG_LEVEL=DEBUG

# Executar e capturar logs
python main.py --mode test 2>&1 | Tee-Object -FilePath debug.log
```

### 2. Informações do Sistema

```powershell
# Versão Python
python --version

# Pacotes instalados
pip list

# Variáveis de ambiente (sanitizadas)
Get-Content .env | Select-String -Pattern "API_URL|_HOST|_PORT|TIMEZONE"
```

### 3. Testar APIs Manualmente

**Evolution API**:
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/instance/connectionState/ncam_instance" `
    -Headers @{"apikey"="SUA_CHAVE"}
```

**Claude API**:
```powershell
$headers = @{
    "x-api-key" = "sk-ant-..."
    "Content-Type" = "application/json"
    "anthropic-version" = "2023-06-01"
}

$body = @{
    model = "claude-sonnet-4-20250514"
    max_tokens = 100
    messages = @(@{role="user"; content="Hello"})
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "https://api.anthropic.com/v1/messages" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

---

## 🔄 Reset Completo (Last Resort)

Se tudo mais falhar:

```powershell
# 1. Backup de dados importantes
Copy-Item .env .env.backup
Copy-Item ncam_intel.db ncam_intel.db.backup

# 2. Remover ambiente virtual
Remove-Item -Recurse -Force venv

# 3. Limpar arquivos temporários
Remove-Item -Recurse -Force src\__pycache__
Remove-Item -Recurse -Force src\*\__pycache__
Remove-Item *.log
Remove-Item *.db

# 4. Recriar do zero
.\setup.ps1

# 5. Restaurar .env
Copy-Item .env.backup .env

# 6. Testar
python main.py --mode test
```

---

**Última atualização**: 25/04/2026
**Versão**: 1.0.0
