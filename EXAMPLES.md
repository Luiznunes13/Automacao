# Exemplos Práticos - NCam Weekly Intelligence

## 📖 Casos de Uso

### 1. Setup Inicial Completo

```powershell
# 1. Executar setup automatizado
.\setup.ps1

# 2. Editar arquivo .env
notepad .env

# 3. Testar todas as integrações
python main.py --mode test

# Saída esperada:
# ✅ WhatsApp OK
# ✅ Discord OK
# ✅ Claude AI OK
# ✅ SMTP OK
```

### 2. Coleta Manual de Teste

```powershell
# Coletar últimos 7 dias e gerar resumo
python main.py --mode manual

# Coletar últimos 3 dias
python main.py --mode manual --days 3

# Apenas WhatsApp (sem gerar resumo)
python main.py --mode manual --collector whatsapp

# Apenas Discord
python main.py --mode manual --collector discord
```

### 3. Verificar Banco de Dados

```powershell
# Ver estatísticas
python utils.py stats

# Saída:
# Total de Mensagens: 150
#   • WhatsApp: 80
#   • Discord: 70
# Mensagens Processadas: 150/150
# Períodos Processados: 1
#   • Resumos enviados: 1

# Listar últimas 20 mensagens
python utils.py recent 20

# Últimas 10 do WhatsApp apenas
python utils.py whatsapp 10

# Últimas 15 do Discord
python utils.py discord 15

# Ver períodos processados
python utils.py windows
```

### 4. Exportação de Dados

```powershell
# Exportar todas as mensagens para CSV
python utils.py export

# Exportar para arquivo específico
python utils.py export mensagens_abril.csv
```

### 5. Manutenção

```powershell
# Limpar mensagens antigas (30 dias)
python utils.py clear

# Limpar mensagens com mais de 60 dias
python utils.py clear 60
```

---

## 🔧 Configurações Avançadas

### Customizar Horário do Resumo

Edite no `.env`:

```env
# Toda segunda-feira às 08h (padrão)
REPORT_SCHEDULE_CRON=0 8 * * MON

# Toda sexta-feira às 17h
REPORT_SCHEDULE_CRON=0 17 * * FRI

# Diariamente às 09h
REPORT_SCHEDULE_CRON=0 9 * * *

# A cada 6 horas
REPORT_SCHEDULE_CRON=0 */6 * * *
```

Formato CRON: `minuto hora dia mês dia_da_semana`

### Filtrar Canais Discord Específicos

```env
# Deixe vazio para todos os canais
DISCORD_CHANNEL_IDS=

# Ou especifique IDs separados por vírgula
DISCORD_CHANNEL_IDS=123456789,987654321,111222333
```

Como obter IDs:
1. Ative Developer Mode no Discord (Configurações → Avançado)
2. Clique com botão direito no canal → Copiar ID

### Múltiplos Servidores Discord

```env
# Múltiplos servers
DISCORD_GUILD_IDS=123456789,987654321,555666777
```

---

## 📧 Personalizar E-mail

### Template HTML Customizado

Edite `src/delivery/email_sender.py`, método `_markdown_to_html()`.

### Múltiplos Destinatários

Opção 1 - Separar por vírgula no `.env`:
```env
EMAIL_RECIPIENT=gerente@ncam.com,suporte@ncam.com,ti@ncam.com
```

Opção 2 - Usar lista de distribuição no seu servidor de e-mail.

---

## 🤖 Ajustar Prompts do Claude

### Editar System Prompt

Arquivo: `src/processors/prompts.py`

```python
SYSTEM_PROMPT = """Você é um assistente especializado em análise de comunicações empresariais da NCam...

[CUSTOMIZE AQUI]

Sua tarefa é analisar mensagens de duas fontes:
...
"""
```

### Customizar Estrutura do Resumo

Edite `SUMMARY_PROMPT_TEMPLATE` no mesmo arquivo para:

- Adicionar seções (ex: "Métricas de SLA")
- Remover seções desnecessárias
- Mudar formato (JSON, HTML, etc.)
- Ajustar nível de detalhe

Exemplo - Adicionar seção de alertas críticos:

```python
## 🚨 ALERTAS CRÍTICOS

**Problemas de Alta Prioridade**:
- [Liste problemas que requerem atenção imediata]

**Clientes em Risco**:
- [Identifique clientes com múltiplas reclamações]
```

---

## 🔍 Debug e Logs

### Nível de Log

Edite `.env`:

```env
# DEBUG: Muito verboso (desenvolvimento)
LOG_LEVEL=DEBUG

# INFO: Informativo (padrão)
LOG_LEVEL=INFO

# WARNING: Apenas avisos
LOG_LEVEL=WARNING

# ERROR: Apenas erros
LOG_LEVEL=ERROR
```

### Visualizar Logs

```powershell
# Tempo real
Get-Content ncam_intel.log -Wait -Tail 50

# Filtrar erros
Select-String -Path ncam_intel.log -Pattern "ERROR"

# Últimas 100 linhas
Get-Content ncam_intel.log -Tail 100
```

---

## 🎯 Casos de Uso Específicos

