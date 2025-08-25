# Pre-commit hook for WOMM project (PowerShell version)
# Runs code quality checks before allowing commits

param(
    [string]$CommitHash = ""
)

# Get project root (parent of .hooks directory)
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

Write-Host "🔍 Running pre-commit checks..." -ForegroundColor Cyan
Write-Host "📁 Project root: $ProjectRoot" -ForegroundColor Gray

# Check if lint.py exists
$lintPath = Join-Path $ProjectRoot "lint.py"
Write-Host "🔍 Looking for lint.py at: $lintPath" -ForegroundColor Gray
if (-not (Test-Path $lintPath)) {
    Write-Host "❌ Error: lint.py not found in project root" -ForegroundColor Red
    Write-Host "   Expected path: $lintPath" -ForegroundColor Red
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    python --version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Python not found in PATH" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Run linting checks with check-only mode
Write-Host "🔧 Running code quality checks..." -ForegroundColor Cyan
try {
    python lint.py --check-only
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Pre-commit checks passed!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Pre-commit checks failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 To fix issues automatically, run:" -ForegroundColor Yellow
        Write-Host "   python lint.py --fix" -ForegroundColor Gray
        Write-Host ""
        Write-Host "💡 To see detailed output, run:" -ForegroundColor Yellow
        Write-Host "   python lint.py --check-only --verbose" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "❌ Error running lint.py: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
