# Script de Setup Automatizado - NCam Weekly Intel
# Execute: .\setup.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   NCam Weekly Intelligence - Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python não encontrado!" -ForegroundColor Red
    Write-Host "  Instale Python 3.11+ em: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# 2. Criar ambiente virtual
Write-Host "`n[2/6] Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ⚠ Ambiente virtual já existe" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "  ✓ Ambiente virtual criado" -ForegroundColor Green
}

# 3. Ativar ambiente virtual
Write-Host "`n[3/6] Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Ambiente virtual ativado" -ForegroundColor Green

# 4. Instalar dependências
Write-Host "`n[4/6] Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet --disable-pip-version-check
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "  ✗ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}

# 5. Criar arquivo .env
Write-Host "`n[5/6] Configurando ambiente..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ⚠ Arquivo .env já existe" -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Arquivo .env criado" -ForegroundColor Green
    Write-Host "  ⚠ EDITE o arquivo .env com suas credenciais!" -ForegroundColor Yellow
}

# 6. Inicializar banco de dados
Write-Host "`n[6/6] Inicializando banco de dados..." -ForegroundColor Yellow
python main.py --mode init
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Banco de dados inicializado" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Verifique se o .env está configurado" -ForegroundColor Yellow
}

# Conclusão
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ✓ Setup Concluído!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nPróximos passos:" -ForegroundColor White
Write-Host "  1. Edite o arquivo .env com suas credenciais" -ForegroundColor White
Write-Host "  2. Execute: python main.py --mode test" -ForegroundColor White
Write-Host "  3. Teste manual: python main.py --mode manual" -ForegroundColor White
Write-Host "  4. Produção: python main.py --mode scheduled`n" -ForegroundColor White

Write-Host "Documentação completa em QUICKSTART.md`n" -ForegroundColor Cyan