### Caso 1: Resumo Emergencial Fora de Horário

```powershell
# Gerar resumo dos últimos 2 dias agora
python main.py --mode manual --days 2
```

### Caso 2: Testar Apenas Coleta (sem Claude/E-mail)

```powershell
# Ver quantas mensagens seriam coletadas
python main.py --collector whatsapp
python main.py --collector discord
```

### Caso 3: Reprocessar Período Específico

```python
# Edite temporariamente src/scheduler/jobs.py
# Método generate_weekly_summary()
# Altere start_date e end_date manualmente

start_date = datetime(2026, 4, 14, 0, 0, 0)  # 14/04/2026
end_date = datetime(2026, 4, 18, 23, 59, 59)  # 18/04/2026

# Execute
python main.py --mode manual
```

### Caso 4: Backup do Banco

```powershell
# Copiar arquivo SQLite
Copy-Item ncam_intel.db "backup_$(Get-Date -Format 'yyyyMMdd').db"

# Compactar com data
Compress-Archive -Path ncam_intel.db -DestinationPath "backup_$(Get-Date -Format 'yyyyMMdd').zip"
```

---

## 🛠️ Solução de Problemas Comuns

### ❌ "No module named 'anthropic'"

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Reinstalar dependências
pip install -r requirements.txt
```

### ❌ Discord bot não lê mensagens

**Problema**: Falta de intents

**Solução**:
1. Discord Developer Portal → Sua aplicação → Bot
2. Ative **Message Content Intent**
3. Salve e reinicie o bot

### ❌ WhatsApp retorna 401 Unauthorized

**Problema**: API Key inválida ou instância não conectada

**Solução**:
```powershell
# Testar Evolution API manualmente
Invoke-WebRequest -Uri "http://localhost:8080/instance/connectionState/ncam_instance" -Headers @{"apikey"="SUA_KEY"}

# Se retornar "close", reconecte escaneando QR Code
```

### ❌ E-mail não envia (Gmail)

**Problema**: Senha normal em vez de senha de app

**Solução**:
1. Google Account → Segurança
2. Verificação em 2 etapas (ativar)
3. Senhas de app → Gerar nova
4. Use essa senha no `.env`

### ❌ Claude retorna erro de rate limit

**Problema**: Muitas requisições ou tokens

**Solução**:
```env
# Reduzir max tokens no .env
ANTHROPIC_MAX_TOKENS=2048

# Ou aguardar reset (geralmente 1 minuto)
```

---

## 📊 Exemplo de Resumo Gerado

```markdown
# Resumo Semanal NCam — 21 a 25 de Abril de 2026

## 📌 Visão Executiva

- 12 clientes ativos com comunicação
- 3 instalações realizadas
- 2 problemas técnicos resolvidos
- 1 reclamação pendente (ABC Indústria)

## 📊 Métricas da Semana

- **Total de mensagens**: 145
  - WhatsApp: 78
  - Discord: 67
- **Clientes ativos**: 12
- **Tempo médio de resposta**: ~4 horas

## 🏢 Análise por Cliente

### ABC Indústria

**WhatsApp (8 mensagens)**:
- Reportou falha no sensor CNC linha 2 (21/04)
- Solicitou visita técnica urgente (22/04)
- Confirmou horário: 24/04 às 14h
- Agradeceu atendimento rápido (25/04)

**Discord (equipe interna - 12 mensagens)**:
- Yuri diagnosticou: cabo com mau contato
- Luiz realizou visita em 24/04
- Problema resolvido: cabo substituído
- Mariana atualizou sistema com histórico

**✅ Status e Ações**:
- [X] Visita técnica realizada (24/04 - Luiz)
- [X] Cabo substituído
- [ ] Enviar relatório de manutenção preventiva

**🎯 Prioridade**: Média

---

[... outros 11 clientes ...]

## ⚠️ Alertas e Atenções

- **XYZ Usinagem**: 3 solicitações de suporte em 2 dias - possível problema recorrente
- **LMN Ferramentaria**: Aguardando peça para finalizar instalação

## 📈 Tendências Identificadas

- Aumento de 20% em solicitações de manutenção preventiva
- Problemas com sensores representam 40% das chamadas
- Clientes elogiaram tempo de resposta da equipe

## 📝 Notas Finais

Semana produtiva com alto nível de satisfação dos clientes.
Recomendar treinamento sobre manutenção preventiva de sensores.
```

---

## 🚀 Próximos Passos (Roadmap)

### Versão 1.1 (Planejada)

- [ ] Dashboard web com Streamlit
- [ ] Gráficos de métricas (matplotlib)
- [ ] Notificações push (Telegram)
- [ ] Backup automático do banco
- [ ] Múltiplos destinatários
- [ ] Filtros por cliente/tag

### Versão 2.0 (Futuro)

- [ ] Análise de sentimento com NLP
- [ ] Detecção de urgência automática
- [ ] Integração com Jira/Trello
- [ ] API REST para consultas
- [ ] Mobile app (notificações)
- [ ] Multi-idioma (EN/PT)

---

**Desenvolvido com ❤️ para NCam Monitoramento**
