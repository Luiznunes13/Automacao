# Script de Upload para GitHub - NCam Weekly Intelligence
# Execute este script após reiniciar o PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   GitHub Upload - NCam Weekly Intel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Git
Write-Host "1️⃣ Verificando instalação do Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não encontrado! Por favor:" -ForegroundColor Red
    Write-Host "   1. Feche este terminal" -ForegroundColor Red
    Write-Host "   2. Abra um novo PowerShell" -ForegroundColor Red
    Write-Host "   3. Execute este script novamente" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Configurar Git (primeira vez)
Write-Host "2️⃣ Configurando Git..." -ForegroundColor Yellow
$userName = git config --global user.name
if (-not $userName) {
    $name = Read-Host "Digite seu nome completo"
    git config --global user.name "$name"
    Write-Host "✅ Nome configurado: $name" -ForegroundColor Green
} else {
    Write-Host "✅ Nome já configurado: $userName" -ForegroundColor Green
}

$userEmail = git config --global user.email
if (-not $userEmail) {
    $email = Read-Host "Digite seu email (mesmo do GitHub)"
    git config --global user.email "$email"
    Write-Host "✅ Email configurado: $email" -ForegroundColor Green
} else {
    Write-Host "✅ Email já configurado: $userEmail" -ForegroundColor Green
}

Write-Host ""

# 3. Inicializar repositório
Write-Host "3️⃣ Inicializando repositório Git..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "⚠️ Repositório já inicializado" -ForegroundColor Yellow
} else {
    git init
    Write-Host "✅ Repositório inicializado" -ForegroundColor Green
}

Write-Host ""

# 4. Verificar .gitignore
Write-Host "4️⃣ Verificando proteção de credenciais..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $ignored = git check-ignore .env 2>$null
    if ($ignored -eq ".env") {
        Write-Host "✅ Arquivo .env está protegido" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Adicione .env ao .gitignore!" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ .gitignore não encontrado!" -ForegroundColor Red
}

Write-Host ""

# 5. Adicionar arquivos
Write-Host "5️⃣ Adicionando arquivos ao Git..." -ForegroundColor Yellow
git add .
$status = git status --short
Write-Host "✅ Arquivos adicionados:" -ForegroundColor Green
Write-Host $status -ForegroundColor Gray

Write-Host ""

# 6. Primeiro commit
Write-Host "6️⃣ Criando commit..." -ForegroundColor Yellow
$commitMessage = @"
🎉 Initial commit: NCam Weekly Intelligence

Sistema completo de resumo semanal automatizado:

✅ WhatsApp Collector (Evolution API)
✅ Discord Collector (discord.py)
✅ Claude Processor (Anthropic API)
✅ Email Delivery (Templates HTML)
✅ Scheduler (APScheduler)
✅ Documentação completa
✅ Utilitários e exemplos

Stack: Python 3.11+, SQLite, APScheduler
Funcionalidades: Coleta automática seg-sex, processamento com IA, envio por email
"@

git commit -m "$commitMessage"
Write-Host "✅ Commit criado" -ForegroundColor Green

Write-Host ""

# 7. Configurar remote
Write-Host "7️⃣ Conectando ao GitHub..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/Luizmunes13/Automacao.git"

$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "⚠️ Remote já configurado: $existingRemote" -ForegroundColor Yellow
    $response = Read-Host "Deseja atualizar? (s/n)"
    if ($response -eq "s") {
        git remote set-url origin $remoteUrl
        Write-Host "✅ Remote atualizado" -ForegroundColor Green
    }
} else {
    git remote add origin $remoteUrl
    Write-Host "✅ Remote configurado: $remoteUrl" -ForegroundColor Green
}

Write-Host ""

# 8. Configurar branch
Write-Host "8️⃣ Configurando branch principal..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ Branch 'main' configurada" -ForegroundColor Green

Write-Host ""

# 9. Push para GitHub
Write-Host "9️⃣ Fazendo upload para GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️ IMPORTANTE: Quando solicitar credenciais:" -ForegroundColor Yellow
Write-Host "   Username: Luizmunes13" -ForegroundColor Cyan
Write-Host "   Password: Use um Personal Access Token (PAT)" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Como obter PAT:" -ForegroundColor White
Write-Host "   1. GitHub.com → Settings → Developer settings" -ForegroundColor Gray
Write-Host "   2. Personal access tokens → Tokens (classic)" -ForegroundColor Gray
Write-Host "   3. Generate new token" -ForegroundColor Gray
Write-Host "   4. Selecione: repo (full control)" -ForegroundColor Gray
Write-Host "   5. Copie o token e use como senha" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Pressione ENTER para continuar com o push (ou 'n' para cancelar)"
if ($response -ne "n") {
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   ✅ UPLOAD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Acesse: https://github.com/Luizmunes13/Automacao" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Erro no push. Possíveis soluções:" -ForegroundColor Red
        Write-Host "   1. Verifique suas credenciais" -ForegroundColor Yellow
        Write-Host "   2. Use um Personal Access Token como senha" -ForegroundColor Yellow
        Write-Host "   3. Se o repo já existe, tente: git push -f origin main" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "❌ Push cancelado pelo usuário" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Comandos futuros para atualizar:" -ForegroundColor Cyan
Write-Host "  git add ." -ForegroundColor Gray
Write-Host "  git commit -m 'Descrição da mudança'" -ForegroundColor Gray
Write-Host "  git push" -ForegroundColor Gray
Write-Host ""
