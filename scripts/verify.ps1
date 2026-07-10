# Windows-friendly verification (same checks as scripts/verify.sh).
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Get-PythonCommand {
    if ($env:PYTHON) {
        return $env:PYTHON
    }
    foreach ($candidate in @("python", "python3")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if (-not $cmd) {
            continue
        }
        & $candidate -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $candidate
        }
    }
    throw "error: no working python or python3 found in PATH"
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

Write-Host "==> git diff --check"
git diff --check
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "All verification checks passed."
