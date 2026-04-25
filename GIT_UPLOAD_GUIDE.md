# 🚀 Guia de Upload para GitHub

## Passo 1: Instalar Git

### Windows (PowerShell como Administrador)

```powershell
# Opção 1: Usando winget (recomendado)
winget install --id Git.Git -e --source winget

# Opção 2: Baixar manualmente
# Acesse: https://git-scm.com/download/win
# E instale o executável
```

Após instalar, **feche e reabra o terminal**.

---

## Passo 2: Configurar Git (Primeira vez apenas)

```powershell
# Configure seu nome
git config --global user.name "Seu Nome"

# Configure seu email (use o mesmo do GitHub)
git config --global user.email "seu-email@example.com"

# Verificar configuração
git config --list
```

---

## Passo 3: Inicializar Repositório Local

No diretório do projeto (`c:\Users\44057824820\Documents\Automacao`):

```powershell
# Inicializar repositório Git
git init

# Adicionar todos os arquivos
git add .

# Verificar status
git status

# Fazer o primeiro commit
git commit -m "Initial commit: NCam Weekly Intelligence - Sistema completo implementado"
```

---

## Passo 4: Conectar ao GitHub

```powershell
# Adicionar remote (substituir pela URL do seu repositório)
git remote add origin https://github.com/Luizmunes13/Automacao.git

# Verificar remote
git remote -v

# Definir branch principal
git branch -M main
```

---

## Passo 5: Fazer Push para GitHub

### Opção A: HTTPS (Requer token de acesso pessoal)

```powershell
# Push inicial
git push -u origin main
```

Quando solicitar credenciais:
- **Username**: Luizmunes13
- **Password**: Use um **Personal Access Token** (não sua senha)

**Como criar um Personal Access Token:**
1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token
4. Selecione permissões: `repo` (full control)
5. Copie o token e use como senha

### Opção B: SSH (Mais seguro, recomendado)

```powershell
# 1. Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@example.com"

# 2. Adicionar ao ssh-agent
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# 3. Copiar chave pública
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard

# 4. Adicionar no GitHub
# GitHub → Settings → SSH and GPG keys → New SSH key
# Cole a chave copiada

# 5. Alterar remote para SSH
git remote set-url origin git@github.com:Luizmunes13/Automacao.git

# 6. Push
git push -u origin main
```

---

## Passo 6: Verificar no GitHub

Acesse: https://github.com/Luizmunes13/Automacao

Você deve ver todos os arquivos do projeto!

---

## 🔄 Comandos Futuros (Para atualizações)

```powershell
# Verificar alterações
git status

# Adicionar alterações
git add .

# Commit
git commit -m "Descrição da mudança"

# Push
git push

# Pull (baixar alterações do GitHub)
git pull
```

---

## 📋 Checklist Antes do Push

- [x] `.gitignore` configurado
- [x] `.env` NÃO está no repositório (apenas `.env.example`)
- [x] Documentação completa (README.md, etc.)
- [x] Código sem erros críticos
- [x] Credenciais sensíveis removidas

---

## 🚨 IMPORTANTE: Proteger Credenciais

**NUNCA commite o arquivo `.env` com credenciais reais!**

Verifique que `.env` está no `.gitignore`:

```powershell
git check-ignore .env
# Deve retornar: .env
```

Se por acaso você commitou `.env` por engano:

```powershell
# Remover do Git (mas manter localmente)
git rm --cached .env

# Commit da remoção
git commit -m "Remove .env from repository"

# Push
git push
```

---

## 📦 Estrutura que será enviada

```
Automacao/
├── src/
│   ├── collectors/
│   ├── processors/
│   ├── delivery/
│   ├── scheduler/
│   ├── utils/
│   ├── database/
│   └── config.py
├── main.py
├── utils.py
├── example_whatsapp_collector.py
├── requirements.txt
├── .env.example          ✅ INCLUÍDO
├── .env                  ❌ IGNORADO
├── .gitignore
├── README.md
├── QUICKSTART.md
├── ARCHITECTURE.md
├── DATAFLOW.md
├── PROJECT_STRUCTURE.md
├── TROUBLESHOOTING.md
├── EXAMPLES.md
├── INDEX.md
├── CHANGELOG.md
└── LICENSE
```

---

## 🎯 Comando Rápido (Tudo em um)

```powershell
# Depois de instalar Git e configurar:
cd "c:\Users\44057824820\Documents\Automacao"
git init
git add .
git commit -m "🎉 Initial commit: NCam Weekly Intelligence - Sistema completo

- WhatsApp Collector (Evolution API) ✅
- Discord Collector (discord.py) ✅
- Claude Processor (Anthropic API) ✅
- Email Delivery (HTML templates) ✅
- Scheduler (APScheduler) ✅
- Documentação completa ✅"
git branch -M main
git remote add origin https://github.com/Luizmunes13/Automacao.git
git push -u origin main
```

---

## 📞 Precisa de Ajuda?

Se encontrar erro "repository already exists":

```powershell
# Forçar push (apenas na primeira vez)
git push -u origin main --force
```

---

**Boa sorte com o upload! 🚀**
