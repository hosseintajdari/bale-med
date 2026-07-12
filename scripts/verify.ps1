# Windows-friendly verification (same checks as scripts/verify.sh).
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Test-Python3 {
    param([string]$Command)

    & $Command -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 0) else 1)" 2>$null
    return $LASTEXITCODE -eq 0
}

function Get-PythonCommand {
    if ($env:PYTHON) {
        if (Test-Python3 $env:PYTHON) {
            return $env:PYTHON
        }
        throw "error: PYTHON must be a Python 3 interpreter"
    }
    foreach ($candidate in @("python3", "python")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if (-not $cmd) {
            continue
        }
        if (Test-Python3 $candidate) {
            return $candidate
        }
    }
    throw "error: no working Python 3 found in PATH (set PYTHON to a Python 3 interpreter)"
}

$Python = Get-PythonCommand

Write-Host "==> unittest"
& $Python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "==> compileall"
& $Python -m compileall app tests
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "==> ruff"
& $Python -m ruff --version 2>$null
if ($LASTEXITCODE -ne 0) {
    & $Python -m pip install -q -r requirements-dev.txt
}
& $Python -m ruff check app tests
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "==> git diff --check"
git diff --check
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "All verification checks passed."
