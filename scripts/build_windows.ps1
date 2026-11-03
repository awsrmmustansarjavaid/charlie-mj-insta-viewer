# Build a portable Windows folder distribution with PyInstaller.
# Run from any working directory; paths are resolved from this script location.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

# Remove stale build outputs so old packages cannot leak into the executable.
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

# Explicit paths and submodule collection make the app package discoverable
# when PyInstaller analyses the entry point on a clean Windows runner.
python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name InstagramResearchSuite `
    --paths $RepoRoot `
    --collect-submodules app `
    --collect-submodules instagram_research_suite `
    --collect-all PySide6 `
    --hidden-import app.data `
    --hidden-import app.data.database `
    main.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

# Keep writable portable data beside the executable.
New-Item -ItemType Directory -Force -Path "dist\InstagramResearchSuite\data" | Out-Null
if (-not (Test-Path "dist\InstagramResearchSuite\InstagramResearchSuite.exe")) {
    throw "Build finished but the expected executable was not created."
}
Write-Host "Build complete: dist\InstagramResearchSuite\InstagramResearchSuite.exe"
